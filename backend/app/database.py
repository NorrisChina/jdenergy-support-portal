from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import text


BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = BACKEND_ROOT / "storage.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    # create_all does not add columns to an existing SQLite database.
    with engine.begin() as connection:
        for table, column in (("users", "customer_company"), ("users", "is_staff"), ("gridscaleproject", "customer_id"), ("gridscaleproject", "partner_name"), ("gridscaleproject", "customer_company"), ("cidealerdelivery", "customer_id"), ("cidealerdelivery", "customer_company"), ("customer_tickets", "resolved_at"), ("customer_tickets", "expected_date"), ("customer_tickets", "customer_company"), ("customer_tickets", "serial_number"), ("after_sales_logs", "customer_company"), ("after_sales_logs", "fault_component")):
            try:
                column_type = "TEXT" if column in {"partner_name", "customer_company", "resolved_at", "fault_component"} else "INTEGER"
                connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"))
            except Exception:
                pass


def get_session() -> Session:
    return Session(engine, expire_on_commit=False)
