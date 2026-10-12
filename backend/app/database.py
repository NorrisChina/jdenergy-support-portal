from __future__ import annotations

import logging
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import text


BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = BACKEND_ROOT / "storage.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
logger = logging.getLogger(__name__)

USER_COLUMN_MIGRATIONS = {
    "customer_name": "TEXT",
    "customer_company": "TEXT DEFAULT ''",
    "country": "TEXT DEFAULT ''",
    "role": "TEXT DEFAULT 'customer'",
    "is_staff": "INTEGER NOT NULL DEFAULT 0",
    "project_ids": "JSON DEFAULT '[]'",
    "is_active": "INTEGER NOT NULL DEFAULT 1",
    "created_at": "DATETIME",
}

VPN_SITE_COLUMN_MIGRATIONS = {
    "port": "INTEGER NOT NULL DEFAULT 22",
    "username": "TEXT NOT NULL DEFAULT 'root'",
    "password": "TEXT NOT NULL DEFAULT ''",
    "use_jump_host": "INTEGER NOT NULL DEFAULT 0",
    "jump_host_ip": "TEXT NOT NULL DEFAULT ''",
    "jump_host_port": "INTEGER NOT NULL DEFAULT 22",
    "jump_host_user": "TEXT NOT NULL DEFAULT 'root'",
    "jump_host_password": "TEXT NOT NULL DEFAULT ''",
    "use_stormshield": "INTEGER NOT NULL DEFAULT 0",
    "stormshield_server": "TEXT NOT NULL DEFAULT ''",
    "stormshield_user": "TEXT NOT NULL DEFAULT ''",
    "stormshield_password": "TEXT NOT NULL DEFAULT ''",
}

VPN_EXPORT_TASK_COLUMN_MIGRATIONS = {
    "progress": "INTEGER NOT NULL DEFAULT 0",
    "current_log": "TEXT NOT NULL DEFAULT ''",
}


def upgrade_users_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as connection:
        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(users)"))
        }
        for column, definition in USER_COLUMN_MIGRATIONS.items():
            if column in existing_columns:
                continue
            connection.execute(
                text(f'ALTER TABLE users ADD COLUMN "{column}" {definition}')
            )
            logger.info("Added missing users.%s column.", column)


def upgrade_vpn_sites_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as connection:
        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(vpn_sites)"))
        }
        for column, definition in VPN_SITE_COLUMN_MIGRATIONS.items():
            if column in existing_columns:
                continue
            connection.execute(
                text(f'ALTER TABLE vpn_sites ADD COLUMN "{column}" {definition}')
            )
            logger.info("Added missing vpn_sites.%s column.", column)


def upgrade_vpn_export_tasks_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as connection:
        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(vpn_export_tasks)"))
        }
        for column, definition in VPN_EXPORT_TASK_COLUMN_MIGRATIONS.items():
            if column in existing_columns:
                continue
            connection.execute(
                text(f'ALTER TABLE vpn_export_tasks ADD COLUMN "{column}" {definition}')
            )
            logger.info("Added missing vpn_export_tasks.%s column.", column)


