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
        for table, column in (("gridscaleproject", "customer_id"), ("gridscaleproject", "partner_name"), ("gridscaleproject", "customer_company"), ("gridscaleproject", "software_version"), ("cidealerdelivery", "customer_id"), ("cidealerdelivery", "customer_company"), ("customer_tickets", "resolved_at"), ("customer_tickets", "expected_date"), ("customer_tickets", "customer_company"), ("customer_tickets", "serial_number"), ("after_sales_logs", "customer_company"), ("after_sales_logs", "fault_component"), ("logistics_shipments", "remarks")):
            try:
                column_type = "TEXT" if column in {"partner_name", "customer_company", "resolved_at", "fault_component", "software_version", "remarks"} else "INTEGER"
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
            except Exception:
                pass
        connection.execute(
            text(
                "UPDATE gridscaleproject "
                "SET software_version = COALESCE(NULLIF(software_version, ''), cell_version, '')"
            )
        )


def get_session() -> Session:
    return Session(engine, expire_on_commit=False)
