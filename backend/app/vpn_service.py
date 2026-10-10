from __future__ import annotations

import csv
import io
import os
import re
import shlex
import socket
import subprocess
import sys
import tempfile
import threading
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import paramiko
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from sqlmodel import select

from .database import get_session
from .models.portal import DiagnosticExportTable, VpnExportTask, VpnSite
BACKEND_ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = BACKEND_ROOT / "uploads" / "vpn_exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

_export_runtime_lock = threading.Lock()
_export_runtime: Dict[int, Dict[str, object]] = {}


def _runtime_for_task(task_id: int) -> Dict[str, object]:
    with _export_runtime_lock:
        runtime = _export_runtime.get(task_id)
        if runtime is None:
            runtime = {"cancel": threading.Event(), "client": None, "pid": None}
            _export_runtime[task_id] = runtime
        return runtime


def request_export_cancel(task_id: int) -> None:
    runtime = _runtime_for_task(task_id)
    cancel_event = runtime["cancel"]
    cancel_event.set()
    client = runtime.get("client")
    pid = runtime.get("pid")
    if client is not None and pid:
        remote_dir = f"/tmp/jd-vpn-export-{task_id}"
        command = (
            f"kill -TERM {int(pid)} 2>/dev/null || true; "
            f"pkill -TERM -P {int(pid)} 2>/dev/null || true; "
            f"rm -rf {shlex.quote(remote_dir)}"
        )
        try:
            client.exec_command(command, timeout=5)
        except Exception:
            pass


def _update_export_task(
    task_id: int,
    *,
    progress: Optional[int] = None,
    log: Optional[str] = None,
    append_log: bool = True,
    status: Optional[str] = None,
    error_message: Optional[str] = None,
    file_name: Optional[str] = None,
    file_path: Optional[str] = None,
) -> Optional[str]:
    with get_session() as session:
        task = session.get(VpnExportTask, task_id)
        if task is None:
            return None
        if task.status != "processing":
            return task.status
        if progress is not None:
            task.progress = max(0, min(100, progress))
        if log is not None:
            task.current_log = (
                f"{task.current_log}\n{log}" if append_log and task.current_log else log
            )[-12000:]
        if status is not None:
            task.status = status
            task.completed_at = datetime.utcnow()
        if error_message is not None:
            task.error_message = error_message[:1000]
        if file_name is not None:
            task.file_name = file_name
        if file_path is not None:
            task.file_path = file_path
        session.add(task)
        session.commit()
        return task.status


class VpnConfigurationError(RuntimeError):
    pass


KEYCHAIN_SERVICES = {
    "VPN_JUMP_PASSWORD": "jd-energy-vpn-jump",
    "VPN_SITE_PASSWORD": "jd-energy-vpn-site",
    "TDENGINE_PASSWORD": "jd-energy-tdengine",
}

SETTING_DEFAULTS = {
    "VPN_JUMP_HOST": "8.216.40.206",
    "VPN_JUMP_USERNAME": "root",
    "VPN_SITE_USERNAME": "root",
    "TDENGINE_USERNAME": "root",
}