def upgrade_delivery_cost_schema() -> None:
    if engine.dialect.name != "sqlite":
        return

    cost_columns = {
        "meal_allowance": "REAL NOT NULL DEFAULT 0",
        "local_transport_cost": "REAL NOT NULL DEFAULT 0",
        "salary_cost": "REAL NOT NULL DEFAULT 0",
        "accommodation_cost": "REAL NOT NULL DEFAULT 0",
        "long_distance_cost": "REAL NOT NULL DEFAULT 0",
        "visa_cost": "REAL NOT NULL DEFAULT 0",
        "hardware_replacement_cost": "REAL NOT NULL DEFAULT 0",
        "total_man_days_note": "TEXT NOT NULL DEFAULT ''",
        "per_day_cost_note": "TEXT NOT NULL DEFAULT ''",
        "one_time_cost_note": "TEXT NOT NULL DEFAULT ''",
        "meal_allowance_note": "TEXT NOT NULL DEFAULT ''",
        "local_transport_cost_note": "TEXT NOT NULL DEFAULT ''",
        "salary_cost_note": "TEXT NOT NULL DEFAULT ''",
        "accommodation_cost_note": "TEXT NOT NULL DEFAULT ''",
        "long_distance_cost_note": "TEXT NOT NULL DEFAULT ''",
        "visa_cost_note": "TEXT NOT NULL DEFAULT ''",
        "tool_cost_note": "TEXT NOT NULL DEFAULT ''",
        "hardware_replacement_cost_note": "TEXT NOT NULL DEFAULT ''",
    }
    legacy_cost_mapping = {
        "travel_cost": "long_distance_cost",
        "labor_cost": "salary_cost",
        "hardware_cost": "hardware_replacement_cost",
    }
    legacy_note_mapping = {
        "travel_cost_note": "long_distance_cost_note",
        "labor_cost_note": "salary_cost_note",
        "hardware_cost_note": "hardware_replacement_cost_note",
    }

    with engine.begin() as connection:
        for table in ("delivery_costs", "after_sales_cost_entries"):
            existing_columns = {
                row[1] for row in connection.execute(text(f'PRAGMA table_info("{table}")'))
            }
            if "tool_cost" not in existing_columns:
                connection.execute(text(f'ALTER TABLE "{table}" ADD COLUMN tool_cost REAL NOT NULL DEFAULT 0'))
                existing_columns.add("tool_cost")
                logger.info("Added %s.tool_cost column.", table)
            for column, definition in cost_columns.items():
                if column not in existing_columns:
                    connection.execute(
                        text(f'ALTER TABLE "{table}" ADD COLUMN "{column}" {definition}')
                    )
                    existing_columns.add(column)
                    logger.info("Added %s.%s column.", table, column)
            for legacy_column, target_column in legacy_cost_mapping.items():
                if legacy_column in existing_columns:
                    connection.execute(
                        text(
                            f'UPDATE "{table}" SET "{target_column}" = '
                            f'CASE WHEN COALESCE("{target_column}", 0) = 0 '
                            f'THEN COALESCE("{legacy_column}", 0) ELSE "{target_column}" END, '
                            f'"{legacy_column}" = 0'
                        )
                    )


