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


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    upgrade_users_schema()
    # create_all does not add columns to an existing SQLite database.
    with engine.begin() as connection:
        for table, column in (("gridscaleproject", "customer_id"), ("gridscaleproject", "partner_name"), ("gridscaleproject", "customer_company"), ("gridscaleproject", "software_version"), ("cidealerdelivery", "customer_id"), ("cidealerdelivery", "customer_company"), ("customer_tickets", "resolved_at"), ("customer_tickets", "expected_date"), ("customer_tickets", "customer_company"), ("customer_tickets", "serial_number"), ("after_sales_logs", "customer_company"), ("after_sales_logs", "fault_component"), ("logistics_shipments", "remarks"), ("logistics_shipments", "created_date"), ("logistics_shipments", "specific_module"), ("logistics_shipments", "stage")):
            try:
                column_type = "TEXT" if column in {"partner_name", "customer_company", "resolved_at", "fault_component", "software_version", "remarks", "created_date", "specific_module", "stage"} else "INTEGER"
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


def get_session() -> Session:
    return Session(engine, expire_on_commit=False)