def keychain_password(service_name: str) -> str:
    if sys.platform != "darwin":
        return ""
    try:
        result = subprocess.run(
            ["/usr/bin/security", "find-generic-password", "-a", "root", "-s", service_name, "-w"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def required_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value and name in SETTING_DEFAULTS:
        value = SETTING_DEFAULTS[name]
    if not value and name in KEYCHAIN_SERVICES:
        value = keychain_password(KEYCHAIN_SERVICES[name])
    if not value:
        raise VpnConfigurationError(f"Server setting {name} is not configured in the environment or Keychain")
    return value


def ssh_settings(include_tdengine: bool = True) -> Dict[str, object]:
    settings: Dict[str, object] = {
        "jump_host": required_setting("VPN_JUMP_HOST"),
        "jump_port": int(os.getenv("VPN_JUMP_PORT", "22")),
        "jump_username": required_setting("VPN_JUMP_USERNAME"),
        "jump_password": os.getenv("VPN_JUMP_PASSWORD", "") or keychain_password(KEYCHAIN_SERVICES["VPN_JUMP_PASSWORD"]),
        "site_port": int(os.getenv("VPN_SITE_PORT", "22")),
        "site_username": required_setting("VPN_SITE_USERNAME"),
        "site_password": os.getenv("VPN_SITE_PASSWORD", "") or keychain_password(KEYCHAIN_SERVICES["VPN_SITE_PASSWORD"]),
        "strict_host_key": os.getenv("VPN_SSH_STRICT_HOST_KEY", "true").lower() not in {"0", "false", "no"},
        "known_hosts": os.getenv("VPN_SSH_KNOWN_HOSTS", "").strip(),
    }
    if include_tdengine:
        settings["tdengine_username"] = required_setting("TDENGINE_USERNAME")
        settings["tdengine_password"] = required_setting("TDENGINE_PASSWORD")
    return settings


def new_ssh_client(settings: Dict[str, object]) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    known_hosts = str(settings["known_hosts"])
    if known_hosts:
        client.load_host_keys(known_hosts)
    else:
        client.load_system_host_keys()
    if bool(settings["strict_host_key"]):
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
    else:
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return client


def connect_jump_host() -> Tuple[paramiko.SSHClient, Dict[str, object]]:
    settings = ssh_settings(include_tdengine=False)
    if not settings["jump_password"]:
        settings["jump_password"] = required_setting("VPN_JUMP_PASSWORD")
    client = new_ssh_client(settings)
    try:
        client.connect(
            hostname=str(settings["jump_host"]),
            port=int(settings["jump_port"]),
            username=str(settings["jump_username"]),
            password=str(settings["jump_password"]),
            timeout=15,
            banner_timeout=15,
            auth_timeout=15,
            look_for_keys=False,
            allow_agent=False,
        )
    except Exception:
        client.close()
        raise
    return client, settings


def connect_site(site: VpnSite) -> Tuple[Optional[paramiko.SSHClient], paramiko.SSHClient]:
    settings = ssh_settings(include_tdengine=False)
    port = int(site.port or settings["site_port"])
    username = site.username or str(settings["site_username"])
    password = site.password or str(settings["site_password"])
    if not password:
        password = required_setting("VPN_SITE_PASSWORD")

    jump_client: Optional[paramiko.SSHClient] = None
    channel = None
    via_jump = bool(site.use_jump_host and site.jump_host_ip)
    if via_jump:
        jump_password = site.jump_host_password or str(settings["jump_password"])
        if not jump_password:
            jump_password = required_setting("VPN_JUMP_PASSWORD")
        jump_client = new_ssh_client(settings)
        try:
            jump_client.connect(
                hostname=site.jump_host_ip,
                port=int(site.jump_host_port or settings["jump_port"]),
                username=site.jump_host_user or str(settings["jump_username"]),
                password=jump_password,
                timeout=15,
                banner_timeout=15,
                auth_timeout=15,
                look_for_keys=False,
                allow_agent=False,
            )
            transport = jump_client.get_transport()
            if transport is None or not transport.is_active():
                raise RuntimeError("跳板机 SSH 通道不可用")
            channel = transport.open_channel(
                "direct-tcpip",
                (site.vpn_ip, port),
                (site.jump_host_ip, 0),
            )
        except Exception as exc:
            jump_client.close()
            raise RuntimeError(
                f"[连接失败] 无法连接跳板机 {site.jump_host_ip}:{site.jump_host_port or 22}：{exc}"
            ) from exc

    site_client = new_ssh_client(settings)
    try:
        site_client.connect(
            hostname=site.vpn_ip,
            port=port,
            username=username,
            password=password,
            sock=channel,
            timeout=15,
            banner_timeout=15,
            auth_timeout=15,
            look_for_keys=False,
            allow_agent=False,
        )
    except Exception as exc:
        if channel is not None:
            channel.close()
        if jump_client is not None:
            jump_client.close()
        path_hint = "请确认目标 SSH 服务及跳板机转发配置" if via_jump else "请确认服务器底层 VPN 隧道已启动且目标 IP 可直连"
        raise RuntimeError(
            f"[连接失败] 无法连接现场目标 {site.vpn_ip}:{port}，{path_hint}。详情：{exc}"
        ) from exc
    return jump_client, site_client


def sql_for_table(table: DiagnosticExportTable, eblock_id: int, start_time: datetime, end_time: datetime) -> str:
    start = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end = end_time.strftime("%Y-%m-%d %H:%M:%S")
    conditions = []
    if table.extra_where:
        conditions.append(table.extra_where)
    if table.has_eblock_id:
        conditions.append(f"eBlock_id = {int(eblock_id)}")
    conditions.extend((f"time >= '{start}'", f"time <= '{end}'"))
    return f"SELECT * FROM {table.table_name} WHERE {' AND '.join(conditions)};"


def build_export_command(
    tables: Iterable[DiagnosticExportTable],
    eblock_id: int,
    start_time: datetime,
    end_time: datetime,
    remote_dir: str,
    tdengine_username: str,
    tdengine_password: str,
) -> Tuple[str, Dict[str, str]]:
    remote_files: Dict[str, str] = {}
    commands = [f"mkdir -p {shlex.quote(remote_dir)}"]
    for table in tables:
        sql = sql_for_table(table, eblock_id, start_time, end_time)
        remote_path = f"{remote_dir}/{table.sheet_name}.csv"
        remote_files[table.sheet_name] = remote_path
        taos_command = " ".join(
            [
                "taos",
                f"-u{shlex.quote(tdengine_username)}",
                f"-p{shlex.quote(tdengine_password)}",
                "-s",
                shlex.quote(sql),
                ">",
                shlex.quote(remote_path),
            ]
        )
        commands.append(taos_command)
    return "set -e; " + " && ".join(commands), remote_files


def normalize_csv_rows(raw: str) -> List[List[str]]:
    text = raw.lstrip("\ufeff").strip()
    if not text:
        return []
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",\t|")
        return list(csv.reader(io.StringIO(text), dialect))
    except csv.Error:
        return [[part.strip() for part in line.split()] for line in text.splitlines() if line.strip()]


def safe_export_name(site_name: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", site_name.strip()).strip(".-")
    return normalized[:80] or "vpn-site"


def excel_safe_value(value: str) -> str:
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value


def build_workbook(csv_files: Dict[str, Path], destination: Path) -> None:
    workbook = Workbook()
    workbook.remove(workbook.active)
    header_fill = PatternFill("solid", fgColor="E2E8F0")
    for table, csv_path in csv_files.items():
        sheet = workbook.create_sheet(title=table)
        raw = csv_path.read_text(encoding="utf-8", errors="replace")
        rows = normalize_csv_rows(raw)
        if not rows:
            rows = [["No data"]]
        for row_index, row in enumerate(rows, start=1):
            sheet.append([excel_safe_value(value) for value in row])
            if row_index == 1:
                for cell in sheet[row_index]:
                    cell.font = Font(bold=True)
                    cell.fill = header_fill
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
    workbook.save(destination)


def run_export_task(task_id: int) -> None:
    jump_client: Optional[paramiko.SSHClient] = None
    site_client: Optional[paramiko.SSHClient] = None
    remote_dir = f"/tmp/jd-vpn-export-{task_id}"
    runtime = _runtime_for_task(task_id)
    cancel_event = runtime["cancel"]
    try:
        with get_session() as session:
            task = session.get(VpnExportTask, task_id)
            if task is None:
                return
            if task.status != "processing":
                return
            site = session.get(VpnSite, task.site_id)
            if site is None:
                raise RuntimeError("VPN site no longer exists")
            task_data = task.model_dump()
            site_data = site.model_dump()
            configured_tables = session.exec(
                select(DiagnosticExportTable).where(
                    DiagnosticExportTable.table_name.in_(task.selected_tables)
                )
            ).all()

        configured_by_name = {item.table_name: item for item in configured_tables}
        export_tables = [configured_by_name[name] for name in task_data["selected_tables"] if name in configured_by_name]
        if len(export_tables) != len(task_data["selected_tables"]):
            raise RuntimeError("One or more diagnostic table configurations no longer exist")

        task = VpnExportTask(**task_data)
        site = VpnSite(**site_data)
        settings = ssh_settings()
        _update_export_task(task_id, progress=2, log="正在连接现场目标机器…", append_log=False)
        jump_client, site_client = connect_site(site)
        runtime["client"] = site_client
        if cancel_event.is_set():
            raise InterruptedError("任务已取消")

        remote_files: Dict[str, str] = {}
        site_client.exec_command(f"mkdir -p {shlex.quote(remote_dir)}", timeout=15)
        total_tables = len(export_tables)
        for index, table in enumerate(export_tables, start=1):
            if cancel_event.is_set():
                raise InterruptedError("任务已取消")
            remote_path = f"{remote_dir}/{table.sheet_name}.csv"
            error_path = f"{remote_path}.err"
            remote_files[table.sheet_name] = remote_path
            sql = sql_for_table(table, task.eblock_id, task.start_time, task.end_time)
            taos_command = " ".join(
                [
                    "exec taos",
                    f"-u{shlex.quote(str(settings['tdengine_username']))}",
                    f"-p{shlex.quote(str(settings['tdengine_password']))}",
                    "-s",
                    shlex.quote(sql),
                    ">",
                    shlex.quote(remote_path),
                    "2>",
                    shlex.quote(error_path),
                ]
            )
            launch_command = (
                f"nohup sh -c {shlex.quote(taos_command)} "
                f">/dev/null 2>&1 </dev/null & echo $!"
            )
            _update_export_task(
                task_id,
                progress=5 + int((index - 1) * 75 / total_tables),
                log=f"[{index}/{total_tables}] 正在导出 {table.table_name}…",
            )
            _, pid_stdout, _ = site_client.exec_command(launch_command, timeout=15)
            pid_text = pid_stdout.read().decode("utf-8", errors="replace").strip()
            if not pid_text.isdigit():
                raise RuntimeError(f"无法启动 {table.table_name} 导出进程")
            process_id = int(pid_text)
            runtime["pid"] = process_id
            while True:
                if cancel_event.is_set():
                    request_export_cancel(task_id)
                    raise InterruptedError("任务已取消")
                _, check_stdout, _ = site_client.exec_command(
                    f"kill -0 {process_id} 2>/dev/null", timeout=10
                )
                process_running = check_stdout.channel.recv_exit_status() == 0
                if not process_running:
                    break
                cancel_event.wait(0.5)
            runtime["pid"] = None
            _, result_stdout, _ = site_client.exec_command(
                f"if test -s {shlex.quote(error_path)}; then cat {shlex.quote(error_path)}; exit 1; fi; "
                f"test -f {shlex.quote(remote_path)}",
                timeout=15,
            )
            result_output = result_stdout.read().decode("utf-8", errors="replace").strip()
            if result_stdout.channel.recv_exit_status() != 0:
                raise RuntimeError(result_output or f"{table.table_name} 导出失败")
            completed_progress = 5 + int(index * 75 / total_tables)
            _update_export_task(
                task_id,
                progress=completed_progress,
                log=f"[{index}/{total_tables}] {table.table_name} 导出完成，进度 {completed_progress}%",
            )

        stamp = task.created_at.strftime("%Y%m%d-%H%M%S")
        safe_site_name = safe_export_name(task.site_name)
        archive_name = f"{safe_site_name}-{stamp}.zip"
        archive_path = EXPORT_DIR / archive_name
        _update_export_task(task_id, progress=82, log="正在下载 CSV 并生成 Excel…")
        with tempfile.TemporaryDirectory(prefix=f"vpn-export-{task_id}-") as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            local_csv_files: Dict[str, Path] = {}
            sftp = site_client.open_sftp()
            try:
                for index, (table, remote_path) in enumerate(remote_files.items(), start=1):
                    if cancel_event.is_set():
                        raise InterruptedError("任务已取消")
                    local_path = temp_dir / f"{table}.csv"
                    sftp.get(remote_path, str(local_path))
                    local_csv_files[table] = local_path
                    _update_export_task(
                        task_id,
                        progress=82 + int(index * 10 / max(1, len(remote_files))),
                        log=f"已下载 {table} ({index}/{len(remote_files)})",
                    )
            finally:
                sftp.close()
            if cancel_event.is_set():
                raise InterruptedError("任务已取消")
            workbook_path = temp_dir / f"{safe_site_name}-{stamp}.xlsx"
            build_workbook(local_csv_files, workbook_path)
            with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for table, local_path in local_csv_files.items():
                    archive.write(local_path, arcname=f"csv/{table}.csv")
                archive.write(workbook_path, arcname=workbook_path.name)

        site_client.exec_command(f"rm -rf {shlex.quote(remote_dir)}")
        if cancel_event.is_set():
            archive_path.unlink(missing_ok=True)
            raise InterruptedError("任务已取消")
        final_status = _update_export_task(
            task_id,
            status="completed",
            progress=100,
            log="导出完成，可下载文件。",
            file_name=archive_name,
            file_path=str(archive_path),
        )
        if final_status == "canceled":
            archive_path.unlink(missing_ok=True)
    except InterruptedError:
        if site_client is not None:
            try:
                site_client.exec_command(f"rm -rf {shlex.quote(remote_dir)}", timeout=5)
            except Exception:
                pass
        _update_export_task(task_id, log="任务已取消，临时文件已清理。", status="canceled")
    except Exception as exc:
        if site_client is not None:
            try:
                site_client.exec_command(f"rm -rf {shlex.quote(remote_dir)}", timeout=5)
            except Exception:
                pass
        current_status = _update_export_task(
            task_id,
            status="failed",
            progress=0,
            log=f"导出失败：{exc}",
            error_message=str(exc),
        )
        if current_status == "canceled":
            _update_export_task(task_id, log="任务已取消，临时文件已清理。")
    finally:
        if site_client is not None:
            site_client.close()
        if jump_client is not None:
            jump_client.close()
        runtime["client"] = None
        runtime["pid"] = None
        with _export_runtime_lock:
            if _export_runtime.get(task_id) is runtime:
                _export_runtime.pop(task_id, None)


def open_terminal_channel(site: Optional[VpnSite], cols: int = 120, rows: int = 32):
    if site is None:
        jump_client, _ = connect_jump_host()
        channel = jump_client.invoke_shell(term="xterm-256color", width=cols, height=rows)
        channel.settimeout(0.2)
        return jump_client, None, channel
    jump_client, site_client = connect_site(site)
    channel = site_client.invoke_shell(term="xterm-256color", width=cols, height=rows)
    channel.settimeout(0.2)
    return jump_client, site_client, channel


def receive_channel(channel: paramiko.Channel) -> bytes:
    try:
        return channel.recv(32768)
    except socket.timeout:
        return b""
