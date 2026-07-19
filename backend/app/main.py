from __future__ import annotations

from collections import defaultdict
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

from .database import get_session, init_db
from .models.ledger import (
    CI_DELIVERY_SEED,
    FAULT_CODE_SEED,
    GRID_SCALE_PROJECT_SEED,
    WAREHOUSE_INVENTORY_SEED,
    WAREHOUSE_TRANSACTION_SEED,
    CiDealerDelivery,
    FaultCode,
    GridScaleProject,
    WarehouseInventory,
    WarehouseTransaction,
)


class FaultCodeRecord(BaseModel):
    fault_code: str
    fault_name: str
    possible_causes: str
    solution: str


class GridScaleStatusUpdate(BaseModel):
    progress_status: str


class CiDeliveryUpdate(BaseModel):
    region: str
    delivered_100c: int
    delivered_250: int


class WarehouseTransactionCreate(BaseModel):
    warehouse_name: str
    tx_type: Literal["国内到货入库", "现场客诉领用出库"]
    product_model: str
    quantity: int
    related_project: str
    tx_no: str


app = FastAPI(
    title="JD Energy Service Portal API",
    version="2.0.0",
    description="Fault lookup, project ledger, C&I deliveries, and warehouse inventory APIs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
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
        session.commit()


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


def serialize_inventory(rows: list[WarehouseInventory]) -> dict[str, list[WarehouseInventory]]:
    grouped: dict[str, list[WarehouseInventory]] = defaultdict(list)
    for row in rows:
        grouped[row.category].append(row)
    return grouped


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "JD Energy Service Portal API"}


@app.get("/api/fault-codes")
def get_fault_codes(q: str = Query(default="", description="Fault code or keyword search term")) -> dict[str, object]:
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


@app.get("/api/ledger/grid-scale")
def list_grid_scale_projects() -> dict[str, object]:
    with get_session() as session:
        items = session.exec(select(GridScaleProject)).all()
    return {"count": len(items), "items": items}


@app.post("/api/ledger/grid-scale/{project_name}/status")
def update_grid_scale_status(project_name: str, payload: GridScaleStatusUpdate) -> dict[str, object]:
    with get_session() as session:
        project = session.get(GridScaleProject, project_name)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        project.progress_status = payload.progress_status
        session.add(project)
        session.commit()
        session.refresh(project)
        return {"message": "updated", "item": project}


@app.get("/api/ledger/ci-deliveries")
def list_ci_deliveries() -> dict[str, object]:
    with get_session() as session:
        items = session.exec(select(CiDealerDelivery)).all()
    return {"count": len(items), "items": items}


@app.post("/api/ledger/ci-deliveries/{dealer_name}")
def update_ci_delivery(dealer_name: str, payload: CiDeliveryUpdate) -> dict[str, object]:
    with get_session() as session:
        item = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == dealer_name)).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Dealer not found")
        item.region = payload.region
        item.delivered_100c = payload.delivered_100c
        item.delivered_250 = payload.delivered_250
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.get("/api/warehouse/summary")
def get_warehouse_summary(warehouse_name: str = Query(default="europe")) -> dict[str, object]:
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
def create_warehouse_transaction(payload: WarehouseTransactionCreate) -> dict[str, object]:
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    with get_session() as session:
        inventory_item = session.exec(
            select(WarehouseInventory).where(
                WarehouseInventory.warehouse_name == payload.warehouse_name,
                WarehouseInventory.product_model == payload.product_model,
            )
        ).first()

        if inventory_item is None:
            raise HTTPException(status_code=404, detail="Inventory item not found")

        delta = payload.quantity if payload.tx_type == "国内到货入库" else -payload.quantity
        next_quantity = inventory_item.quantity + delta
        if next_quantity < 0:
            raise HTTPException(status_code=400, detail="Inventory would become negative")

        inventory_item.quantity = next_quantity
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
