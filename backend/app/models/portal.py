from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy import JSON as SAJSON
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    country: str = ""
    role: str = Field(default="customer", index=True)
    is_staff: bool = False
    project_ids: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FaultComponent(SQLModel, table=True):
    __tablename__ = "fault_components"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    name_en: str = ""
    sort_order: int = Field(default=0, index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LogisticsStatus(SQLModel, table=True):
    __tablename__ = "logistics_statuses"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    name_en: str = ""
    step_order: int = Field(default=0, index=True)
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectMilestone(SQLModel, table=True):
    __tablename__ = "milestones"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str = Field(index=True)
    milestone_key: str = Field(index=True)
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: str = Field(default="待开始")
    notes: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AfterSalesLog(SQLModel, table=True):
    __tablename__ = "after_sales_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_date: date
    country: str
    customer: str
    customer_company: str = ""
    project_name: str = Field(index=True)
    product_model: str
    support_type: str
    issue_category: str
    faulty_component: str
    fault_component: str = ""
    fault_description: str = ""
    onsite_solution: str = ""
    serial_number: str = ""
    status: str = "处理中 (Pending)"
    pending_reason: str = ""
    created_by: str
    attachments: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))
    customer_id: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerTicket(SQLModel, table=True):
    __tablename__ = "customer_tickets"

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: int = Field(index=True)
    customer_name: str
    customer_company: str = ""
    submit_time: datetime = Field(default_factory=datetime.utcnow)
    project_name: str = Field(index=True)
    serial_number: str
    product_model: str
    ticket_type: str
    suspected_scope: str
    suspected_component: str
    description: str
    attachments: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))
    expected_resolution_date: Optional[date] = None
    expected_date: Optional[date] = None
    contact: str
    status: str = Field(default="待处理 (Pending)")
    staff_reply: str = ""
    resolved_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LogisticsShipment(SQLModel, table=True):
    __tablename__ = "logistics_shipments"

    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_no: str = Field(index=True, unique=True)
    created_date: date = Field(default_factory=date.today, index=True)
    stage: str = Field(default="delivery", index=True)
    customer_company: str = Field(default="", index=True)
    related_project: str = Field(default="", index=True)
    destination_country: str = ""
    destination_port: str = ""
    container_no: str = ""
    equipment_model: str = ""
    specific_module: str = ""
    equipment_qty: int = 0
    status: str = Field(default="工厂备货")
    eta: Optional[date] = None
    ata: Optional[date] = None
    carrier: str = ""
    tracking_url: str = ""
    remarks: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmpowermentSkill(SQLModel, table=True):
    __tablename__ = "empowerment_skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    name_en: str = ""
    sort_order: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EmpowermentRecord(SQLModel, table=True):
    __tablename__ = "empowerment_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    partner_name: str = Field(index=True, unique=True)
    delivery_418_net: int = 0
    delivery_418_soft: int = 0
    delivery_250_net: int = 0
    delivery_250_soft: int = 0
    delivery_100c_net: int = 0
    delivery_100c_soft: int = 0
    aftersales_scores: Dict[str, int] = Field(default_factory=dict, sa_column=Column(SAJSON))
    remarks: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)