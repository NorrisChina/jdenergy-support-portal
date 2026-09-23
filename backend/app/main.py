from __future__ import annotations

import os
import asyncio
import json
import uuid
import mimetypes
import base64
import csv
import re
import hashlib
import hmac
import io
import logging
import ipaddress
import secrets
import threading
import time
from datetime import timedelta
from datetime import date, datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi import APIRouter, BackgroundTasks, Body, Depends, FastAPI, File, Form, Header, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import or_
from sqlmodel import select

from .database import get_session, init_db
from .models.after_sales import FaultCode as AfterSalesFaultCode
from .models.ledger import (
    CI_DELIVERY_SEED,
    FAULT_CODE_SEED,
    GRID_SCALE_PROJECT_SEED,
    WAREHOUSE_INVENTORY_SEED,
    WAREHOUSE_TRANSACTION_SEED,
    CiDealerDelivery,
    CIDeliveryBatch,
    FaultCode,
    GridScaleProject,
    WarehouseInventory,
    WarehouseInventoryItem,
    WarehouseTransaction,
    WAREHOUSE_INVENTORY_ITEM_SEED,
)
from .models.technical_docs import (
    TECHNICAL_DOCS_SEED,
    TECHNICAL_DOC_CATEGORIES,
    TECHNICAL_DOC_PRODUCT_SERIES,
    TechnicalDoc,
)
from .models.portal import AfterSalesLog, CustomerTicket, DiagnosticExportTable, EmpowermentRecord, EmpowermentSkill, FaultComponent, LogisticsShipment, LogisticsStatus, ProjectMilestone, User, VpnExportTask, VpnSite
from .vpn_service import EXPORT_DIR, open_terminal_channel, receive_channel, run_export_task


logger = logging.getLogger(__name__)

SUPER_ADMIN_USERNAME = "admin"
SUPER_ADMIN_PASSWORD = "111"
VIEWER_USERNAME = "JDE"
VIEWER_PASSWORD = "123"
SYSTEM_COMPANY = "JD Energy"


FAULTY_COMPONENT_OPTIONS = (
    "门锁", "通讯线束", "电表", "熔断器", "断路器", "bmu", "pcs", "液冷机",
    "HIM板", "急停", "io模块", "开关电源", "交换机", "风扇", "pack", "网络控制器", "空调", "其他",
)

FAULT_COMPONENT_SEED = [
    FaultComponent(name=name, sort_order=index)
    for index, name in enumerate(FAULTY_COMPONENT_OPTIONS, start=1)
]

LOGISTICS_STATUS_SEED = [
    LogisticsStatus(name=name, name_en=name_en, step_order=index)
    for index, (name, name_en) in enumerate(
        (
            ("工厂备货", "Factory Preparation"),
            ("集港装船", "Port Consolidation"),
            ("海上运输中", "In Ocean Transit"),
            ("清关中", "Customs Clearance"),
            ("陆运中", "Inland Transit"),
            ("已送达现场", "Delivered On Site"),
        ),
        start=1,
    )
]

EMPOWERMENT_SKILL_SEED = [
    EmpowermentSkill(name=name, name_en=name_en, sort_order=index)
    for index, (name, name_en) in enumerate(
        (("PCS更换", "PCS Replacement"), ("水机更换", "Cooling Unit Replacement"), ("问题定位", "Issue Diagnosis")),
        start=1,
    )
]

DIAGNOSTIC_EXPORT_TABLE_SEED = [
    DiagnosticExportTable(table_name="eblock.bms_rs", sheet_name="bms_rs", sort_order=10),
    DiagnosticExportTable(table_name="eblock.bms_tm", sheet_name="bms_tm", sort_order=20),
    DiagnosticExportTable(table_name="eblock.bms_tc", sheet_name="bms_tc", sort_order=30),
    DiagnosticExportTable(table_name="eblock.pcs_tc", sheet_name="pcs_tc", extra_where="pcs_id = 1", sort_order=40),
    DiagnosticExportTable(table_name="eblock.pcs_tm", sheet_name="pcs_tm", extra_where="pcs_id = 1", sort_order=50),
    DiagnosticExportTable(table_name="eblock.pcs_rs", sheet_name="pcs_rs", extra_where="pcs_id = 1", sort_order=60),
    DiagnosticExportTable(table_name="eblock.elink_yk", sheet_name="elink_yk", has_eblock_id=False, sort_order=70),
    DiagnosticExportTable(table_name="eblock.elink_yt", sheet_name="elink_yt", has_eblock_id=False, sort_order=80),
    DiagnosticExportTable(table_name="eblock.elink_yx", sheet_name="elink_yx", has_eblock_id=False, sort_order=90),
    DiagnosticExportTable(table_name="eblock.elink_yc", sheet_name="elink_yc", has_eblock_id=False, sort_order=100),
]

LOGISTICS_SHIPMENT_SEED = [
    LogisticsShipment(
        tracking_no="MSCU7712345",
        customer_company="Munich Energy Partners",
        related_project="418 项目",
        destination_country="Germany",
        destination_port="Hamburg",
        container_no="MSKU-889021",
        equipment_model="eBlock-418",
        equipment_qty=12,
        status="海上运输中",
        eta=date(2026, 9, 20),
        carrier="Maersk",
        tracking_url="https://www.maersk.com/tracking/MSCU7712345",
    ),
    LogisticsShipment(
        tracking_no="COSU8801122",
        customer_company="Rotterdam Solar Hub",
        related_project="Rotterdam Solar Hub",
        destination_country="Netherlands",
        destination_port="Rotterdam",
        container_no="CSNU-441098",
        equipment_model="eBlock-250",
        equipment_qty=6,
        status="清关中",
        eta=date(2026, 9, 5),
        carrier="COSCO",
        tracking_url="https://elines.coscoshipping.com/COSU8801122",
    ),
    LogisticsShipment(
        tracking_no="ONEY9903344",
        customer_company="Warsaw Green Power",
        related_project="Warsaw Green Power",
        destination_country="Poland",
        destination_port="Koper",
        container_no="ONEU-772311",
        equipment_model="eBlock-100C",
        equipment_qty=8,
        status="已送达现场",
        eta=date(2026, 8, 10),
        ata=date(2026, 8, 9),
        carrier="ONE",
        tracking_url="https://ecomm.one-line.com/ONEY9903344",
    ),
]

EMPOWERMENT_RECORD_SEED = [
    EmpowermentRecord(partner_name="意大利 Afore", delivery_250_net=80, delivery_250_soft=80, delivery_100c_net=60, delivery_100c_soft=60, delivery_418_net=30, delivery_418_soft=30, aftersales_scores={"PCS更换": 65, "水机更换": 65, "问题定位": 70}, remarks="中国人手把手带训，有团队支持"),
    EmpowermentRecord(partner_name="德国 Tripme", delivery_250_net=95, delivery_250_soft=95, delivery_100c_net=90, delivery_100c_soft=90, delivery_418_net=70, delivery_418_soft=70, aftersales_scores={"PCS更换": 80, "水机更换": 80, "问题定位": 85}, remarks="有独立试验设备"),
    EmpowermentRecord(partner_name="荷兰 Sietec", delivery_250_net=60, delivery_250_soft=60, delivery_100c_net=55, delivery_100c_soft=55, delivery_418_net=20, delivery_418_soft=20, aftersales_scores={"PCS更换": 45, "水机更换": 45, "问题定位": 50}, remarks="需加强备件更换培训"),
]


class FaultCodeRecord(BaseModel):
    fault_code: str
    fault_name: str
    possible_causes: str
    solution: str


class FaultCodeUpsert(BaseModel):
    fault_name: str
    possible_causes: str
    solution: str


class AfterSalesFaultCodeItem(BaseModel):
    module: str
    fault_code: str
    fault_name: str = ""
    fault_level: str = ""
    is_stop: str = ""
    recovery: str = ""
    detection_condition: str = ""
    trigger_logic: str = ""
    possible_cause: str = ""
    solution: str = ""


class AfterSalesFaultCodeImportPayload(BaseModel):
    items: List[AfterSalesFaultCodeItem]


class AfterSalesFaultCodeCreate(BaseModel):
    module: str
    fault_code: str
    fault_name: str = ""
    fault_level: str = ""
    is_stop: str = ""
    recovery: str = ""
    detection_condition: str = ""
    trigger_logic: str = ""
    possible_cause: str = ""
    solution: str = ""


class AfterSalesFaultCodeUpdate(BaseModel):
    module: Optional[str] = None
    fault_code: Optional[str] = None
    fault_name: Optional[str] = None
    fault_level: Optional[str] = None
    is_stop: Optional[str] = None
    recovery: Optional[str] = None
    detection_condition: Optional[str] = None
    trigger_logic: Optional[str] = None
    possible_cause: Optional[str] = None
    solution: Optional[str] = None


class GridScaleStatusUpdate(BaseModel):
    progress_status: str


class GridScaleProjectUpsert(BaseModel):
    project_name: str
    cod: str
    capacity_mwh: float
    software_version: str = ""
    progress_status: str
    photo_paths: List[str]
    partner_name: str = ""
    customer_company: str = ""


class CiDeliveryUpdate(BaseModel):
    region: str
    delivered_100c: int = 0
    delivered_250: int = 0
    customer_company: Optional[str] = None


class CiDeliveryCreateUpdate(CiDeliveryUpdate):
    dealer_name: str


class CIDeliveryBatchPayload(BaseModel):
    product_type: Literal["100C", "250"]
    quantity: int = Field(default=1, gt=0)
    delivery_date: str
    serial_numbers: Optional[str] = ""


class WarehouseTransactionCreate(BaseModel):
    warehouse_name: str
    tx_type: Literal["国内到货入库", "现场客诉领用出库"]
    product_model: str
    quantity: int
    related_project: str
    tx_no: str


class WarehouseTransactionUpdate(WarehouseTransactionCreate):
    pass


class WarehouseInventoryItemCreate(BaseModel):
    item_no: str
    description_zh: str
    specification: str
    total_quantity: int = 0
    damaged_quantity: int = 0
    available_quantity: Optional[int] = None
    photo_paths: List[str] = Field(default_factory=list)
    remarks: Optional[str] = None


class WarehouseInventoryItemUpdate(BaseModel):
    description_zh: str
    specification: str
    total_quantity: int = 0
    damaged_quantity: int = 0
    available_quantity: Optional[int] = None
    photo_paths: List[str] = Field(default_factory=list)
    remarks: Optional[str] = None


class TechnicalDocUpdate(BaseModel):
    product_series: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None


class LoginPayload(BaseModel):
    username: str
    password: str


class CustomerUserPayload(BaseModel):
    username: str
    password: str
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    country: Optional[str] = None
    project_ids: List[str] = Field(default_factory=list)


class CustomerUserUpdatePayload(BaseModel):
    password: Optional[str] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    country: Optional[str] = None
    project_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MilestonePayload(BaseModel):
    actual_date: Optional[date] = None


