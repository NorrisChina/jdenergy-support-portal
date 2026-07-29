from __future__ import annotations

import os
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
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
    WarehouseInventoryItem,
    WarehouseTransaction,
    WAREHOUSE_INVENTORY_ITEM_SEED,
)


class FaultCodeRecord(BaseModel):
    fault_code: str
    fault_name: str
    possible_causes: str
    solution: str


class FaultCodeUpsert(BaseModel):
    fault_name: str
    possible_causes: str
    solution: str


class GridScaleStatusUpdate(BaseModel):
    progress_status: str


class GridScaleProjectUpsert(BaseModel):
    project_name: str
    cod: str
    capacity_mwh: float
    cell_version: str
    pcs_model: str
    progress_status: str
    photo_paths: list[str]


class CiDeliveryUpdate(BaseModel):
    region: str
    delivered_100c: int
    delivered_250: int


class CiDeliveryCreateUpdate(CiDeliveryUpdate):
    dealer_name: str


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
    photo_paths: list[str] = Field(default_factory=list)
    remarks: Optional[str] = None


class WarehouseInventoryItemUpdate(BaseModel):
    description_zh: str
    specification: str
    total_quantity: int = 0
    damaged_quantity: int = 0
    available_quantity: Optional[int] = None
    photo_paths: list[str] = Field(default_factory=list)
    remarks: Optional[str] = None


app = FastAPI(
    title="JD Energy Service Portal API",
    version="2.0.0",
    description="Fault lookup, project ledger, C&I deliveries, and warehouse inventory APIs.",
)

BACKEND_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_ROOT / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static_uploads", StaticFiles(directory=UPLOAD_DIR), name="static_uploads")

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
        if session.exec(select(WarehouseInventoryItem)).first() is None:
            session.add_all(WAREHOUSE_INVENTORY_ITEM_SEED)
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


@app.post("/api/fault-codes")
def create_fault_code(payload: FaultCodeRecord) -> dict[str, object]:
    with get_session() as session:
        if session.get(FaultCode, payload.fault_code) is not None:
                        raise HTTPException(status_code=409, detail="Fault code already exists")
        item = FaultCode(**payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
        original_suffix = Path(file.filename or "").suffix or ".bin"
        new_filename = f"{uuid.uuid4().hex}{original_suffix}"
        file_path = UPLOAD_DIR / new_filename
        contents = await file.read()
        file_path.write_bytes(contents)
        return {"url": f"/static_uploads/{new_filename}"}


@app.put("/api/fault-codes/{fault_code}")
def update_fault_code(fault_code: str, payload: FaultCodeUpsert) -> dict[str, object]:
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
def delete_fault_code(fault_code: str) -> dict[str, object]:
    with get_session() as session:
        item = session.get(FaultCode, fault_code)
        if item is None:
            raise HTTPException(status_code=404, detail="Fault code not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/ledger/grid-scale")
def list_grid_scale_projects() -> dict[str, object]:
    with get_session() as session:
        items = session.exec(select(GridScaleProject)).all()
    return {"count": len(items), "items": items}


@app.post("/api/ledger/grid-scale")
def create_grid_scale_project(payload: GridScaleProjectUpsert) -> dict[str, object]:
    with get_session() as session:
        if session.get(GridScaleProject, payload.project_name) is not None:
            raise HTTPException(status_code=409, detail="Project already exists")
        item = GridScaleProject(**payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/ledger/grid-scale/{project_name}")
def update_grid_scale_project(project_name: str, payload: GridScaleProjectUpsert) -> dict[str, object]:
    with get_session() as session:
        item = session.get(GridScaleProject, project_name)
        if item is None:
            raise HTTPException(status_code=404, detail="Project not found")
        item.cod = payload.cod
        item.capacity_mwh = payload.capacity_mwh
        item.cell_version = payload.cell_version
        item.pcs_model = payload.pcs_model
        item.progress_status = payload.progress_status
        item.photo_paths = payload.photo_paths
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


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


@app.delete("/api/ledger/grid-scale/{project_name}")
def delete_grid_scale_project(project_name: str) -> dict[str, object]:
    with get_session() as session:
        item = session.get(GridScaleProject, project_name)
        if item is None:
            raise HTTPException(status_code=404, detail="Project not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/warehouse/inventory")
def list_warehouse_inventory_items() -> dict[str, object]:
    with get_session() as session:
        items = session.exec(select(WarehouseInventoryItem)).all()
    return {"count": len(items), "items": items}


@app.post("/api/warehouse/inventory")
def create_warehouse_inventory_item(payload: WarehouseInventoryItemCreate) -> dict[str, object]:
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


@app.put("/api/warehouse/inventory/{item_no}")
def update_warehouse_inventory_item(item_no: str, payload: WarehouseInventoryItemUpdate) -> dict[str, object]:
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


@app.delete("/api/warehouse/inventory/{item_no}")
def delete_warehouse_inventory_item(item_no: str) -> dict[str, object]:
    with get_session() as session:
        item = session.get(WarehouseInventoryItem, item_no)
        if item is None:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/ledger/ci-deliveries")
def list_ci_deliveries() -> dict[str, object]:
    with get_session() as session:
        items = session.exec(select(CiDealerDelivery)).all()
    return {"count": len(items), "items": items}


@app.post("/api/ledger/ci-deliveries")
def create_ci_delivery(payload: CiDeliveryCreateUpdate) -> dict[str, object]:
    with get_session() as session:
        if session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.dealer_name)).first() is not None:
            raise HTTPException(status_code=409, detail="Dealer already exists")
        item = CiDealerDelivery(**payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/ledger/ci-deliveries/{dealer_name}")
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


@app.delete("/api/ledger/ci-deliveries/{dealer_name}")
def delete_ci_delivery(dealer_name: str) -> dict[str, object]:
    with get_session() as session:
        item = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == dealer_name)).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Dealer not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


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
def update_warehouse_transaction(tx_no: str, payload: WarehouseTransactionUpdate) -> dict[str, object]:
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
def delete_warehouse_transaction(tx_no: str) -> dict[str, object]:
    with get_session() as session:
        transaction = session.exec(select(WarehouseTransaction).where(WarehouseTransaction.tx_no == tx_no)).first()
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        delta = transaction.quantity if transaction.tx_type == "国内到货入库" else -transaction.quantity
        apply_inventory_delta(session, transaction.warehouse_name, transaction.product_model, -delta)
        session.delete(transaction)
        session.commit()
        return {"message": "deleted", "summary": get_warehouse_summary(transaction.warehouse_name)}