def upgrade_fixed_cost_schema() -> None:
    if engine.dialect.name != "sqlite":
        return
    with engine.begin() as connection:
        table_exists = connection.execute(
            text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'delivery_fixed_cost_entries'")
        ).first()
        if not table_exists:
            return

        table_info = connection.execute(text('PRAGMA table_info("delivery_fixed_cost_entries")')).all()
        existing_columns = {row[1] for row in table_info}
        project_id_info = next((row for row in table_info if row[1] == "project_id"), None)
        requires_customer_migration = "customer_name" not in existing_columns or (
            project_id_info is not None and bool(project_id_info[3])
        )
        if requires_customer_migration:
            backup_table = "delivery_fixed_cost_entries_project_legacy"
            suffix = 1
            while connection.execute(
                text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = :name"),
                {"name": backup_table},
            ).first():
                suffix += 1
                backup_table = f"delivery_fixed_cost_entries_project_legacy_{suffix}"
            connection.execute(
                text(f'ALTER TABLE delivery_fixed_cost_entries RENAME TO "{backup_table}"')
            )
            connection.execute(
                text(
                    "CREATE TABLE delivery_fixed_cost_entries ("
                    "id INTEGER NOT NULL PRIMARY KEY, customer_name TEXT NOT NULL, name TEXT NOT NULL, "
                    "daily_price REAL NOT NULL DEFAULT 0, start_date DATE NOT NULL, end_date DATE NOT NULL, "
                    "total_days INTEGER NOT NULL DEFAULT 1, total_price REAL NOT NULL DEFAULT 0, "
                    "note TEXT NOT NULL DEFAULT '', created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL)"
                )
            )
            legacy_columns = {row[1] for row in connection.execute(text(f'PRAGMA table_info("{backup_table}")'))}
            table_names = {
                row[0] for row in connection.execute(text("SELECT name FROM sqlite_master WHERE type = 'table'")).all()
            }
            if "project_id" in legacy_columns and "delivery_cost_projects" in table_names:
                if "gridscaleproject" in table_names:
                    customer_expression = (
                        "CASE WHEN p.project_type = '418' THEN "
                        "COALESCE(NULLIF(g.customer_company, ''), NULLIF(g.partner_name, ''), "
                        "NULLIF(p.customer_name, ''), '') "
                        "ELSE COALESCE(NULLIF(p.customer_name, ''), '') END"
                    )
                    project_join = (
                        'LEFT JOIN delivery_cost_projects p ON p.id = f.project_id '
                        "LEFT JOIN gridscaleproject g ON g.project_name = p.project_name"
                    )
                else:
                    customer_expression = "COALESCE(NULLIF(p.customer_name, ''), '')"
                    project_join = 'LEFT JOIN delivery_cost_projects p ON p.id = f.project_id'
            else:
                customer_expression = "''"
                project_join = ""
            connection.execute(
                text(
                    f'INSERT INTO delivery_fixed_cost_entries '
                    f'(id, customer_name, name, daily_price, start_date, end_date, total_days, total_price, note, created_at, updated_at) '
                    f'SELECT f.id, {customer_expression}, f.name, f.daily_price, f.start_date, f.end_date, '
                    f'f.total_days, f.total_price, f.note, f.created_at, f.updated_at '
                    f'FROM "{backup_table}" f {project_join}'
                )
            )
            connection.execute(
                text("CREATE INDEX ix_delivery_fixed_cost_entries_customer_name ON delivery_fixed_cost_entries (customer_name)")
            )
            logger.info("Migrated fixed costs from project scope to customer scope; legacy rows preserved in %s.", backup_table)
        elif "ix_delivery_fixed_cost_entries_customer_name" not in {
            row[1] for row in connection.execute(text("PRAGMA index_list('delivery_fixed_cost_entries')"))
        }:
            connection.execute(
                text("CREATE INDEX ix_delivery_fixed_cost_entries_customer_name ON delivery_fixed_cost_entries (customer_name)")
            )


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    upgrade_users_schema()
    upgrade_vpn_sites_schema()
    upgrade_vpn_export_tasks_schema()
    upgrade_delivery_cost_schema()
    upgrade_fixed_cost_schema()
    # create_all does not add columns to an existing SQLite database.
    with engine.begin() as connection:
        for table, column in (("gridscaleproject", "customer_id"), ("gridscaleproject", "partner_name"), ("gridscaleproject", "customer_company"), ("gridscaleproject", "software_version"), ("cidealerdelivery", "customer_id"), ("cidealerdelivery", "customer_company"), ("customer_tickets", "resolved_at"), ("customer_tickets", "expected_date"), ("customer_tickets", "customer_company"), ("customer_tickets", "serial_number"), ("after_sales_logs", "customer_company"), ("after_sales_logs", "fault_component"), ("after_sales_logs", "serial_number"), ("after_sales_logs", "rd_contact"), ("logistics_shipments", "remarks"), ("logistics_shipments", "created_date"), ("logistics_shipments", "specific_module"), ("logistics_shipments", "stage")):
            try:
                column_type = "TEXT" if column in {"partner_name", "customer_company", "resolved_at", "fault_component", "serial_number", "rd_contact", "software_version", "remarks", "created_date", "specific_module", "stage"} else "INTEGER"
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
            except Exception:
                pass
        grid_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(gridscaleproject)"))
        }
        if "id" not in grid_columns:
            connection.execute(text("ALTER TABLE gridscaleproject ADD COLUMN id INTEGER"))
            connection.execute(text("UPDATE gridscaleproject SET id = rowid WHERE id IS NULL"))
            logger.info("Added and backfilled gridscaleproject.id.")
        empowerment_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(empowerment_records)"))
        }
        legacy_empowerment_columns = {"delivery_250", "delivery_100c", "delivery_418", "troubleshooting", "spare_parts", "learning_ability", "learning_willingness"}
        if empowerment_columns & legacy_empowerment_columns:
            backup_table = "empowerment_records_legacy"
            suffix = 1
            while connection.execute(text("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = :name"), {"name": backup_table}).first():
                suffix += 1
                backup_table = f"empowerment_records_legacy_{suffix}"
            connection.execute(text(f'ALTER TABLE empowerment_records RENAME TO "{backup_table}"'))
            connection.execute(text("CREATE TABLE empowerment_records (id INTEGER PRIMARY KEY, partner_name TEXT NOT NULL UNIQUE, delivery_418_net INTEGER NOT NULL DEFAULT 0, delivery_418_soft INTEGER NOT NULL DEFAULT 0, delivery_250_net INTEGER NOT NULL DEFAULT 0, delivery_250_soft INTEGER NOT NULL DEFAULT 0, delivery_100c_net INTEGER NOT NULL DEFAULT 0, delivery_100c_soft INTEGER NOT NULL DEFAULT 0, aftersales_scores JSON NOT NULL DEFAULT '{}', remarks TEXT NOT NULL DEFAULT '', updated_at DATETIME NOT NULL)"))
            legacy_scores = "json_object('PCS更换', COALESCE(spare_parts, 0), '水机更换', COALESCE(spare_parts, 0), '问题定位', COALESCE(troubleshooting, 0))"
            scores_expression = f"CASE WHEN aftersales_scores IS NULL OR aftersales_scores = '' OR aftersales_scores = '{{}}' THEN {legacy_scores} ELSE aftersales_scores END" if "aftersales_scores" in empowerment_columns else legacy_scores
            connection.execute(text(f"INSERT INTO empowerment_records (id, partner_name, delivery_418_net, delivery_418_soft, delivery_250_net, delivery_250_soft, delivery_100c_net, delivery_100c_soft, aftersales_scores, remarks, updated_at) SELECT id, partner_name, COALESCE(delivery_418, 0), COALESCE(delivery_418, 0), COALESCE(delivery_250, 0), COALESCE(delivery_250, 0), COALESCE(delivery_100c, 0), COALESCE(delivery_100c, 0), {scores_expression}, COALESCE(remarks, ''), updated_at FROM \"{backup_table}\""))
            empowerment_columns = {
                row[1] for row in connection.execute(text("PRAGMA table_info(empowerment_records)"))
            }
            logger.info("Migrated empowerment_records to dynamic skill schema; legacy data preserved in %s.", backup_table)
        for column, definition in {
            "delivery_418_net": "INTEGER DEFAULT 0",
            "delivery_418_soft": "INTEGER DEFAULT 0",
            "delivery_250_net": "INTEGER DEFAULT 0",
            "delivery_250_soft": "INTEGER DEFAULT 0",
            "delivery_100c_net": "INTEGER DEFAULT 0",
            "delivery_100c_soft": "INTEGER DEFAULT 0",
            "aftersales_scores": "JSON DEFAULT '{}'",
        }.items():
            if column not in empowerment_columns:
                connection.execute(text(f'ALTER TABLE empowerment_records ADD COLUMN "{column}" {definition}'))
        connection.execute(
            text(
                "UPDATE gridscaleproject "
                "SET software_version = COALESCE(NULLIF(software_version, ''), cell_version, '')"
            )
        )
        connection.execute(
            text(
                "UPDATE logistics_shipments "
                "SET created_date = COALESCE(NULLIF(created_date, ''), DATE(created_at), DATE('now'))"
            )
        )
        connection.execute(
            text(
                "UPDATE logistics_shipments "
                "SET stage = COALESCE(NULLIF(stage, ''), 'delivery')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO ci_delivery_batches "
                "(dealer_id, product_type, quantity, delivery_date, serial_numbers, created_at) "
                "SELECT d.id, '100C', d.delivered_100c, DATE('now'), '', DATETIME('now') "
                "FROM cidealerdelivery d "
                "WHERE d.delivered_100c > 0 "
                "AND NOT EXISTS (SELECT 1 FROM ci_delivery_batches b WHERE b.dealer_id = d.id AND b.product_type = '100C')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO ci_delivery_batches "
                "(dealer_id, product_type, quantity, delivery_date, serial_numbers, created_at) "
                "SELECT d.id, '250', d.delivered_250, DATE('now'), '', DATETIME('now') "
                "FROM cidealerdelivery d "
                "WHERE d.delivered_250 > 0 "
                "AND NOT EXISTS (SELECT 1 FROM ci_delivery_batches b WHERE b.dealer_id = d.id AND b.product_type = '250')"
            )
        )


def get_session() -> Session:
    return Session(engine, expire_on_commit=False)