class AfterSalesLogPayload(BaseModel):
    event_date: date
    country: str
    customer: str
    customer_company: Optional[str] = None
    project_name: str
    product_model: Literal["418", "250", "100C"]
    support_type: Literal["远程 (Remote)", "现场 (On-site)"]
    issue_category: Literal["软件 (Software)", "硬件 (Hardware)"]
    fault_component: Optional[str] = None
    faulty_component: Optional[str] = None
    fault_description: str = ""
    onsite_solution: str = ""
    serial_number: Optional[str] = ""
    rd_contact: Optional[str] = ""
    status: Literal["已解决 (Resolved)", "处理中 (Pending)"] = "处理中 (Pending)"
    pending_reason: str = ""
    created_by: str
    attachments: List[str] = Field(default_factory=list)


class TicketPayload(BaseModel):
    project_name: str
    customer_company: Optional[str] = None
    serial_number: str
    product_model: Literal["418", "250", "100C"]
    ticket_type: Literal["产品需求 (Feature Request)", "故障报修/Bug (Issue Report)"]
    suspected_scope: Literal["软件", "硬件"]
    suspected_component: str
    description: str
    attachments: List[str] = Field(default_factory=list)
    expected_resolution_date: Optional[date] = None
    expected_date: Optional[date] = None
    contact: str


class TicketUpdatePayload(BaseModel):
    status: Literal["待处理 (Pending)", "处理中 (In Progress)", "已回复/已解决 (Resolved)", "已关闭 (Closed)"]
    staff_reply: str = ""
    resolved_at: Optional[datetime] = None
    expected_date: Optional[date] = None


LOGISTICS_STATUS_OPTIONS = ("工厂备货", "集港装船", "海上运输中", "清关中", "陆运中", "已送达现场")


class LogisticsShipmentPayload(BaseModel):
    created_date: date = Field(default_factory=date.today)
    stage: Literal["delivery", "after_sales"] = "delivery"
    customer_company: str = ""
    related_project: str = ""
    destination_country: str = ""
    equipment_model: str = ""
    specific_module: str = ""
    equipment_qty: int = 0
    status: str = "工厂备货"
    eta: Optional[date] = None
    tracking_url: str = ""
    remarks: str = ""


class EmpowermentRecordPayload(BaseModel):
    partner_name: str
    delivery_418_net: int = Field(default=0, ge=0, le=100)
    delivery_418_soft: int = Field(default=0, ge=0, le=100)
    delivery_250_net: int = Field(default=0, ge=0, le=100)
    delivery_250_soft: int = Field(default=0, ge=0, le=100)
    delivery_100c_net: int = Field(default=0, ge=0, le=100)
    delivery_100c_soft: int = Field(default=0, ge=0, le=100)
    aftersales_scores: Dict[str, int] = Field(default_factory=dict)
    remarks: str = ""


class FaultComponentPayload(BaseModel):
    name: str
    name_en: str = ""
    sort_order: int = 0
    is_active: bool = True


class LogisticsStatusPayload(BaseModel):
    name: str
    name_en: str = ""
    step_order: int = 0
    is_active: bool = True


class EmpowermentSkillPayload(BaseModel):
    name: str
    name_en: str = ""
    sort_order: int = 0
    is_active: bool = True


class VpnSitePayload(BaseModel):
    name: str
    vpn_ip: str
    customer_company: str = ""


class VpnExportPayload(BaseModel):
    site_id: int
    eblock_id: int = Field(default=1, ge=1)
    start_time: datetime
    end_time: datetime
    tables: List[str] = Field(default_factory=list)


class DiagnosticExportTablePayload(BaseModel):
    table_name: str
    sheet_name: str
    has_eblock_id: bool = True
    extra_where: str = ""
    sort_order: int = 0
    is_enabled: bool = True


class VpnTerminalTicketPayload(BaseModel):
    site_id: Optional[int] = None


app = FastAPI(
    title="JD Energy Service Portal API",
    version="2.0.0",
    description="Fault lookup, project ledger, C&I deliveries, and warehouse inventory APIs.",
)

BACKEND_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_ROOT / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
DOCS_UPLOAD_DIR = UPLOAD_DIR / "docs"
os.makedirs(DOCS_UPLOAD_DIR, exist_ok=True)

TERMINAL_TICKET_TTL_SECONDS = 30
TERMINAL_IDLE_TIMEOUT_SECONDS = 900
MAX_EXPORT_RANGE = timedelta(days=31)
terminal_tickets: Dict[str, Dict[str, object]] = {}
terminal_ticket_lock = threading.Lock()

