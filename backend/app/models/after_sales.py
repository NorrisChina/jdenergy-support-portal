from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class FaultCode(SQLModel, table=True):
    __tablename__ = "after_sales_fault_codes"

    id: Optional[int] = Field(default=None, primary_key=True)
    module: str = Field(index=True)
    fault_code: str = Field(index=True)
    fault_name: str
    fault_level: str
    is_stop: str
    recovery: str
    detection_condition: str
    trigger_logic: str
    possible_cause: str
    solution: str