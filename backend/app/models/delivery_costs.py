from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import CheckConstraint, UniqueConstraint
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
    travel_cost: float = Field(default=0.0, ge=0)
    labor_cost: float = Field(default=0.0, ge=0)
    hardware_cost: float = Field(default=0.0, ge=0)
    meal_allowance: float = Field(default=0.0, ge=0)
    local_transport_cost: float = Field(default=0.0, ge=0)
    salary_cost: float = Field(default=0.0, ge=0)
    accommodation_cost: float = Field(default=0.0, ge=0)
    long_distance_cost: float = Field(default=0.0, ge=0)
    visa_cost: float = Field(default=0.0, ge=0)
    tool_cost: float = Field(default=0.0, ge=0)
    hardware_replacement_cost: float = Field(default=0.0, ge=0)
    total_man_days_note: str = Field(default="")
    per_day_cost_note: str = Field(default="")
    one_time_cost_note: str = Field(default="")
    total_cost_note: str = Field(default="")
    meal_allowance_note: str = Field(default="")
    local_transport_cost_note: str = Field(default="")
    salary_cost_note: str = Field(default="")
    accommodation_cost_note: str = Field(default="")
    long_distance_cost_note: str = Field(default="")
    visa_cost_note: str = Field(default="")
    tool_cost_note: str = Field(default="")
    hardware_replacement_cost_note: str = Field(default="")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AfterSalesCostEntry(SQLModel, table=True):
    __tablename__ = "after_sales_cost_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="delivery_cost_projects.id", index=True)
    event_date: Optional[date] = Field(default=None, index=True)
    reference: str = ""
    travel_cost: float = Field(default=0.0, ge=0)
    labor_cost: float = Field(default=0.0, ge=0)
    hardware_cost: float = Field(default=0.0, ge=0)
    travel_cost_note: str = Field(default="")
    labor_cost_note: str = Field(default="")
    hardware_cost_note: str = Field(default="")
    meal_allowance: float = Field(default=0.0, ge=0)
    local_transport_cost: float = Field(default=0.0, ge=0)
    salary_cost: float = Field(default=0.0, ge=0)
    accommodation_cost: float = Field(default=0.0, ge=0)
    long_distance_cost: float = Field(default=0.0, ge=0)
    visa_cost: float = Field(default=0.0, ge=0)
    tool_cost: float = Field(default=0.0, ge=0)
    hardware_replacement_cost: float = Field(default=0.0, ge=0)
    total_man_days_note: str = Field(default="")
    per_day_cost_note: str = Field(default="")
    one_time_cost_note: str = Field(default="")
    total_cost_note: str = Field(default="")
    meal_allowance_note: str = Field(default="")
    local_transport_cost_note: str = Field(default="")
    salary_cost_note: str = Field(default="")
    accommodation_cost_note: str = Field(default="")
    long_distance_cost_note: str = Field(default="")
    visa_cost_note: str = Field(default="")
    tool_cost_note: str = Field(default="")
    hardware_replacement_cost_note: str = Field(default="")
    import_batch_id: str = Field(index=True)
    source_row: int = 0
    after_sales_log_id: Optional[int] = Field(
        default=None,
        foreign_key="after_sales_logs.id",
        index=True,
        unique=True,
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CostPersonDay(SQLModel, table=True):
    __tablename__ = "delivery_cost_person_days"
    __table_args__ = (
        CheckConstraint(
            "(delivery_cost_id IS NOT NULL AND after_sales_cost_entry_id IS NULL) OR "
            "(delivery_cost_id IS NULL AND after_sales_cost_entry_id IS NOT NULL)",
            name="ck_cost_person_day_single_parent",
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    delivery_cost_id: Optional[int] = Field(default=None, foreign_key="delivery_costs.id", index=True)
    after_sales_cost_entry_id: Optional[int] = Field(default=None, foreign_key="after_sales_cost_entries.id", index=True)
    person_name: str
    days: float = Field(default=0, ge=0)
    note: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FixedCostEntry(SQLModel, table=True):
    __tablename__ = "delivery_fixed_cost_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str = Field(index=True)
    name: str
    daily_price: float = Field(default=0, ge=0)
    start_date: date
    end_date: date
    total_days: int = Field(default=1, ge=1)
    total_price: float = Field(default=0, ge=0)
    note: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CostAssumption(SQLModel, table=True):
    __tablename__ = "delivery_cost_assumptions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    default_amount: float = Field(default=0, ge=0)
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)