app.mount("/static_uploads", StaticFiles(directory=UPLOAD_DIR), name="static_uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


warehouse_inventory_router = APIRouter(
    prefix="/api/warehouse/inventory",
    tags=["Warehouse Inventory"],
)

grid_scale_router = APIRouter(
    prefix="/api/ledger/grid-scale",
    tags=["Grid-Scale Ledger"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    ensure_default_admin()
    ensure_fault_components()
    ensure_logistics_statuses()
    ensure_empowerment_skills()
    ensure_diagnostic_export_tables()
    seed_mode = os.getenv("SEED_MODE", "all").strip().lower()
    if seed_mode == "all":
        seed_database()
    elif seed_mode in {"none", "after-sales-only", "after_sales_only"}:
        # Skip legacy full-module seed when deploying with selective data initialization.
        pass
    else:
        seed_database()


def seed_database() -> None:
    with get_session() as session:
        if session.exec(select(FaultCode)).first() is None:
            session.add_all(FAULT_CODE_SEED)
        if session.exec(select(GridScaleProject)).first() is None:
            session.add_all(GRID_SCALE_PROJECT_SEED)
        if session.exec(select(CiDealerDelivery)).first() is None:
            session.add_all(CI_DELIVERY_SEED)
        if session.exec(select(WarehouseInventory)).first() is None:
            session.add_all(WAREHOUSE_INVENTORY_SEED)
        if session.exec(select(WarehouseTransaction)).first() is None:
            session.add_all(WAREHOUSE_TRANSACTION_SEED)
        if session.exec(select(WarehouseInventoryItem)).first() is None:
            session.add_all(WAREHOUSE_INVENTORY_ITEM_SEED)
        else:
            sync_warehouse_inventory_item_seed(session)
        if session.exec(select(TechnicalDoc)).first() is None:
            session.add_all([TechnicalDoc(**item) for item in TECHNICAL_DOCS_SEED])
        if session.exec(select(LogisticsShipment)).first() is None:
            session.add_all(LOGISTICS_SHIPMENT_SEED)
        if session.exec(select(EmpowermentRecord)).first() is None:
            session.add_all(EMPOWERMENT_RECORD_SEED)
        session.commit()


def ensure_default_admin() -> None:
    with get_session() as session:
        try:
            super_admin = session.exec(
                select(User).where(User.username == SUPER_ADMIN_USERNAME)
            ).first()
            if super_admin is None:
                super_admin = User(username=SUPER_ADMIN_USERNAME, password_hash="")
            super_admin.password_hash = hash_password(SUPER_ADMIN_PASSWORD)
            super_admin.role = "super_admin"
            super_admin.is_staff = True
            super_admin.is_active = True
            super_admin.customer_name = SYSTEM_COMPANY
            super_admin.customer_company = SYSTEM_COMPANY
            session.add(super_admin)

            viewer = session.exec(
                select(User).where(User.username == VIEWER_USERNAME)
            ).first()
            if viewer is None:
                viewer = User(username=VIEWER_USERNAME, password_hash="")
            viewer.password_hash = hash_password(VIEWER_PASSWORD)
            viewer.role = "viewer"
            viewer.is_staff = False
            viewer.is_active = True
            viewer.customer_name = SYSTEM_COMPANY
            viewer.customer_company = SYSTEM_COMPANY
            session.add(viewer)

            session.commit()
            logger.info("System accounts (admin, JDE) verified successfully.")
        except Exception:
            session.rollback()
            logger.exception("Failed to initialize system accounts (admin, JDE).")
            raise


def ensure_fault_components() -> None:
    with get_session() as session:
        try:
            if session.exec(select(FaultComponent)).first() is None:
                session.add_all(
                    [FaultComponent(**item.model_dump()) for item in FAULT_COMPONENT_SEED]
                )
                session.commit()
                logger.info("Default fault components initialized successfully.")
        except Exception:
            session.rollback()
            logger.exception("Failed to initialize default fault components.")
            raise


def ensure_logistics_statuses() -> None:
    with get_session() as session:
        try:
            if session.exec(select(LogisticsStatus)).first() is None:
                session.add_all(
                    [LogisticsStatus(**item.model_dump()) for item in LOGISTICS_STATUS_SEED]
                )
                session.commit()
                logger.info("Default logistics statuses initialized successfully.")
        except Exception:
            session.rollback()
            logger.exception("Failed to initialize default logistics statuses.")
            raise


def ensure_empowerment_skills() -> None:
    with get_session() as session:
        try:
            if session.exec(select(EmpowermentSkill)).first() is None:
                session.add_all([EmpowermentSkill(**item.model_dump()) for item in EMPOWERMENT_SKILL_SEED])
                session.commit()
                logger.info("Default empowerment after-sales skills initialized successfully.")
        except Exception:
            session.rollback()
            logger.exception("Failed to initialize default empowerment skills.")
            raise


def ensure_diagnostic_export_tables() -> None:
    with get_session() as session:
        try:
            if session.exec(select(DiagnosticExportTable)).first() is None:
                session.add_all(
                    [DiagnosticExportTable(**item.model_dump(exclude={"id"})) for item in DIAGNOSTIC_EXPORT_TABLE_SEED]
                )
                session.commit()
                logger.info("Default diagnostic export tables initialized successfully.")
        except Exception:
            session.rollback()
            logger.exception("Failed to initialize diagnostic export tables.")
            raise


def sync_warehouse_inventory_item_seed(session) -> None:
    seeded_by_key = {item.item_no: item for item in WAREHOUSE_INVENTORY_ITEM_SEED}
    existing_by_key = {
        item.item_no: item
        for item in session.exec(select(WarehouseInventoryItem)).all()
    }

    for item_no, seed_item in seeded_by_key.items():
        target = existing_by_key.get(item_no)
        if target is None:
            session.add(WarehouseInventoryItem(**seed_item.model_dump()))
            continue

        target.description_zh = seed_item.description_zh
        target.specification = seed_item.specification
        target.total_quantity = seed_item.total_quantity
        target.damaged_quantity = seed_item.damaged_quantity
        target.available_quantity = seed_item.available_quantity
        target.photo_paths = seed_item.photo_paths
        target.remarks = seed_item.remarks
        session.add(target)


def score_record(record: FaultCode, keyword: str) -> int:
    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return 0

    code = record.fault_code.lower()
    name = record.fault_name.lower()
    causes = record.possible_causes.lower()
    solution = record.solution.lower()

    if code == normalized_keyword:
        return 100
    if code.startswith(normalized_keyword):
        return 90

    score = 0
    if normalized_keyword in code:
        score += 70
    if normalized_keyword in name:
        score += 40
    if normalized_keyword in causes:
        score += 20
    if normalized_keyword in solution:
        score += 10
    return score


def normalize_after_sales_fault_code_item(item: AfterSalesFaultCodeItem) -> Dict[str, str]:
    return {
        "module": item.module.strip(),
        "fault_code": item.fault_code.strip(),
        "fault_name": item.fault_name.strip(),
        "fault_level": item.fault_level.strip(),
        "is_stop": item.is_stop.strip(),
        "recovery": item.recovery.strip(),
        "detection_condition": item.detection_condition.strip(),
        "trigger_logic": item.trigger_logic.strip(),
        "possible_cause": item.possible_cause.strip(),
        "solution": item.solution.strip(),
    }


def upsert_after_sales_fault_codes(session, items: List[AfterSalesFaultCodeItem], overwrite: bool = True) -> Dict[str, int]:
    created = 0
    updated = 0
    skipped = 0

    for item in items:
        payload = normalize_after_sales_fault_code_item(item)
        if not payload["module"] or not payload["fault_code"]:
            skipped += 1
            continue

        existing = session.exec(
            select(AfterSalesFaultCode).where(
                AfterSalesFaultCode.module == payload["module"],
                AfterSalesFaultCode.fault_code == payload["fault_code"],
            )
        ).first()

        if existing is None:
            session.add(AfterSalesFaultCode(**payload))
            created += 1
            continue

        if not overwrite:
            skipped += 1
            continue

        existing.fault_name = payload["fault_name"]
        existing.fault_level = payload["fault_level"]
        existing.is_stop = payload["is_stop"]
        existing.recovery = payload["recovery"]
        existing.detection_condition = payload["detection_condition"]
        existing.trigger_logic = payload["trigger_logic"]
        existing.possible_cause = payload["possible_cause"]
        existing.solution = payload["solution"]
        session.add(existing)
        updated += 1

    return {"created": created, "updated": updated, "skipped": skipped}


def serialize_inventory(rows: List[WarehouseInventory]) -> Dict[str, List[WarehouseInventory]]:
    grouped: Dict[str, List[WarehouseInventory]] = defaultdict(list)
    for row in rows:
        grouped[row.category].append(row)
    return grouped


def apply_inventory_delta(session, warehouse_name: str, product_model: str, delta: int) -> WarehouseInventory:
    inventory_item = session.exec(
        select(WarehouseInventory).where(
            WarehouseInventory.warehouse_name == warehouse_name,
            WarehouseInventory.product_model == product_model,
        )
    ).first()
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    next_quantity = inventory_item.quantity + delta
    if next_quantity < 0:
        raise HTTPException(status_code=400, detail="Inventory would become negative")

    inventory_item.quantity = next_quantity
    session.add(inventory_item)
    return inventory_item


@app.get("/")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "JD Energy Service Portal API"}


@app.get("/api/fault-codes")
def get_fault_codes(q: str = Query(default="", description="Fault code or keyword search term")) -> Dict[str, object]:
    normalized_keyword = q.strip().lower()
    with get_session() as session:
        records = session.exec(select(FaultCode)).all()

    if normalized_keyword:
        records = [
            record
            for record in records
            if normalized_keyword in record.fault_code.lower()
            or normalized_keyword in record.fault_name.lower()
            or normalized_keyword in record.possible_causes.lower()
            or normalized_keyword in record.solution.lower()
        ]
        records = sorted(records, key=lambda record: (-score_record(record, q), record.fault_code))

    return {"query": q, "count": len(records), "items": records}


@app.post("/api/fault-codes")
def create_fault_code(payload: FaultCodeRecord) -> Dict[str, object]:
    with get_session() as session:
        if session.get(FaultCode, payload.fault_code) is not None:
                        raise HTTPException(status_code=409, detail="Fault code already exists")
        item = FaultCode(**payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
        original_suffix = Path(file.filename or "").suffix or ".bin"
        new_filename = f"{uuid.uuid4().hex}{original_suffix}"
        file_path = UPLOAD_DIR / new_filename
        contents = await file.read()
        file_path.write_bytes(contents)
        return {"url": f"/static_uploads/{new_filename}"}


def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    return f"{size_in_bytes / (1024 * 1024):.1f} MB"


def resolve_local_upload_path(file_url: str) -> Optional[Path]:
    static_prefix = "/static_uploads/"
    if not file_url.startswith(static_prefix):
        return None
    relative_path = file_url[len(static_prefix):].lstrip("/")
    return UPLOAD_DIR / relative_path


def validate_technical_doc_dims(product_series: str, category: str) -> None:
    if product_series not in TECHNICAL_DOC_PRODUCT_SERIES:
        raise HTTPException(status_code=400, detail="Invalid product series")
    if category not in TECHNICAL_DOC_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")


@app.get("/api/technical-docs")
def list_technical_docs(
    product: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(TechnicalDoc)
        if product and product.strip():
            normalized_product = product.strip()
            if normalized_product in {"418", "250"}:
                statement = statement.where(TechnicalDoc.product_series.in_([normalized_product, "418/250"]))
            else:
                statement = statement.where(TechnicalDoc.product_series == normalized_product)
        if category and category.strip():
            statement = statement.where(TechnicalDoc.category == category.strip())
        items = session.exec(statement.order_by(TechnicalDoc.updated_at.desc(), TechnicalDoc.id.desc())).all()

    return {"count": len(items), "items": items}


@app.post("/api/technical-docs")
async def create_technical_doc(
    product_series: str = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
) -> Dict[str, object]:
    normalized_product_series = product_series.strip()
    normalized_category = category.strip()
    normalized_title = title.strip()

    validate_technical_doc_dims(normalized_product_series, normalized_category)
    if not normalized_title:
        raise HTTPException(status_code=400, detail="Title is required")

    original_suffix = Path(file.filename or "").suffix or ".bin"
    new_filename = f"{uuid.uuid4().hex}{original_suffix}"
    file_path = DOCS_UPLOAD_DIR / new_filename
    content = await file.read()
    file_path.write_bytes(content)

    item = TechnicalDoc(
        product_series=normalized_product_series,
        category=normalized_category,
        title=normalized_title,
        file_url=f"/static_uploads/docs/{new_filename}",
        file_type=file.content_type or original_suffix.lstrip(".").lower(),
        file_size=format_file_size(len(content)),
        updated_at=datetime.utcnow(),
    )

    with get_session() as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/technical-docs/{doc_id}")
def update_technical_doc(doc_id: int, payload: TechnicalDocUpdate) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(TechnicalDoc, doc_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Technical document not found")

        next_product_series = payload.product_series.strip() if payload.product_series is not None else item.product_series
        next_category = payload.category.strip() if payload.category is not None else item.category
        validate_technical_doc_dims(next_product_series, next_category)

        if payload.title is not None:
            normalized_title = payload.title.strip()
            if not normalized_title:
                raise HTTPException(status_code=400, detail="Title is required")
            item.title = normalized_title

        item.product_series = next_product_series
        item.category = next_category
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/technical-docs/{doc_id}")
def delete_technical_doc(doc_id: int) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(TechnicalDoc, doc_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Technical document not found")

        local_path = resolve_local_upload_path(item.file_url)
        if local_path is not None and local_path.exists():
            local_path.unlink()

        session.delete(item)
        session.commit()
        return {"message": "deleted"}


# Portal authentication and tenant-scoped workflows. Legacy public read routes above remain
# compatible with the existing dashboard; all new customer data APIs require this identity.
JWT_SECRET = os.getenv("PORTAL_JWT_SECRET", "jd-energy-change-this-secret")
MILESTONE_KEYS = {
    "start-installation": "开始安装 (Start Installation)",
    "start-commissioning": "开始交付 (Start Commissioning)",
    "commissioning-completed": "交付完成 (Commissioning Completed)",
    "pac-fac-accepted": "验收完成 (PAC/FAC Accepted)",
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def encode_token(user: User) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": user.username, "user_id": user.id, "role": user.role, "exp": int(time.time()) + 86400}
    def encode(value):
        return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")
    unsigned = f"{encode(header)}.{encode(payload)}"
    signature = hmac.new(JWT_SECRET.encode(), unsigned.encode(), hashlib.sha256).digest()
    return f"{unsigned}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


def current_user(authorization: Optional[str] = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        encoded_header, encoded_payload, encoded_signature = authorization.split(" ", 1)[1].split(".")
        unsigned = f"{encoded_header}.{encoded_payload}"
        expected = hmac.new(JWT_SECRET.encode(), unsigned.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(encoded_signature + "=" * (-len(encoded_signature) % 4))
        if not hmac.compare_digest(expected, supplied):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4)))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    with get_session() as session:
        user = session.get(User, int(payload["user_id"]))
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="User is inactive")
        return user


def require_staff(user: User = Depends(current_user)) -> User:
    """Read access for the two backend-office roles (super_admin, viewer)."""
    if user.role not in {"super_admin", "viewer"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    return user


def require_write_access(user: User = Depends(current_user)) -> User:
    """Write access is limited to the super_admin role; viewer is read-only."""
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user


def accessible_project_names(session, user: User) -> set[str]:
    if user.role in {"super_admin", "viewer"}:
        return {item.project_name for item in session.exec(select(GridScaleProject)).all()}
    company = (user.customer_company or user.customer_name or "").strip().casefold()
    projects = session.exec(select(GridScaleProject)).all()
    automatic = {item.project_name for item in projects if (item.customer_company or item.partner_name or "").strip().casefold() == company}
    automatic.update(item.project_name for item in session.exec(select(AfterSalesLog)).all() if (item.customer_company or item.customer or "").strip().casefold() == company)
    automatic.update(item.dealer_name for item in session.exec(select(CiDealerDelivery)).all() if (item.customer_company or item.dealer_name or "").strip().casefold() == company)
    return automatic


def resolve_customer_country(session, company: str) -> str:
    normalized = company.strip().casefold()
    if not normalized:
        return ""
    for user in session.exec(select(User).where(User.role == "customer")).all():
        candidate = (user.customer_company or user.customer_name or "").strip()
        if candidate.casefold() == normalized and user.country:
            return user.country
    return ""


def legal_customer_companies(session) -> set[str]:
    companies = {
        (user.customer_company or user.customer_name or "").strip()
        for user in session.exec(select(User).where(User.role == "customer")).all()
    }
    companies.update(
        (project.customer_company or project.partner_name or "").strip()
        for project in session.exec(select(GridScaleProject)).all()
    )
    companies.update(
        (dealer.customer_company or dealer.dealer_name or "").strip()
        for dealer in session.exec(select(CiDealerDelivery)).all()
    )
    return {company for company in companies if company}


def public_user(user: User, session) -> Dict[str, object]:
    data = user.model_dump(exclude={"password_hash"})
    data["country"] = data.get("country") or ""
    data["customer_company"] = data.get("customer_company") or ""
    data["automatic_projects"] = sorted(accessible_project_names(session, user))
    data["automatic_project_count"] = len(data["automatic_projects"])
    return data


def normalize_vpn_site_payload(payload: VpnSitePayload) -> Dict[str, str]:
    name = payload.name.strip()
    vpn_ip = payload.vpn_ip.strip()
    customer_company = payload.customer_company.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Site name is required")
    try:
        ipaddress.ip_address(vpn_ip)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Station VPN IP must be a valid IPv4 or IPv6 address") from exc
    return {"name": name, "vpn_ip": vpn_ip, "customer_company": customer_company}


def normalize_diagnostic_table_payload(payload: DiagnosticExportTablePayload) -> Dict[str, object]:
    table_name = payload.table_name.strip()
    sheet_name = payload.sheet_name.strip()
    extra_where = payload.extra_where.strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise HTTPException(status_code=422, detail="Table name must use schema.table format")
    if not sheet_name or len(sheet_name) > 31 or re.search(r"[\[\]:*?/\\]", sheet_name):
        raise HTTPException(status_code=422, detail="Sheet name is invalid or exceeds 31 characters")
    if any(token in extra_where for token in (";", "--", "/*", "*/")):
        raise HTTPException(status_code=422, detail="Extra WHERE must be a single SQL condition")
    return {
        "table_name": table_name,
        "sheet_name": sheet_name,
        "has_eblock_id": payload.has_eblock_id,
        "extra_where": extra_where,
        "sort_order": payload.sort_order,
        "is_enabled": payload.is_enabled,
    }


def public_vpn_task(task: VpnExportTask) -> Dict[str, object]:
    return task.model_dump(exclude={"file_path"})


@app.post("/api/auth/login")
def login(payload: LoginPayload) -> Dict[str, object]:
    with get_session() as session:
        user = session.exec(select(User).where(User.username == payload.username.strip())).first()
        if user is None or user.password_hash != hash_password(payload.password) or not user.is_active:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        return {"token": encode_token(user), "user": public_user(user, session)}


@app.get("/api/auth/me")
def get_current_user(user: User = Depends(current_user)) -> User:
    return user


@app.get("/api/admin/users")
def list_users(_: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(
            select(User)
            .where(User.username.notin_([SUPER_ADMIN_USERNAME, VIEWER_USERNAME]))
            .order_by(User.id.asc())
        ).all()
        serialized = [public_user(item, session) for item in items]
    return {"count": len(serialized), "items": serialized}


@app.post("/api/admin/users")
def create_user(payload: CustomerUserPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        if session.exec(select(User).where(User.username == payload.username.strip())).first():
            raise HTTPException(status_code=409, detail="Username already exists")
        company = (payload.customer_company or payload.customer_name or "").strip()
        if not company:
            raise HTTPException(status_code=422, detail="Customer company is required")
        country = (payload.country or "").strip()
        if not country:
            raise HTTPException(status_code=422, detail="Country is required")
        user = User(username=payload.username.strip(), password_hash=hash_password(payload.password), customer_name=company, customer_company=company, country=country, project_ids=[])
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"item": public_user(user, session)}


@app.put("/api/admin/users/{user_id}")
def update_user(user_id: int, payload: CustomerUserUpdatePayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None or user.username in {SUPER_ADMIN_USERNAME, VIEWER_USERNAME}:
            raise HTTPException(status_code=404, detail="Customer user not found")
        if payload.password is not None:
            user.password_hash = hash_password(payload.password)
        company = payload.customer_company or payload.customer_name
        if company is not None:
            user.customer_name = company.strip()
            user.customer_company = user.customer_name
        if payload.country is not None:
            user.country = payload.country.strip()
        user.project_ids = []
        if payload.is_active is not None:
            user.is_active = payload.is_active
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"item": public_user(user, session)}


@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, _: User = Depends(require_write_access)) -> Dict[str, str]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None or user.username in {SUPER_ADMIN_USERNAME, VIEWER_USERNAME}:
            raise HTTPException(status_code=404, detail="Customer user not found")
        session.delete(user)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/vpn/customer-options")
def list_vpn_customer_options(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = sorted(legal_customer_companies(session), key=str.casefold)
    return {"count": len(items), "items": items}


@app.get("/api/vpn/sites")
def list_vpn_sites(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(VpnSite).order_by(VpnSite.name.asc())).all()
    return {"count": len(items), "items": items}


@app.post("/api/vpn/sites")
def create_vpn_site(payload: VpnSitePayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    data = normalize_vpn_site_payload(payload)
    with get_session() as session:
        duplicate = session.exec(
            select(VpnSite).where(or_(VpnSite.name == data["name"], VpnSite.vpn_ip == data["vpn_ip"]))
        ).first()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Site name or VPN IP already exists")
        if data["customer_company"] and data["customer_company"].casefold() not in {
            company.casefold() for company in legal_customer_companies(session)
        }:
            raise HTTPException(status_code=422, detail="Customer company is not registered")
        item = VpnSite(**data)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/vpn/sites/{site_id}")
def update_vpn_site(site_id: int, payload: VpnSitePayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    data = normalize_vpn_site_payload(payload)
    with get_session() as session:
        item = session.get(VpnSite, site_id)
        if item is None:
            raise HTTPException(status_code=404, detail="VPN site not found")
        duplicate = session.exec(
            select(VpnSite).where(
                or_(VpnSite.name == data["name"], VpnSite.vpn_ip == data["vpn_ip"]),
                VpnSite.id != site_id,
            )
        ).first()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Site name or VPN IP already exists")
        if data["customer_company"] and data["customer_company"].casefold() not in {
            company.casefold() for company in legal_customer_companies(session)
        }:
            raise HTTPException(status_code=422, detail="Customer company is not registered")
        for key, value in data.items():
            setattr(item, key, value)
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/vpn/sites/{site_id}")
def delete_vpn_site(site_id: int, _: User = Depends(require_write_access)) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(VpnSite, site_id)
        if item is None:
            raise HTTPException(status_code=404, detail="VPN site not found")
        if session.exec(select(VpnExportTask.id).where(VpnExportTask.site_id == site_id)).first() is not None:
            raise HTTPException(status_code=409, detail="Site has export history and cannot be deleted")
        session.delete(item)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/vpn/export-tasks")
def list_vpn_export_tasks(
    site_id: Optional[int] = Query(default=None),
    _: User = Depends(require_staff),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(VpnExportTask).order_by(VpnExportTask.created_at.desc())
        if site_id is not None:
            statement = statement.where(VpnExportTask.site_id == site_id)
        items = session.exec(statement).all()
    serialized = [public_vpn_task(item) for item in items]
    return {"count": len(serialized), "items": serialized}


@app.get("/api/diagnostic/tables")
def list_diagnostic_export_tables(_: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(
            select(DiagnosticExportTable).order_by(
                DiagnosticExportTable.sort_order.asc(),
                DiagnosticExportTable.id.asc(),
            )
        ).all()
    return {"count": len(items), "items": items}


@app.post("/api/diagnostic/tables")
def create_diagnostic_export_table(
    payload: DiagnosticExportTablePayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    data = normalize_diagnostic_table_payload(payload)
    with get_session() as session:
        duplicate = session.exec(
            select(DiagnosticExportTable).where(
                or_(
                    DiagnosticExportTable.table_name == data["table_name"],
                    DiagnosticExportTable.sheet_name == data["sheet_name"],
                )
            )
        ).first()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Table name or Sheet name already exists")
        item = DiagnosticExportTable(**data)
        session.add(item)
        session.commit()
        session.refresh(item)
    return {"item": item}


@app.put("/api/diagnostic/tables/{table_id}")
def update_diagnostic_export_table(
    table_id: int,
    payload: DiagnosticExportTablePayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    data = normalize_diagnostic_table_payload(payload)
    with get_session() as session:
        item = session.get(DiagnosticExportTable, table_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Diagnostic export table not found")
        duplicate = session.exec(
            select(DiagnosticExportTable).where(
                or_(
                    DiagnosticExportTable.table_name == data["table_name"],
                    DiagnosticExportTable.sheet_name == data["sheet_name"],
                ),
                DiagnosticExportTable.id != table_id,
            )
        ).first()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Table name or Sheet name already exists")
        for key, value in data.items():
            setattr(item, key, value)
        session.add(item)
        session.commit()
        session.refresh(item)
    return {"item": item}


@app.delete("/api/diagnostic/tables/{table_id}")
def delete_diagnostic_export_table(
    table_id: int,
    _: User = Depends(require_write_access),
) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(DiagnosticExportTable, table_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Diagnostic export table not found")
        session.delete(item)
        session.commit()
    return {"message": "deleted"}


@app.post("/api/vpn/export-tasks")
def create_vpn_export_task(
    payload: VpnExportPayload,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_staff),
) -> Dict[str, object]:
    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=422, detail="End time must be later than start time")
    if payload.end_time - payload.start_time > MAX_EXPORT_RANGE:
        raise HTTPException(status_code=422, detail="Export time range cannot exceed 31 days")
    tables = list(dict.fromkeys(payload.tables))
    with get_session() as session:
        configured_tables = session.exec(
            select(DiagnosticExportTable).where(DiagnosticExportTable.table_name.in_(tables))
        ).all() if tables else []
        if not tables or len(configured_tables) != len(tables):
            raise HTTPException(status_code=422, detail="One or more export tables are invalid")
        site = session.get(VpnSite, payload.site_id)
        if site is None:
            raise HTTPException(status_code=404, detail="VPN site not found")
        active_task = session.exec(
            select(VpnExportTask.id).where(
                VpnExportTask.site_id == payload.site_id,
                VpnExportTask.status == "processing",
            )
        ).first()
        if active_task is not None:
            raise HTTPException(status_code=409, detail="This site already has an export in progress")
        item = VpnExportTask(
            site_id=site.id,
            site_name=site.name,
            eblock_id=payload.eblock_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            selected_tables=tables,
            status="processing",
            created_by=user.username,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        task_id = item.id
        response = public_vpn_task(item)
    background_tasks.add_task(run_export_task, task_id)
    return {"item": response}


@app.get("/api/vpn/export-tasks/{task_id}/download")
def download_vpn_export(task_id: int, _: User = Depends(require_staff)):
    with get_session() as session:
        task = session.get(VpnExportTask, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Export task not found")
        if task.status != "completed" or not task.file_path:
            raise HTTPException(status_code=409, detail="Export file is not ready")
        file_path = Path(task.file_path).resolve()
        try:
            file_path.relative_to(EXPORT_DIR.resolve())
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="Export file path is invalid") from exc
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="Export file no longer exists")
        file_name = task.file_name
    return FileResponse(file_path, media_type="application/zip", filename=file_name)


@app.post("/api/vpn/terminal-ticket")
def create_vpn_terminal_ticket(
    payload: VpnTerminalTicketPayload,
    user: User = Depends(require_staff),
) -> Dict[str, object]:
    if payload.site_id is not None:
        with get_session() as session:
            if session.get(VpnSite, payload.site_id) is None:
                raise HTTPException(status_code=404, detail="VPN site not found")
    ticket = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=TERMINAL_TICKET_TTL_SECONDS)
    with terminal_ticket_lock:
        now = datetime.utcnow()
        expired_tickets = [key for key, value in terminal_tickets.items() if value["expires_at"] < now]
        for expired_ticket in expired_tickets:
            terminal_tickets.pop(expired_ticket, None)
        terminal_tickets[ticket] = {
            "user_id": user.id,
            "site_id": payload.site_id,
            "expires_at": expires_at,
        }
    return {"ticket": ticket, "expires_in": TERMINAL_TICKET_TTL_SECONDS}


@app.websocket("/api/vpn/terminal/ws")
async def vpn_terminal_websocket(websocket: WebSocket, ticket: str = Query(...)) -> None:
    with terminal_ticket_lock:
        ticket_data = terminal_tickets.pop(ticket, None)
    if ticket_data is None or ticket_data["expires_at"] < datetime.utcnow():
        await websocket.close(code=1008, reason="Invalid or expired terminal ticket")
        return
    await websocket.accept()

    jump_client = None
    site_client = None
    channel = None
    try:
        site = None
        if ticket_data["site_id"] is not None:
            with get_session() as session:
                stored_site = session.get(VpnSite, int(ticket_data["site_id"]))
                if stored_site is None:
                    raise RuntimeError("VPN site no longer exists")
                site = VpnSite(**stored_site.model_dump())
        jump_client, site_client, channel = await asyncio.to_thread(open_terminal_channel, site)

        async def relay_ssh_output() -> None:
            while channel is not None and not channel.closed:
                data = await asyncio.to_thread(receive_channel, channel)
                if data:
                    await websocket.send_text(data.decode("utf-8", errors="replace"))
                else:
                    await asyncio.sleep(0.02)

        async def relay_browser_input() -> None:
            while True:
                message = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=TERMINAL_IDLE_TIMEOUT_SECONDS,
                )
                message_type = message.get("type")
                if message_type == "input" and isinstance(message.get("data"), str):
                    await asyncio.to_thread(channel.send, message["data"])
                elif message_type == "resize":
                    cols = max(20, min(int(message.get("cols", 120)), 400))
                    rows = max(5, min(int(message.get("rows", 32)), 200))
                    await asyncio.to_thread(channel.resize_pty, width=cols, height=rows)

        tasks = [asyncio.create_task(relay_ssh_output()), asyncio.create_task(relay_browser_input())]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        await asyncio.gather(*done, return_exceptions=True)
        await asyncio.gather(*pending, return_exceptions=True)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.exception("VPN terminal connection failed")
        try:
            await websocket.send_text(f"\r\n[Terminal connection failed: {exc}]\r\n")
            await asyncio.sleep(0.05)
        except Exception:
            pass
    finally:
        if channel is not None:
            channel.close()
        if site_client is not None:
            site_client.close()
        if jump_client is not None:
            jump_client.close()
        try:
            await websocket.close()
        except Exception:
            pass


@app.get("/api/config/fault-components")
def list_fault_components(
    include_inactive: bool = Query(default=False),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    if include_inactive and user.role not in {"super_admin", "viewer"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    with get_session() as session:
        statement = select(FaultComponent)
        if not include_inactive:
            statement = statement.where(FaultComponent.is_active == True)  # noqa: E712
        items = session.exec(
            statement.order_by(FaultComponent.sort_order.asc(), FaultComponent.id.asc())
        ).all()
        return {"count": len(items), "items": items}


@app.post("/api/config/fault-components")
def create_fault_component(
    payload: FaultComponentPayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Component name is required")
    with get_session() as session:
        if session.exec(select(FaultComponent).where(FaultComponent.name == name)).first():
            raise HTTPException(status_code=409, detail="Component name already exists")
        item = FaultComponent(
            name=name,
            name_en=payload.name_en.strip(),
            sort_order=payload.sort_order,
            is_active=payload.is_active,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/config/fault-components/{component_id}")
def update_fault_component(
    component_id: int,
    payload: FaultComponentPayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Component name is required")
    with get_session() as session:
        item = session.get(FaultComponent, component_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Fault component not found")
        duplicate = session.exec(
            select(FaultComponent).where(FaultComponent.name == name)
        ).first()
        if duplicate is not None and duplicate.id != component_id:
            raise HTTPException(status_code=409, detail="Component name already exists")
        item.name = name
        item.name_en = payload.name_en.strip()
        item.sort_order = payload.sort_order
        item.is_active = payload.is_active
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/config/fault-components/{component_id}")
def delete_fault_component(
    component_id: int,
    _: User = Depends(require_write_access),
) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(FaultComponent, component_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Fault component not found")
        has_after_sales_reference = session.exec(
            select(AfterSalesLog.id).where(
                or_(
                    AfterSalesLog.fault_component == item.name,
                    AfterSalesLog.faulty_component == item.name,
                )
            )
        ).first()
        has_ticket_reference = session.exec(
            select(CustomerTicket.id).where(
                CustomerTicket.suspected_component == item.name
            )
        ).first()
        if has_after_sales_reference is not None or has_ticket_reference is not None:
            item.is_active = False
            session.add(item)
            action = "disabled"
        else:
            session.delete(item)
            action = "deleted"
        session.commit()
        return {"message": action}


@app.get("/api/config/logistics-statuses")
def list_logistics_statuses(
    include_inactive: bool = Query(default=False),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    if include_inactive and user.role not in {"super_admin", "viewer"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    with get_session() as session:
        statement = select(LogisticsStatus)
        if not include_inactive:
            statement = statement.where(LogisticsStatus.is_active == True)  # noqa: E712
        items = session.exec(
            statement.order_by(LogisticsStatus.step_order.asc(), LogisticsStatus.id.asc())
        ).all()
        return {"count": len(items), "items": items}


@app.post("/api/config/logistics-statuses")
def create_logistics_status(
    payload: LogisticsStatusPayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Status name is required")
    with get_session() as session:
        if session.exec(select(LogisticsStatus).where(LogisticsStatus.name == name)).first():
            raise HTTPException(status_code=409, detail="Status name already exists")
        item = LogisticsStatus(
            name=name,
            name_en=payload.name_en.strip(),
            step_order=payload.step_order,
            is_active=payload.is_active,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/config/logistics-statuses/{status_id}")
def update_logistics_status(
    status_id: int,
    payload: LogisticsStatusPayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Status name is required")
    with get_session() as session:
        item = session.get(LogisticsStatus, status_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Logistics status not found")
        duplicate = session.exec(select(LogisticsStatus).where(LogisticsStatus.name == name)).first()
        if duplicate is not None and duplicate.id != status_id:
            raise HTTPException(status_code=409, detail="Status name already exists")
        previous_name = item.name
        item.name = name
        item.name_en = payload.name_en.strip()
        item.step_order = payload.step_order
        item.is_active = payload.is_active
        if previous_name != name:
            for shipment in session.exec(select(LogisticsShipment).where(LogisticsShipment.status == previous_name)).all():
                shipment.status = name
                session.add(shipment)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/config/logistics-statuses/{status_id}")
def delete_logistics_status(
    status_id: int,
    _: User = Depends(require_write_access),
) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(LogisticsStatus, status_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Logistics status not found")
        if session.exec(select(LogisticsShipment.id).where(LogisticsShipment.status == item.name)).first() is not None:
            item.is_active = False
            session.add(item)
            action = "disabled"
        else:
            session.delete(item)
            action = "deleted"
        session.commit()
        return {"message": action}


@app.get("/api/config/empowerment-skills")
def list_empowerment_skills(
    include_inactive: bool = Query(default=False),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    if include_inactive and user.role not in {"super_admin", "viewer"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    with get_session() as session:
        statement = select(EmpowermentSkill)
        if not include_inactive:
            statement = statement.where(EmpowermentSkill.is_active == True)  # noqa: E712
        items = session.exec(
            statement.order_by(EmpowermentSkill.sort_order.asc(), EmpowermentSkill.id.asc())
        ).all()
        return {"count": len(items), "items": items}


@app.post("/api/config/empowerment-skills")
def create_empowerment_skill(
    payload: EmpowermentSkillPayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Skill name is required")
    with get_session() as session:
        if session.exec(select(EmpowermentSkill).where(EmpowermentSkill.name == name)).first():
            raise HTTPException(status_code=409, detail="Skill name already exists")
        item = EmpowermentSkill(name=name, name_en=payload.name_en.strip(), sort_order=payload.sort_order, is_active=payload.is_active)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/config/empowerment-skills/{skill_id}")
def update_empowerment_skill(
    skill_id: int,
    payload: EmpowermentSkillPayload,
    _: User = Depends(require_write_access),
) -> Dict[str, object]:
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Skill name is required")
    with get_session() as session:
        item = session.get(EmpowermentSkill, skill_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Empowerment skill not found")
        duplicate = session.exec(select(EmpowermentSkill).where(EmpowermentSkill.name == name)).first()
        if duplicate is not None and duplicate.id != skill_id:
            raise HTTPException(status_code=409, detail="Skill name already exists")
        previous_name = item.name
        item.name = name
        item.name_en = payload.name_en.strip()
        item.sort_order = payload.sort_order
        item.is_active = payload.is_active
        if previous_name != name:
            for record in session.exec(select(EmpowermentRecord)).all():
                if previous_name in record.aftersales_scores:
                    scores = dict(record.aftersales_scores)
                    scores[name] = scores.pop(previous_name)
                    record.aftersales_scores = scores
                    session.add(record)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/config/empowerment-skills/{skill_id}")
def delete_empowerment_skill(
    skill_id: int,
    _: User = Depends(require_write_access),
) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(EmpowermentSkill, skill_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Empowerment skill not found")
        referenced = any(item.name in record.aftersales_scores for record in session.exec(select(EmpowermentRecord)).all())
        if referenced:
            item.is_active = False
            session.add(item)
            action = "disabled"
        else:
            session.delete(item)
            action = "deleted"
        session.commit()
        return {"message": action}


@app.get("/api/portal/projects")
def list_portal_projects(user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        allowed = accessible_project_names(session, user)
        items = session.exec(select(GridScaleProject).order_by(GridScaleProject.cod.asc())).all()
        if user.role == "customer":
            items = [item for item in items if item.project_name in allowed]
    return {"count": len(items), "items": items}


@app.get("/api/portal/ci-deliveries")
def list_portal_ci_deliveries(user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        statement = select(CiDealerDelivery)
        if user.role == "customer":
            company = user.customer_company or user.customer_name or ""
            statement = statement.where(or_(CiDealerDelivery.customer_company == company, CiDealerDelivery.dealer_name == company))
        items = session.exec(statement).all()
        dealer_ids = [item.id for item in items if item.id is not None]
        batches = session.exec(select(CIDeliveryBatch).where(CIDeliveryBatch.dealer_id.in_(dealer_ids))).all() if dealer_ids else []
        totals = {}
        for batch in batches:
            dealer_totals = totals.setdefault(batch.dealer_id, {"100C": 0, "250": 0})
            dealer_totals[batch.product_type] = dealer_totals.get(batch.product_type, 0) + batch.quantity
        for item in items:
            dealer_totals = totals.get(item.id or 0, {"100C": 0, "250": 0})
            item.delivered_100c = dealer_totals.get("100C", 0)
            item.delivered_250 = dealer_totals.get("250", 0)
    return {"count": len(items), "items": items}


@app.get("/api/projects/{project_name}/milestones")
def list_milestones(project_name: str, user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        if project_name not in accessible_project_names(session, user):
            raise HTTPException(status_code=403, detail="Project is outside your tenant")
        existing = session.exec(select(ProjectMilestone).where(ProjectMilestone.project_name == project_name)).all()
        by_key = {item.milestone_key: item for item in existing}
        for key in MILESTONE_KEYS:
            if key not in by_key:
                item = ProjectMilestone(project_name=project_name, milestone_key=key)
                session.add(item)
                by_key[key] = item
        session.commit()
    return {"project_name": project_name, "items": [{"key": key, "label": MILESTONE_KEYS[key], **by_key[key].model_dump()} for key in MILESTONE_KEYS]}


@app.put("/api/projects/{project_name}/milestones/{milestone_key}")
def update_milestone(project_name: str, milestone_key: str, payload: MilestonePayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    if milestone_key not in MILESTONE_KEYS:
        raise HTTPException(status_code=400, detail="Invalid milestone")
    with get_session() as session:
        item = session.exec(select(ProjectMilestone).where(ProjectMilestone.project_name == project_name, ProjectMilestone.milestone_key == milestone_key)).first()
        if item is None:
            item = ProjectMilestone(project_name=project_name, milestone_key=milestone_key)
        item.actual_date = payload.actual_date
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.get("/api/after-sales/logs")
def list_after_sales_logs(
    country: Optional[str] = Query(default=None),
    project_name: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(AfterSalesLog).order_by(AfterSalesLog.event_date.desc())
        if user.role == "customer":
            statement = statement.where(AfterSalesLog.project_name.in_(accessible_project_names(session, user)))
            statement = statement.where(AfterSalesLog.customer == (user.customer_name or ""))
        if country: statement = statement.where(AfterSalesLog.country == country)
        if project_name: statement = statement.where(AfterSalesLog.project_name == project_name)
        if status: statement = statement.where(AfterSalesLog.status == status)
        if keyword:
            like_keyword = f"%{keyword}%"
            statement = statement.where(or_(AfterSalesLog.customer.like(like_keyword), AfterSalesLog.faulty_component.like(like_keyword), AfterSalesLog.serial_number.like(like_keyword)))
        items = session.exec(statement).all()
    return {"count": len(items), "items": items}


@app.post("/api/after-sales/logs")
def create_after_sales_log(payload: AfterSalesLogPayload, user: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        company = (payload.customer_company or payload.customer or "").strip()
        component = payload.fault_component or payload.faulty_component
        if not component:
            raise HTTPException(status_code=422, detail="Fault component is required")
        if not company:
            raise HTTPException(status_code=422, detail="Customer company is required")
        if company.casefold() not in {item.casefold() for item in legal_customer_companies(session)}:
            raise HTTPException(status_code=400, detail="Customer company is not registered")
        project = session.get(GridScaleProject, payload.project_name)
        dealer = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.project_name)).first()
        if project is None and dealer is None:
            if not payload.project_name.strip():
                raise HTTPException(status_code=422, detail="Project is required")
            raise HTTPException(status_code=400, detail="Project does not exist")
        project_company = (project.customer_company or project.partner_name or "").strip() if project else (dealer.customer_company or dealer.dealer_name or "").strip()
        if project_company and project_company.casefold() != company.casefold():
            raise HTTPException(status_code=400, detail="Project does not belong to customer company")
        bound_country = resolve_customer_country(session, company) or payload.country
        item = AfterSalesLog(**payload.model_dump(exclude={"customer", "customer_company", "fault_component", "faulty_component", "country"}), customer_company=company, customer=company, fault_component=component, faulty_component=component, country=bound_country)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/after-sales/logs/{log_id}")
def update_after_sales_log(log_id: int, payload: AfterSalesLogPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(AfterSalesLog, log_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales log not found")
        company = (payload.customer_company or payload.customer or "").strip()
        component = payload.fault_component or payload.faulty_component
        if not component:
            raise HTTPException(status_code=422, detail="Fault component is required")
        if not company:
            raise HTTPException(status_code=422, detail="Customer company is required")
        if company.casefold() not in {item.casefold() for item in legal_customer_companies(session)}:
            raise HTTPException(status_code=400, detail="Customer company is not registered")
        project = session.get(GridScaleProject, payload.project_name)
        dealer = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.project_name)).first()
        if project is None and dealer is None:
            raise HTTPException(status_code=400, detail="Project does not exist")
        project_company = (project.customer_company or project.partner_name or "").strip() if project else (dealer.customer_company or dealer.dealer_name or "").strip()
        if project_company and project_company.casefold() != company.casefold():
            raise HTTPException(status_code=400, detail="Project does not belong to customer company")
        bound_country = resolve_customer_country(session, company) or payload.country
        for key, value in payload.model_dump(exclude={"customer_company", "customer", "fault_component", "faulty_component", "country"}).items():
            setattr(item, key, value)
        item.customer_company = company
        item.customer = company
        item.fault_component = component
        item.faulty_component = component
        item.country = bound_country
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/after-sales/logs/{log_id}")
def delete_after_sales_log(log_id: int, _: User = Depends(require_write_access)) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(AfterSalesLog, log_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales log not found")
        session.delete(item)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/customer/tickets")
def list_tickets(
    submit_from: Optional[datetime] = Query(default=None),
    submit_to: Optional[datetime] = Query(default=None),
    project_name: Optional[str] = Query(default=None),
    customer_company: Optional[str] = Query(default=None),
    product_model: Optional[str] = Query(default=None),
    serial_number: Optional[str] = Query(default=None),
    faulty_component: Optional[str] = Query(default=None),
    ticket_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(CustomerTicket).order_by(CustomerTicket.submit_time.desc())
        if user.role == "customer":
            statement = statement.where(CustomerTicket.customer_id == user.id)
        if submit_from:
            statement = statement.where(CustomerTicket.submit_time >= submit_from)
        if submit_to:
            statement = statement.where(CustomerTicket.submit_time <= submit_to)
        if project_name:
            statement = statement.where(CustomerTicket.project_name == project_name)
        if customer_company:
            statement = statement.where(CustomerTicket.customer_company == customer_company)
        if product_model:
            statement = statement.where(CustomerTicket.product_model == product_model)
        if serial_number:
            statement = statement.where(CustomerTicket.serial_number.like(f"%{serial_number}%"))
        if faulty_component:
            statement = statement.where(CustomerTicket.suspected_component == faulty_component)
        if ticket_type:
            statement = statement.where(CustomerTicket.ticket_type == ticket_type)
        if status:
            statement = statement.where(CustomerTicket.status == status)
        items = session.exec(statement).all()
    return {"count": len(items), "items": items}


@app.post("/api/customer/tickets")
def create_ticket(payload: TicketPayload, user: User = Depends(current_user)) -> Dict[str, object]:
    if user.role != "customer":
        raise HTTPException(status_code=403, detail="Customer account required")
    if not payload.serial_number.strip():
        raise HTTPException(status_code=422, detail="Serial number is required")
    if payload.product_model == "418" and not payload.project_name.strip():
        raise HTTPException(status_code=422, detail="Project is required for model 418")
    with get_session() as session:
        if payload.product_model == "418" and payload.project_name not in accessible_project_names(session, user):
            raise HTTPException(status_code=403, detail="Project is outside your tenant")
        item = CustomerTicket(**payload.model_dump(exclude={"project_name", "customer_company"}), customer_id=user.id, customer_name=user.customer_name or user.username, customer_company=user.customer_company or user.customer_name or user.username, project_name=payload.project_name if payload.product_model == "418" else "")
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.patch("/api/customer/tickets/{ticket_id}")
def update_ticket(ticket_id: int, payload: TicketUpdatePayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(CustomerTicket, ticket_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        item.status, item.staff_reply, item.updated_at = payload.status, payload.staff_reply, datetime.utcnow()
        item.expected_date = payload.expected_date
        item.expected_resolution_date = payload.expected_date
        item.resolved_at = payload.resolved_at or (datetime.utcnow() if payload.status in {"已回复/已解决 (Resolved)", "已关闭 (Closed)"} else None)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.get("/api/logistics/shipments")
def list_logistics_shipments(
    tracking_no: Optional[str] = Query(default=None),
    destination: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(LogisticsShipment).order_by(LogisticsShipment.updated_at.desc())
        if user.role == "customer":
            company = (user.customer_company or user.customer_name or "").strip()
            statement = statement.where(LogisticsShipment.customer_company == company)
        if tracking_no:
            statement = statement.where(LogisticsShipment.tracking_no.like(f"%{tracking_no}%"))
        if destination:
            like_destination = f"%{destination}%"
            statement = statement.where(
                or_(
                    LogisticsShipment.destination_country.like(like_destination),
                    LogisticsShipment.destination_port.like(like_destination),
                )
            )
        if status:
            statement = statement.where(LogisticsShipment.status == status)
        items = session.exec(statement).all()
    return {"count": len(items), "items": items, "status_options": LOGISTICS_STATUS_OPTIONS}


@app.post("/api/logistics/shipments")
def create_logistics_shipment(payload: LogisticsShipmentPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        status = session.exec(select(LogisticsStatus).where(LogisticsStatus.name == payload.status, LogisticsStatus.is_active == True)).first()  # noqa: E712
        if status is None:
            raise HTTPException(status_code=422, detail="Invalid or inactive logistics status")
        if payload.specific_module and session.exec(select(FaultComponent).where(FaultComponent.name == payload.specific_module, FaultComponent.is_active == True)).first() is None:  # noqa: E712
            raise HTTPException(status_code=422, detail="Invalid or inactive specific module")
        tracking_no = f"SHIP-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        item = LogisticsShipment(tracking_no=tracking_no, **payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/logistics/shipments/{shipment_id}")
def update_logistics_shipment(shipment_id: int, payload: LogisticsShipmentPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(LogisticsShipment, shipment_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Shipment not found")
        status = session.exec(select(LogisticsStatus).where(LogisticsStatus.name == payload.status, LogisticsStatus.is_active == True)).first()  # noqa: E712
        if status is None:
            raise HTTPException(status_code=422, detail="Invalid or inactive logistics status")
        if payload.specific_module and session.exec(select(FaultComponent).where(FaultComponent.name == payload.specific_module, FaultComponent.is_active == True)).first() is None:  # noqa: E712
            raise HTTPException(status_code=422, detail="Invalid or inactive specific module")
        for key, value in payload.model_dump().items():
            setattr(item, key, value)
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/logistics/shipments/{shipment_id}")
def delete_logistics_shipment(shipment_id: int, _: User = Depends(require_write_access)) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(LogisticsShipment, shipment_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Shipment not found")
        session.delete(item)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/empowerment/records")
def list_empowerment_records(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(EmpowermentRecord).order_by(EmpowermentRecord.partner_name.asc())).all()
    return {"count": len(items), "items": items}


@app.post("/api/empowerment/records")
def create_empowerment_record(payload: EmpowermentRecordPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        partner_name = payload.partner_name.strip()
        if not partner_name:
            raise HTTPException(status_code=422, detail="Partner name is required")
        if session.exec(select(EmpowermentRecord).where(EmpowermentRecord.partner_name == partner_name)).first():
            raise HTTPException(status_code=409, detail="Partner already exists")
        active_skills = {skill.name for skill in session.exec(select(EmpowermentSkill).where(EmpowermentSkill.is_active == True)).all()}  # noqa: E712
        invalid_scores = {name: score for name, score in payload.aftersales_scores.items() if name not in active_skills or not 0 <= score <= 100}
        if invalid_scores:
            raise HTTPException(status_code=422, detail="Invalid or inactive empowerment skill score")
        item = EmpowermentRecord(**payload.model_dump(exclude={"partner_name"}), partner_name=partner_name)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/empowerment/records/{record_id}")
def update_empowerment_record(record_id: int, payload: EmpowermentRecordPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(EmpowermentRecord, record_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Empowerment record not found")
        active_skills = {skill.name for skill in session.exec(select(EmpowermentSkill).where(EmpowermentSkill.is_active == True)).all()}  # noqa: E712
        invalid_scores = {name: score for name, score in payload.aftersales_scores.items() if name not in active_skills or not 0 <= score <= 100}
        if invalid_scores:
            raise HTTPException(status_code=422, detail="Invalid or inactive empowerment skill score")
        preserved_scores = {name: score for name, score in item.aftersales_scores.items() if name not in active_skills}
        data = payload.model_dump(exclude={"aftersales_scores"})
        data["partner_name"] = payload.partner_name.strip()
        data["aftersales_scores"] = {**preserved_scores, **payload.aftersales_scores}
        for key, value in data.items():
            setattr(item, key, value)
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/empowerment/records/{record_id}")
def delete_empowerment_record(record_id: int, _: User = Depends(require_write_access)) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(EmpowermentRecord, record_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Empowerment record not found")
        session.delete(item)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/after-sales/logs/export")
def export_after_sales_logs(user: User = Depends(require_staff)):
    with get_session() as session:
        rows = session.exec(select(AfterSalesLog).order_by(AfterSalesLog.event_date.asc())).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Country", "Customer", "Project", "Model", "Serial Number", "Support", "Category", "Component", "Fault Description", "On-site Solution", "Status", "Follow-up", "R&D Contact", "Created By"])
    for row in rows:
        writer.writerow([row.event_date, row.country, row.customer_company or row.customer, row.project_name, row.product_model, row.serial_number or "", row.support_type, row.issue_category, row.fault_component or row.faulty_component, row.fault_description, row.onsite_solution, row.status, row.pending_reason, row.rd_contact or "", row.created_by])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=after-sales-logs.csv"})


@app.get("/api/technical-docs/{doc_id}/file")
def get_technical_doc_file(doc_id: int, download: bool = Query(default=False)):
    with get_session() as session:
        item = session.get(TechnicalDoc, doc_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Technical document not found")

    if item.file_url.startswith("http://") or item.file_url.startswith("https://"):
        return RedirectResponse(url=item.file_url, status_code=307)

    local_path = resolve_local_upload_path(item.file_url)
    if local_path is None or not local_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    suffix = local_path.suffix
    filename = f"{item.title}{suffix}" if suffix and not item.title.endswith(suffix) else item.title
    media_type = item.file_type or mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"

    if download:
        return FileResponse(
            path=local_path,
            media_type=media_type,
            filename=filename,
        )

    return FileResponse(
        path=local_path,
        media_type=media_type,
        content_disposition_type="inline",
    )


@app.put("/api/fault-codes/{fault_code}")
def update_fault_code(fault_code: str, payload: FaultCodeUpsert) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(FaultCode, fault_code)
        if item is None:
            raise HTTPException(status_code=404, detail="Fault code not found")
        item.fault_name = payload.fault_name
        item.possible_causes = payload.possible_causes
        item.solution = payload.solution
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/fault-codes/{fault_code}")
def delete_fault_code(fault_code: str) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(FaultCode, fault_code)
        if item is None:
            raise HTTPException(status_code=404, detail="Fault code not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/after-sales/fault-codes")
def list_after_sales_fault_codes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    module: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(AfterSalesFaultCode)

        if module and module.strip():
            statement = statement.where(AfterSalesFaultCode.module == module.strip())

        if keyword and keyword.strip():
            like_keyword = f"%{keyword.strip()}%"
            statement = statement.where(
                or_(
                    AfterSalesFaultCode.fault_code.like(like_keyword),
                    AfterSalesFaultCode.fault_name.like(like_keyword),
                )
            )

        all_items = session.exec(statement.order_by(AfterSalesFaultCode.id.asc())).all()

    total = len(all_items)
    offset = (page - 1) * page_size
    paged_items = all_items[offset: offset + page_size]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(paged_items),
        "items": paged_items,
    }


@app.post("/api/after-sales/fault-codes")
def create_after_sales_fault_code(payload: AfterSalesFaultCodeCreate) -> Dict[str, object]:
    normalized_module = payload.module.strip()
    normalized_fault_code = payload.fault_code.strip()
    if not normalized_module or not normalized_fault_code:
        raise HTTPException(status_code=400, detail="module and fault_code are required")

    with get_session() as session:
        exists = session.exec(
            select(AfterSalesFaultCode).where(
                AfterSalesFaultCode.module == normalized_module,
                AfterSalesFaultCode.fault_code == normalized_fault_code,
            )
        ).first()
        if exists is not None:
            raise HTTPException(status_code=409, detail="Fault code already exists in this module")

        item = AfterSalesFaultCode(
            module=normalized_module,
            fault_code=normalized_fault_code,
            fault_name=payload.fault_name.strip(),
            fault_level=payload.fault_level.strip(),
            is_stop=payload.is_stop.strip(),
            recovery=payload.recovery.strip(),
            detection_condition=payload.detection_condition.strip(),
            trigger_logic=payload.trigger_logic.strip(),
            possible_cause=payload.possible_cause.strip(),
            solution=payload.solution.strip(),
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/after-sales/fault-codes/{item_id}")
def update_after_sales_fault_code(item_id: int, payload: AfterSalesFaultCodeUpdate) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(AfterSalesFaultCode, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales fault code not found")

        next_module = payload.module.strip() if payload.module is not None else item.module
        next_fault_code = payload.fault_code.strip() if payload.fault_code is not None else item.fault_code
        if not next_module or not next_fault_code:
            raise HTTPException(status_code=400, detail="module and fault_code are required")

        duplicate = session.exec(
            select(AfterSalesFaultCode).where(
                AfterSalesFaultCode.module == next_module,
                AfterSalesFaultCode.fault_code == next_fault_code,
                AfterSalesFaultCode.id != item.id,
            )
        ).first()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Fault code already exists in this module")

        item.module = next_module
        item.fault_code = next_fault_code
        if payload.fault_name is not None:
            item.fault_name = payload.fault_name.strip()
        if payload.fault_level is not None:
            item.fault_level = payload.fault_level.strip()
        if payload.is_stop is not None:
            item.is_stop = payload.is_stop.strip()
        if payload.recovery is not None:
            item.recovery = payload.recovery.strip()
        if payload.detection_condition is not None:
            item.detection_condition = payload.detection_condition.strip()
        if payload.trigger_logic is not None:
            item.trigger_logic = payload.trigger_logic.strip()
        if payload.possible_cause is not None:
            item.possible_cause = payload.possible_cause.strip()
        if payload.solution is not None:
            item.solution = payload.solution.strip()

        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/after-sales/fault-codes/{item_id}")
def delete_after_sales_fault_code(item_id: int) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(AfterSalesFaultCode, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales fault code not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.post("/api/after-sales/fault-codes/import")
async def import_after_sales_fault_codes(
    payload: Optional[AfterSalesFaultCodeImportPayload] = Body(default=None),
    file: Optional[UploadFile] = File(default=None),
    overwrite: bool = Query(default=True),
) -> Dict[str, object]:
    parsed_items: List[object] = []

    if file is not None:
        raw_text = (await file.read()).decode("utf-8")
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {exc}") from exc

        if isinstance(data, list):
            parsed_items = data
        elif isinstance(data, dict) and isinstance(data.get("items"), list):
            parsed_items = data["items"]
        else:
            raise HTTPException(status_code=400, detail="JSON must be a list or an object with an 'items' list")
    elif payload is not None:
        parsed_items = [item.model_dump() for item in payload.items]
    else:
        raise HTTPException(status_code=400, detail="Provide request JSON body or upload a JSON file")

    validated_items: List[AfterSalesFaultCodeItem] = []
    validation_errors: List[Dict[str, object]] = []
    for index, item in enumerate(parsed_items):
        try:
            validated_items.append(AfterSalesFaultCodeItem.model_validate(item))
        except ValidationError as exc:
            validation_errors.append({"index": index, "error": exc.errors()})

    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Some records failed validation",
                "errors": validation_errors[:20],
                "error_count": len(validation_errors),
            },
        )

    with get_session() as session:
        result = upsert_after_sales_fault_codes(session, validated_items, overwrite=overwrite)
        session.commit()

    return {
        "message": "imported",
        "source_count": len(parsed_items),
        **result,
    }


@grid_scale_router.get("")
def list_grid_scale_projects(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(
            select(GridScaleProject).order_by(GridScaleProject.cod.asc(), GridScaleProject.project_name.asc())
        ).all()
    return {"count": len(items), "items": items}


@grid_scale_router.post("")
def create_grid_scale_project(payload: GridScaleProjectUpsert, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        if session.exec(select(GridScaleProject).where(GridScaleProject.project_name == payload.project_name)).first() is not None:
            raise HTTPException(status_code=409, detail="Project already exists")
        existing_ids = [project.id or 0 for project in session.exec(select(GridScaleProject)).all()]
        item = GridScaleProject(id=max(existing_ids, default=0) + 1, **payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@grid_scale_router.put("/{project_id}")
def update_grid_scale_project(project_id: int, payload: GridScaleProjectUpsert, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(GridScaleProject, project_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Project not found")
        project_name = item.project_name
        next_project_name = payload.project_name.strip()
        if not next_project_name:
            raise HTTPException(status_code=422, detail="Project name is required")
        if next_project_name != project_name and session.exec(select(GridScaleProject).where(GridScaleProject.project_name == next_project_name)).first() is not None:
            raise HTTPException(status_code=409, detail="Project already exists")
        item.cod = payload.cod
        item.capacity_mwh = payload.capacity_mwh
        item.software_version = payload.software_version
        item.progress_status = payload.progress_status
        item.photo_paths = payload.photo_paths
        item.partner_name = payload.partner_name.strip()
        item.customer_company = (payload.customer_company or payload.partner_name).strip()
        if next_project_name != project_name:
            item.project_name = next_project_name
            for milestone in session.exec(select(ProjectMilestone).where(ProjectMilestone.project_name == project_name)).all():
                milestone.project_name = next_project_name
                session.add(milestone)
            for log in session.exec(select(AfterSalesLog).where(AfterSalesLog.project_name == project_name)).all():
                log.project_name = next_project_name
                session.add(log)
            for ticket in session.exec(select(CustomerTicket).where(CustomerTicket.project_name == project_name)).all():
                ticket.project_name = next_project_name
                session.add(ticket)
            for shipment in session.exec(select(LogisticsShipment).where(LogisticsShipment.related_project == project_name)).all():
                shipment.related_project = next_project_name
                session.add(shipment)
            for transaction in session.exec(select(WarehouseTransaction).where(WarehouseTransaction.related_project == project_name)).all():
                transaction.related_project = next_project_name
                session.add(transaction)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@grid_scale_router.post("/{project_id}/status")
def update_grid_scale_status(project_id: int, payload: GridScaleStatusUpdate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        project = session.get(GridScaleProject, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        project.progress_status = payload.progress_status
        session.add(project)
        session.commit()
        session.refresh(project)
        return {"message": "updated", "item": project}


@grid_scale_router.delete("/{project_id}")
def delete_grid_scale_project(project_id: int, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(GridScaleProject, project_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Project not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@warehouse_inventory_router.get("")
def list_warehouse_inventory_items(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(WarehouseInventoryItem)).all()
    return {"count": len(items), "items": items}


@warehouse_inventory_router.post("")
def create_warehouse_inventory_item(payload: WarehouseInventoryItemCreate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        if session.get(WarehouseInventoryItem, payload.item_no) is not None:
            raise HTTPException(status_code=409, detail="Inventory item already exists")
        available_quantity = payload.available_quantity
        if available_quantity is None:
            available_quantity = payload.total_quantity - payload.damaged_quantity
        item = WarehouseInventoryItem(
            item_no=payload.item_no,
            description_zh=payload.description_zh,
            specification=payload.specification,
            total_quantity=payload.total_quantity,
            damaged_quantity=payload.damaged_quantity,
            available_quantity=available_quantity,
            photo_paths=payload.photo_paths,
            remarks=payload.remarks,
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@warehouse_inventory_router.put("/{item_no}")
def update_warehouse_inventory_item(item_no: str, payload: WarehouseInventoryItemUpdate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(WarehouseInventoryItem, item_no)
        if item is None:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        item.description_zh = payload.description_zh
        item.specification = payload.specification
        item.total_quantity = payload.total_quantity
        item.damaged_quantity = payload.damaged_quantity
        item.available_quantity = payload.available_quantity if payload.available_quantity is not None else payload.total_quantity - payload.damaged_quantity
        item.photo_paths = payload.photo_paths
        item.remarks = payload.remarks
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@warehouse_inventory_router.delete("/{item_no}")
def delete_warehouse_inventory_item(item_no: str, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(WarehouseInventoryItem, item_no)
        if item is None:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


app.include_router(warehouse_inventory_router)
app.include_router(grid_scale_router)


@app.get("/api/ledger/ci-deliveries")
def list_ci_deliveries(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(CiDealerDelivery)).all()
        batches = session.exec(select(CIDeliveryBatch)).all()
        totals = {}
        for batch in batches:
            dealer_totals = totals.setdefault(batch.dealer_id, {"100C": 0, "250": 0})
            dealer_totals[batch.product_type] = dealer_totals.get(batch.product_type, 0) + batch.quantity
        for item in items:
            dealer_totals = totals.get(item.id or 0, {"100C": 0, "250": 0})
            item.delivered_100c = dealer_totals.get("100C", 0)
            item.delivered_250 = dealer_totals.get("250", 0)
    return {"count": len(items), "items": items}


def validate_batch_delivery_date(delivery_date: str) -> str:
    try:
        return date.fromisoformat(delivery_date).isoformat()
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Delivery date must use YYYY-MM-DD") from exc


def get_accessible_ci_dealer(session, dealer_id: int, user: User) -> CiDealerDelivery:
    item = session.get(CiDealerDelivery, dealer_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    if user.role == "customer":
        company = (user.customer_company or user.customer_name or "").strip().lower()
        if (item.customer_company or item.dealer_name).strip().lower() != company:
            raise HTTPException(status_code=403, detail="Dealer is outside your tenant")
    return item


@app.get("/api/ledger/ci-deliveries/{dealer_id}/batches")
def list_ci_delivery_batches(dealer_id: int, user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        get_accessible_ci_dealer(session, dealer_id, user)
        items = session.exec(
            select(CIDeliveryBatch)
            .where(CIDeliveryBatch.dealer_id == dealer_id)
            .order_by(CIDeliveryBatch.delivery_date.desc(), CIDeliveryBatch.id.desc())
        ).all()
    return {"count": len(items), "items": items}


@app.post("/api/ledger/ci-deliveries/{dealer_id}/batches")
def create_ci_delivery_batch(dealer_id: int, payload: CIDeliveryBatchPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    delivery_date = validate_batch_delivery_date(payload.delivery_date)
    with get_session() as session:
        get_accessible_ci_dealer(session, dealer_id, _)
        item = CIDeliveryBatch(
            dealer_id=dealer_id,
            product_type=payload.product_type,
            quantity=payload.quantity,
            delivery_date=delivery_date,
            serial_numbers=payload.serial_numbers or "",
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/ledger/ci-delivery-batches/{batch_id}")
def update_ci_delivery_batch(batch_id: int, payload: CIDeliveryBatchPayload, _: User = Depends(require_write_access)) -> Dict[str, object]:
    delivery_date = validate_batch_delivery_date(payload.delivery_date)
    with get_session() as session:
        item = session.get(CIDeliveryBatch, batch_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Delivery batch not found")
        item.product_type = payload.product_type
        item.quantity = payload.quantity
        item.delivery_date = delivery_date
        item.serial_numbers = payload.serial_numbers or ""
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/ledger/ci-delivery-batches/{batch_id}")
def delete_ci_delivery_batch(batch_id: int, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(CIDeliveryBatch, batch_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Delivery batch not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.post("/api/ledger/ci-deliveries")
def create_ci_delivery(payload: CiDeliveryCreateUpdate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        if session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.dealer_name)).first() is not None:
            raise HTTPException(status_code=409, detail="Dealer already exists")
        item = CiDealerDelivery(**payload.model_dump(exclude={"customer_company"}), customer_company=(payload.customer_company or payload.dealer_name).strip())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/ledger/ci-deliveries/{dealer_name}")
def update_ci_delivery(dealer_name: str, payload: CiDeliveryUpdate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == dealer_name)).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Dealer not found")
        item.region = payload.region
        item.customer_company = (payload.customer_company or payload.dealer_name).strip()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/ledger/ci-deliveries/{dealer_name}")
def delete_ci_delivery(dealer_name: str, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        item = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == dealer_name)).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Dealer not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/warehouse/summary")
def get_warehouse_summary(warehouse_name: str = Query(default="europe"), _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        inventory_items = session.exec(
            select(WarehouseInventory).where(WarehouseInventory.warehouse_name == warehouse_name)
        ).all()
        transactions = session.exec(
            select(WarehouseTransaction)
            .where(WarehouseTransaction.warehouse_name == warehouse_name)
            .order_by(WarehouseTransaction.id.desc())
            .limit(20)
        ).all()

    return {
        "warehouse_name": warehouse_name,
        "inventory": inventory_items,
        "grouped_inventory": serialize_inventory(inventory_items),
        "transactions": transactions,
    }


@app.post("/api/warehouse/transactions")
def create_warehouse_transaction(payload: WarehouseTransactionCreate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    with get_session() as session:
        delta = payload.quantity if payload.tx_type == "国内到货入库" else -payload.quantity
        inventory_item = apply_inventory_delta(session, payload.warehouse_name, payload.product_model, delta)
        transaction = WarehouseTransaction(
            tx_no=payload.tx_no,
            warehouse_name=payload.warehouse_name,
            tx_type=payload.tx_type,
            product_model=payload.product_model,
            product_name=inventory_item.product_name,
            quantity=payload.quantity,
            related_project=payload.related_project,
        )
        session.add(inventory_item)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)

    return {"message": "created", "item": transaction, "summary": get_warehouse_summary(payload.warehouse_name)}


@app.put("/api/warehouse/transactions/{tx_no}")
def update_warehouse_transaction(tx_no: str, payload: WarehouseTransactionUpdate, _: User = Depends(require_write_access)) -> Dict[str, object]:
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    with get_session() as session:
        transaction = session.exec(select(WarehouseTransaction).where(WarehouseTransaction.tx_no == tx_no)).first()
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        old_delta = transaction.quantity if transaction.tx_type == "国内到货入库" else -transaction.quantity
        apply_inventory_delta(session, transaction.warehouse_name, transaction.product_model, -old_delta)

        new_delta = payload.quantity if payload.tx_type == "国内到货入库" else -payload.quantity
        apply_inventory_delta(session, payload.warehouse_name, payload.product_model, new_delta)

        transaction.tx_no = payload.tx_no
        transaction.warehouse_name = payload.warehouse_name
        transaction.tx_type = payload.tx_type
        transaction.product_model = payload.product_model
        transaction.product_name = (
            session.exec(
                select(WarehouseInventory.product_name).where(
                    WarehouseInventory.warehouse_name == payload.warehouse_name,
                    WarehouseInventory.product_model == payload.product_model,
                )
            ).first()
            or transaction.product_name
        )
        transaction.quantity = payload.quantity
        transaction.related_project = payload.related_project
        session.add(transaction)
        session.commit()
        session.refresh(transaction)

    return {"message": "updated", "item": transaction, "summary": get_warehouse_summary(payload.warehouse_name)}


@app.delete("/api/warehouse/transactions/{tx_no}")
def delete_warehouse_transaction(tx_no: str, _: User = Depends(require_write_access)) -> Dict[str, object]:
    with get_session() as session:
        transaction = session.exec(select(WarehouseTransaction).where(WarehouseTransaction.tx_no == tx_no)).first()
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        delta = transaction.quantity if transaction.tx_type == "国内到货入库" else -transaction.quantity
        apply_inventory_delta(session, transaction.warehouse_name, transaction.product_model, -delta)
        session.delete(transaction)
        session.commit()
        return {"message": "deleted", "summary": get_warehouse_summary(transaction.warehouse_name)}
