from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class DeliveryCostProject(SQLModel, table=True):
    __tablename__ = "delivery_cost_projects"
    __table_args__ = (
        UniqueConstraint("project_type", "project_key", name="uq_delivery_cost_project_key"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    project_type: str = Field(index=True)
    project_key: str = Field(index=True)
    project_name: str = ""
    customer_name: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DeliveryCost(SQLModel, table=True):
    __tablename__ = "delivery_costs"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="delivery_cost_projects.id", index=True, unique=True)
    delivery_headcount: int = Field(default=0, ge=0)
    travel_cost: float = Field(default=0, ge=0)
    labor_cost: float = Field(default=0, ge=0)
    tool_cost: float = Field(default=0, ge=0)
    hardware_cost: float = Field(default=0, ge=0)
    travel_cost_note: str = ""
    labor_cost_note: str = ""
    tool_cost_note: str = ""
    hardware_cost_note: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AfterSalesCostEntry(SQLModel, table=True):
    __tablename__ = "after_sales_cost_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="delivery_cost_projects.id", index=True)
    event_date: Optional[date] = Field(default=None, index=True)
    reference: str = ""
    travel_cost: float = Field(default=0, ge=0)
    labor_cost: float = Field(default=0, ge=0)
    tool_cost: float = Field(default=0, ge=0)
    hardware_cost: float = Field(default=0, ge=0)
    travel_cost_note: str = ""
    labor_cost_note: str = ""
    tool_cost_note: str = ""
    hardware_cost_note: str = ""
    import_batch_id: str = Field(index=True)
    source_row: int = 0
    after_sales_log_id: Optional[int] = Field(
        default=None,
        foreign_key="after_sales_logs.id",
        index=True,
        unique=True,
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CostAssumption(SQLModel, table=True):
    __tablename__ = "delivery_cost_assumptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    default_amount: float = Field(default=0, ge=0)
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)