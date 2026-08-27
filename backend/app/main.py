from __future__ import annotations

import os
import json
import uuid
import mimetypes
import base64
import csv
import hashlib
import hmac
import io
import time
from datetime import date, datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from fastapi import APIRouter, Body, Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import or_
from sqlmodel import select

from .database import get_session, init_db
from .models.after_sales import FaultCode as AfterSalesFaultCode
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
from .models.technical_docs import (
    TECHNICAL_DOCS_SEED,
    TECHNICAL_DOC_CATEGORIES,
    TECHNICAL_DOC_PRODUCT_SERIES,
    TechnicalDoc,
)
from .models.portal import AfterSalesLog, CustomerTicket, ProjectMilestone, User


FAULTY_COMPONENT_OPTIONS = ("PACK", "Chiller", "PCS", "eLink", "Cabinet", "Software", "Transformer", "Other")


class FaultCodeRecord(BaseModel):
    fault_code: str
    fault_name: str
    possible_causes: str
    solution: str


class FaultCodeUpsert(BaseModel):
    fault_name: str
    possible_causes: str
    solution: str


class AfterSalesFaultCodeItem(BaseModel):
    module: str
    fault_code: str
    fault_name: str = ""
    fault_level: str = ""
    is_stop: str = ""
    recovery: str = ""
    detection_condition: str = ""
    trigger_logic: str = ""
    possible_cause: str = ""
    solution: str = ""


class AfterSalesFaultCodeImportPayload(BaseModel):
    items: List[AfterSalesFaultCodeItem]


class AfterSalesFaultCodeCreate(BaseModel):
    module: str
    fault_code: str
    fault_name: str = ""
    fault_level: str = ""
    is_stop: str = ""
    recovery: str = ""
    detection_condition: str = ""
    trigger_logic: str = ""
    possible_cause: str = ""
    solution: str = ""


class AfterSalesFaultCodeUpdate(BaseModel):
    module: Optional[str] = None
    fault_code: Optional[str] = None
    fault_name: Optional[str] = None
    fault_level: Optional[str] = None
    is_stop: Optional[str] = None
    recovery: Optional[str] = None
    detection_condition: Optional[str] = None
    trigger_logic: Optional[str] = None
    possible_cause: Optional[str] = None
    solution: Optional[str] = None


class GridScaleStatusUpdate(BaseModel):
    progress_status: str


class GridScaleProjectUpsert(BaseModel):
    project_name: str
    cod: str
    capacity_mwh: float
    cell_version: str
    pcs_model: str
    progress_status: str
    photo_paths: List[str]
    partner_name: str = ""
    customer_company: str = ""


class CiDeliveryUpdate(BaseModel):
    region: str
    delivered_100c: int
    delivered_250: int
    customer_company: Optional[str] = None


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
    photo_paths: List[str] = Field(default_factory=list)
    remarks: Optional[str] = None


class WarehouseInventoryItemUpdate(BaseModel):
    description_zh: str
    specification: str
    total_quantity: int = 0
    damaged_quantity: int = 0
    available_quantity: Optional[int] = None
    photo_paths: List[str] = Field(default_factory=list)
    remarks: Optional[str] = None


class TechnicalDocUpdate(BaseModel):
    product_series: Optional[str] = None
    category: Optional[str] = None
    title: Optional[str] = None


class LoginPayload(BaseModel):
    username: str
    password: str


class CustomerUserPayload(BaseModel):
    username: str
    password: str
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    project_ids: List[str] = Field(default_factory=list)


class CustomerUserUpdatePayload(BaseModel):
    password: Optional[str] = None
    customer_name: Optional[str] = None
    customer_company: Optional[str] = None
    project_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MilestonePayload(BaseModel):
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Literal["已完成", "进行中", "待开始"] = "待开始"
    notes: str = ""


class AfterSalesLogPayload(BaseModel):
    event_date: date
    country: str
    customer: str
    customer_company: Optional[str] = None
    project_name: str
    product_model: Literal["418", "250", "100C"]
    support_type: Literal["远程 (Remote)", "现场 (On-site)"]
    issue_category: Literal["软件 (Software)", "硬件 (Hardware)"]
    fault_component: Optional[Literal["PACK", "Chiller", "PCS", "eLink", "Cabinet", "Software", "Transformer", "Other"]] = None
    faulty_component: Optional[Literal["PACK", "Chiller", "PCS", "eLink", "Cabinet", "Software", "Transformer", "Other"]] = None
    serial_number: str = ""
    status: Literal["已解决 (Resolved)", "处理中 (Pending)"] = "处理中 (Pending)"
    pending_reason: str = ""
    created_by: str
    attachments: List[str] = Field(default_factory=list)


class TicketPayload(BaseModel):
    project_name: str
    customer_company: Optional[str] = None
    serial_number: str
    product_model: Literal["418", "250", "100C"]
    ticket_type: Literal["产品需求 (Feature Request)", "故障报修/Bug (Issue Report)"]
    suspected_scope: Literal["软件", "硬件"]
    suspected_component: Literal["PACK", "Chiller", "PCS", "eLink", "Cabinet", "Software", "Transformer", "Other"]
    description: str
    attachments: List[str] = Field(default_factory=list)
    expected_resolution_date: Optional[date] = None
    expected_date: Optional[date] = None
    contact: str


class TicketUpdatePayload(BaseModel):
    status: Literal["待处理 (Pending)", "处理中 (In Progress)", "已回复/已解决 (Resolved)", "已关闭 (Closed)"]
    staff_reply: str = ""
    resolved_at: Optional[datetime] = None
    expected_date: Optional[date] = None


app = FastAPI(
    title="JD Energy Service Portal API",
    version="2.0.0",
    description="Fault lookup, project ledger, C&I deliveries, and warehouse inventory APIs.",
)

BACKEND_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_ROOT / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
DOCS_UPLOAD_DIR = UPLOAD_DIR / "docs"
os.makedirs(DOCS_UPLOAD_DIR, exist_ok=True)

app.mount("/static_uploads", StaticFiles(directory=UPLOAD_DIR), name="static_uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def deny_customer_warehouse_access(request: Request, call_next):
    protected_customer_paths = ("/api/warehouse/", "/api/ledger/grid-scale", "/api/ledger/ci-deliveries")
    if request.url.path.startswith(protected_customer_paths):
        authorization = request.headers.get("authorization", "")
        if authorization.lower().startswith("bearer "):
            try:
                token_payload = authorization.split(" ", 1)[1].split(".")[1]
                payload = json.loads(base64.urlsafe_b64decode(token_payload + "=" * (-len(token_payload) % 4)))
                if payload.get("role") == "customer":
                    return Response(content=json.dumps({"detail": "Warehouse is not available to customer accounts"}), status_code=403, media_type="application/json")
            except (ValueError, IndexError, json.JSONDecodeError):
                pass
    return await call_next(request)

warehouse_inventory_router = APIRouter(
    prefix="/api/warehouse/inventory",
    tags=["Warehouse Inventory"],
)

grid_scale_router = APIRouter(
    prefix="/api/ledger/grid-scale",
    tags=["Grid-Scale Ledger"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_mode = os.getenv("SEED_MODE", "all").strip().lower()
    if seed_mode == "all":
        seed_database()
    elif seed_mode in {"none", "after-sales-only", "after_sales_only"}:
        # Skip legacy full-module seed when deploying with selective data initialization.
        pass
    else:
        seed_database()


def seed_database() -> None:
    with get_session() as session:
        if session.exec(select(User).where(User.username == "JDE")).first() is None:
            session.add(User(username="JDE", password_hash=hash_password("Jdny_8888"), role="admin", customer_name="JD Energy"))
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
        else:
            sync_warehouse_inventory_item_seed(session)
        if session.exec(select(TechnicalDoc)).first() is None:
            session.add_all([TechnicalDoc(**item) for item in TECHNICAL_DOCS_SEED])
        session.commit()


def sync_warehouse_inventory_item_seed(session) -> None:
    seeded_by_key = {item.item_no: item for item in WAREHOUSE_INVENTORY_ITEM_SEED}
    existing_by_key = {
        item.item_no: item
        for item in session.exec(select(WarehouseInventoryItem)).all()
    }

    for item_no, seed_item in seeded_by_key.items():
        target = existing_by_key.get(item_no)
        if target is None:
            session.add(WarehouseInventoryItem(**seed_item.model_dump()))
            continue

        target.description_zh = seed_item.description_zh
        target.specification = seed_item.specification
        target.total_quantity = seed_item.total_quantity
        target.damaged_quantity = seed_item.damaged_quantity
        target.available_quantity = seed_item.available_quantity
        target.photo_paths = seed_item.photo_paths
        target.remarks = seed_item.remarks
        session.add(target)


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


def normalize_after_sales_fault_code_item(item: AfterSalesFaultCodeItem) -> Dict[str, str]:
    return {
        "module": item.module.strip(),
        "fault_code": item.fault_code.strip(),
        "fault_name": item.fault_name.strip(),
        "fault_level": item.fault_level.strip(),
        "is_stop": item.is_stop.strip(),
        "recovery": item.recovery.strip(),
        "detection_condition": item.detection_condition.strip(),
        "trigger_logic": item.trigger_logic.strip(),
        "possible_cause": item.possible_cause.strip(),
        "solution": item.solution.strip(),
    }


def upsert_after_sales_fault_codes(session, items: List[AfterSalesFaultCodeItem], overwrite: bool = True) -> Dict[str, int]:
    created = 0
    updated = 0
    skipped = 0

    for item in items:
        payload = normalize_after_sales_fault_code_item(item)
        if not payload["module"] or not payload["fault_code"]:
            skipped += 1
            continue

        existing = session.exec(
            select(AfterSalesFaultCode).where(
                AfterSalesFaultCode.module == payload["module"],
                AfterSalesFaultCode.fault_code == payload["fault_code"],
            )
        ).first()

        if existing is None:
            session.add(AfterSalesFaultCode(**payload))
            created += 1
            continue

        if not overwrite:
            skipped += 1
            continue

        existing.fault_name = payload["fault_name"]
        existing.fault_level = payload["fault_level"]
        existing.is_stop = payload["is_stop"]
        existing.recovery = payload["recovery"]
        existing.detection_condition = payload["detection_condition"]
        existing.trigger_logic = payload["trigger_logic"]
        existing.possible_cause = payload["possible_cause"]
        existing.solution = payload["solution"]
        session.add(existing)
        updated += 1

    return {"created": created, "updated": updated, "skipped": skipped}


def serialize_inventory(rows: List[WarehouseInventory]) -> Dict[str, List[WarehouseInventory]]:
    grouped: Dict[str, List[WarehouseInventory]] = defaultdict(list)
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
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "JD Energy Service Portal API"}


@app.get("/api/fault-codes")
def get_fault_codes(q: str = Query(default="", description="Fault code or keyword search term")) -> Dict[str, object]:
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
def create_fault_code(payload: FaultCodeRecord) -> Dict[str, object]:
    with get_session() as session:
        if session.get(FaultCode, payload.fault_code) is not None:
                        raise HTTPException(status_code=409, detail="Fault code already exists")
        item = FaultCode(**payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
        original_suffix = Path(file.filename or "").suffix or ".bin"
        new_filename = f"{uuid.uuid4().hex}{original_suffix}"
        file_path = UPLOAD_DIR / new_filename
        contents = await file.read()
        file_path.write_bytes(contents)
        return {"url": f"/static_uploads/{new_filename}"}


def format_file_size(size_in_bytes: int) -> str:
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    return f"{size_in_bytes / (1024 * 1024):.1f} MB"


def resolve_local_upload_path(file_url: str) -> Optional[Path]:
    static_prefix = "/static_uploads/"
    if not file_url.startswith(static_prefix):
        return None
    relative_path = file_url[len(static_prefix):].lstrip("/")
    return UPLOAD_DIR / relative_path


def validate_technical_doc_dims(product_series: str, category: str) -> None:
    if product_series not in TECHNICAL_DOC_PRODUCT_SERIES:
        raise HTTPException(status_code=400, detail="Invalid product series")
    if category not in TECHNICAL_DOC_CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")


@app.get("/api/technical-docs")
def list_technical_docs(
    product: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(TechnicalDoc)
        if product and product.strip():
            normalized_product = product.strip()
            if normalized_product in {"418", "250"}:
                statement = statement.where(TechnicalDoc.product_series.in_([normalized_product, "418/250"]))
            else:
                statement = statement.where(TechnicalDoc.product_series == normalized_product)
        if category and category.strip():
            statement = statement.where(TechnicalDoc.category == category.strip())
        items = session.exec(statement.order_by(TechnicalDoc.updated_at.desc(), TechnicalDoc.id.desc())).all()

    return {"count": len(items), "items": items}


@app.post("/api/technical-docs")
async def create_technical_doc(
    product_series: str = Form(...),
    category: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
) -> Dict[str, object]:
    normalized_product_series = product_series.strip()
    normalized_category = category.strip()
    normalized_title = title.strip()

    validate_technical_doc_dims(normalized_product_series, normalized_category)
    if not normalized_title:
        raise HTTPException(status_code=400, detail="Title is required")

    original_suffix = Path(file.filename or "").suffix or ".bin"
    new_filename = f"{uuid.uuid4().hex}{original_suffix}"
    file_path = DOCS_UPLOAD_DIR / new_filename
    content = await file.read()
    file_path.write_bytes(content)

    item = TechnicalDoc(
        product_series=normalized_product_series,
        category=normalized_category,
        title=normalized_title,
        file_url=f"/static_uploads/docs/{new_filename}",
        file_type=file.content_type or original_suffix.lstrip(".").lower(),
        file_size=format_file_size(len(content)),
        updated_at=datetime.utcnow(),
    )

    with get_session() as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/technical-docs/{doc_id}")
def update_technical_doc(doc_id: int, payload: TechnicalDocUpdate) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(TechnicalDoc, doc_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Technical document not found")

        next_product_series = payload.product_series.strip() if payload.product_series is not None else item.product_series
        next_category = payload.category.strip() if payload.category is not None else item.category
        validate_technical_doc_dims(next_product_series, next_category)

        if payload.title is not None:
            normalized_title = payload.title.strip()
            if not normalized_title:
                raise HTTPException(status_code=400, detail="Title is required")
            item.title = normalized_title

        item.product_series = next_product_series
        item.category = next_category
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/technical-docs/{doc_id}")
def delete_technical_doc(doc_id: int) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(TechnicalDoc, doc_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Technical document not found")

        local_path = resolve_local_upload_path(item.file_url)
        if local_path is not None and local_path.exists():
            local_path.unlink()

        session.delete(item)
        session.commit()
        return {"message": "deleted"}


# Portal authentication and tenant-scoped workflows. Legacy public read routes above remain
# compatible with the existing dashboard; all new customer data APIs require this identity.
JWT_SECRET = os.getenv("PORTAL_JWT_SECRET", "jd-energy-change-this-secret")
MILESTONE_KEYS = {
    "start-installation": "开始安装 (Start Installation)",
    "start-commissioning": "开始交付 (Start Commissioning)",
    "commissioning-completed": "交付完成 (Commissioning Completed)",
    "pac-fac-accepted": "验收完成 (PAC/FAC Accepted)",
}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def encode_token(user: User) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": user.username, "user_id": user.id, "role": user.role, "exp": int(time.time()) + 86400}
    def encode(value):
        return base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode()).decode().rstrip("=")
    unsigned = f"{encode(header)}.{encode(payload)}"
    signature = hmac.new(JWT_SECRET.encode(), unsigned.encode(), hashlib.sha256).digest()
    return f"{unsigned}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


def current_user(authorization: Optional[str] = Header(default=None)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        encoded_header, encoded_payload, encoded_signature = authorization.split(" ", 1)[1].split(".")
        unsigned = f"{encoded_header}.{encoded_payload}"
        expected = hmac.new(JWT_SECRET.encode(), unsigned.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(encoded_signature + "=" * (-len(encoded_signature) % 4))
        if not hmac.compare_digest(expected, supplied):
            raise ValueError("signature")
        payload = json.loads(base64.urlsafe_b64decode(encoded_payload + "=" * (-len(encoded_payload) % 4)))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired")
    except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    with get_session() as session:
        user = session.get(User, int(payload["user_id"]))
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="User is inactive")
        return user


def require_staff(user: User = Depends(current_user)) -> User:
    if user.role not in {"admin", "staff"}:
        raise HTTPException(status_code=403, detail="Staff access required")
    return user


def accessible_project_names(session, user: User) -> set[str]:
    if user.role in {"admin", "staff"}:
        return {item.project_name for item in session.exec(select(GridScaleProject)).all()}
    company = (user.customer_company or user.customer_name or "").strip().casefold()
    projects = session.exec(select(GridScaleProject)).all()
    automatic = {item.project_name for item in projects if (item.customer_company or item.partner_name or "").strip().casefold() == company}
    automatic.update(item.project_name for item in session.exec(select(AfterSalesLog)).all() if (item.customer_company or item.customer or "").strip().casefold() == company)
    automatic.update(item.dealer_name for item in session.exec(select(CiDealerDelivery)).all() if (item.customer_company or item.dealer_name or "").strip().casefold() == company)
    return automatic


def legal_customer_companies(session) -> set[str]:
    companies = {
        (user.customer_company or user.customer_name or "").strip()
        for user in session.exec(select(User).where(User.role == "customer")).all()
    }
    companies.update(
        (project.customer_company or project.partner_name or "").strip()
        for project in session.exec(select(GridScaleProject)).all()
    )
    companies.update(
        (dealer.customer_company or dealer.dealer_name or "").strip()
        for dealer in session.exec(select(CiDealerDelivery)).all()
    )
    return {company for company in companies if company}


def public_user(user: User, session) -> Dict[str, object]:
    data = user.model_dump(exclude={"password_hash"})
    data["automatic_projects"] = sorted(accessible_project_names(session, user))
    data["automatic_project_count"] = len(data["automatic_projects"])
    return data


@app.post("/api/auth/login")
def login(payload: LoginPayload) -> Dict[str, object]:
    with get_session() as session:
        user = session.exec(select(User).where(User.username == payload.username.strip())).first()
        if user is None or user.password_hash != hash_password(payload.password) or not user.is_active:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        return {"token": encode_token(user), "user": public_user(user, session)}


@app.get("/api/auth/me")
def get_current_user(user: User = Depends(current_user)) -> User:
    return user


@app.get("/api/admin/users")
def list_users(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(User).order_by(User.id.asc())).all()
        serialized = [public_user(item, session) for item in items]
    return {"count": len(serialized), "items": serialized}


@app.post("/api/admin/users")
def create_user(payload: CustomerUserPayload, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        if session.exec(select(User).where(User.username == payload.username.strip())).first():
            raise HTTPException(status_code=409, detail="Username already exists")
        company = (payload.customer_company or payload.customer_name or "").strip()
        if not company:
            raise HTTPException(status_code=422, detail="Customer company is required")
        user = User(username=payload.username.strip(), password_hash=hash_password(payload.password), customer_name=company, customer_company=company, project_ids=[])
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"item": public_user(user, session)}


@app.put("/api/admin/users/{user_id}")
def update_user(user_id: int, payload: CustomerUserUpdatePayload, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None or user.role == "admin":
            raise HTTPException(status_code=404, detail="Customer user not found")
        if payload.password is not None:
            user.password_hash = hash_password(payload.password)
        company = payload.customer_company or payload.customer_name
        if company is not None:
            user.customer_name = company.strip()
            user.customer_company = user.customer_name
        user.project_ids = []
        if payload.is_active is not None:
            user.is_active = payload.is_active
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"item": public_user(user, session)}


@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, _: User = Depends(require_staff)) -> Dict[str, str]:
    with get_session() as session:
        user = session.get(User, user_id)
        if user is None or user.role == "admin":
            raise HTTPException(status_code=404, detail="Customer user not found")
        session.delete(user)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/portal/projects")
def list_portal_projects(user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        allowed = accessible_project_names(session, user)
        items = session.exec(select(GridScaleProject).order_by(GridScaleProject.cod.asc())).all()
        if user.role == "customer":
            items = [item for item in items if item.project_name in allowed]
    return {"count": len(items), "items": items}


@app.get("/api/portal/ci-deliveries")
def list_portal_ci_deliveries(user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        statement = select(CiDealerDelivery)
        if user.role == "customer":
            company = user.customer_company or user.customer_name or ""
            statement = statement.where(or_(CiDealerDelivery.customer_company == company, CiDealerDelivery.dealer_name == company))
        items = session.exec(statement).all()
    return {"count": len(items), "items": items}


@app.get("/api/projects/{project_name}/milestones")
def list_milestones(project_name: str, user: User = Depends(current_user)) -> Dict[str, object]:
    with get_session() as session:
        if project_name not in accessible_project_names(session, user):
            raise HTTPException(status_code=403, detail="Project is outside your tenant")
        existing = session.exec(select(ProjectMilestone).where(ProjectMilestone.project_name == project_name)).all()
        by_key = {item.milestone_key: item for item in existing}
        for key in MILESTONE_KEYS:
            if key not in by_key:
                item = ProjectMilestone(project_name=project_name, milestone_key=key)
                session.add(item)
                by_key[key] = item
        session.commit()
    return {"project_name": project_name, "items": [{"key": key, "label": MILESTONE_KEYS[key], **by_key[key].model_dump()} for key in MILESTONE_KEYS]}


@app.put("/api/projects/{project_name}/milestones/{milestone_key}")
def update_milestone(project_name: str, milestone_key: str, payload: MilestonePayload, _: User = Depends(require_staff)) -> Dict[str, object]:
    if milestone_key not in MILESTONE_KEYS:
        raise HTTPException(status_code=400, detail="Invalid milestone")
    with get_session() as session:
        item = session.exec(select(ProjectMilestone).where(ProjectMilestone.project_name == project_name, ProjectMilestone.milestone_key == milestone_key)).first()
        if item is None:
            item = ProjectMilestone(project_name=project_name, milestone_key=milestone_key)
        item.planned_date, item.actual_date, item.status, item.notes = payload.planned_date, payload.actual_date, payload.status, payload.notes
        item.updated_at = datetime.utcnow()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.get("/api/after-sales/logs")
def list_after_sales_logs(
    country: Optional[str] = Query(default=None),
    project_name: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(AfterSalesLog).order_by(AfterSalesLog.event_date.desc())
        if user.role == "customer":
            statement = statement.where(AfterSalesLog.project_name.in_(accessible_project_names(session, user)))
            statement = statement.where(AfterSalesLog.customer == (user.customer_name or ""))
        if country: statement = statement.where(AfterSalesLog.country == country)
        if project_name: statement = statement.where(AfterSalesLog.project_name == project_name)
        if status: statement = statement.where(AfterSalesLog.status == status)
        if keyword:
            like_keyword = f"%{keyword}%"
            statement = statement.where(or_(AfterSalesLog.customer.like(like_keyword), AfterSalesLog.faulty_component.like(like_keyword), AfterSalesLog.serial_number.like(like_keyword)))
        items = session.exec(statement).all()
    return {"count": len(items), "items": items}


@app.post("/api/after-sales/logs")
def create_after_sales_log(payload: AfterSalesLogPayload, user: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        company = (payload.customer_company or payload.customer or "").strip()
        component = payload.fault_component or payload.faulty_component
        if not component:
            raise HTTPException(status_code=422, detail="Fault component is required")
        if not company:
            raise HTTPException(status_code=422, detail="Customer company is required")
        if company.casefold() not in {item.casefold() for item in legal_customer_companies(session)}:
            raise HTTPException(status_code=400, detail="Customer company is not registered")
        project = session.get(GridScaleProject, payload.project_name)
        dealer = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.project_name)).first()
        if project is None and dealer is None:
            if not payload.project_name.strip():
                raise HTTPException(status_code=422, detail="Project is required")
            raise HTTPException(status_code=400, detail="Project does not exist")
        project_company = (project.customer_company or project.partner_name or "").strip() if project else (dealer.customer_company or dealer.dealer_name or "").strip()
        if project_company and project_company.casefold() != company.casefold():
            raise HTTPException(status_code=400, detail="Project does not belong to customer company")
        item = AfterSalesLog(**payload.model_dump(exclude={"customer", "customer_company", "fault_component", "faulty_component"}), customer_company=company, customer=company, fault_component=component, faulty_component=component)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.put("/api/after-sales/logs/{log_id}")
def update_after_sales_log(log_id: int, payload: AfterSalesLogPayload, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(AfterSalesLog, log_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales log not found")
        company = (payload.customer_company or payload.customer or "").strip()
        component = payload.fault_component or payload.faulty_component
        if not component:
            raise HTTPException(status_code=422, detail="Fault component is required")
        if not company:
            raise HTTPException(status_code=422, detail="Customer company is required")
        if company.casefold() not in {item.casefold() for item in legal_customer_companies(session)}:
            raise HTTPException(status_code=400, detail="Customer company is not registered")
        project = session.get(GridScaleProject, payload.project_name)
        dealer = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.project_name)).first()
        if project is None and dealer is None:
            raise HTTPException(status_code=400, detail="Project does not exist")
        project_company = (project.customer_company or project.partner_name or "").strip() if project else (dealer.customer_company or dealer.dealer_name or "").strip()
        if project_company and project_company.casefold() != company.casefold():
            raise HTTPException(status_code=400, detail="Project does not belong to customer company")
        for key, value in payload.model_dump(exclude={"customer_company", "customer", "fault_component", "faulty_component"}).items():
            setattr(item, key, value)
        item.customer_company = company
        item.customer = company
        item.fault_component = component
        item.faulty_component = component
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.delete("/api/after-sales/logs/{log_id}")
def delete_after_sales_log(log_id: int, _: User = Depends(require_staff)) -> Dict[str, str]:
    with get_session() as session:
        item = session.get(AfterSalesLog, log_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales log not found")
        session.delete(item)
        session.commit()
    return {"message": "deleted"}


@app.get("/api/customer/tickets")
def list_tickets(
    submit_from: Optional[datetime] = Query(default=None),
    submit_to: Optional[datetime] = Query(default=None),
    project_name: Optional[str] = Query(default=None),
    customer_company: Optional[str] = Query(default=None),
    product_model: Optional[str] = Query(default=None),
    serial_number: Optional[str] = Query(default=None),
    faulty_component: Optional[str] = Query(default=None),
    ticket_type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    user: User = Depends(current_user),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(CustomerTicket).order_by(CustomerTicket.submit_time.desc())
        if user.role == "customer":
            statement = statement.where(CustomerTicket.customer_id == user.id)
        if submit_from:
            statement = statement.where(CustomerTicket.submit_time >= submit_from)
        if submit_to:
            statement = statement.where(CustomerTicket.submit_time <= submit_to)
        if project_name:
            statement = statement.where(CustomerTicket.project_name == project_name)
        if customer_company:
            statement = statement.where(CustomerTicket.customer_company == customer_company)
        if product_model:
            statement = statement.where(CustomerTicket.product_model == product_model)
        if serial_number:
            statement = statement.where(CustomerTicket.serial_number.like(f"%{serial_number}%"))
        if faulty_component:
            statement = statement.where(CustomerTicket.suspected_component == faulty_component)
        if ticket_type:
            statement = statement.where(CustomerTicket.ticket_type == ticket_type)
        if status:
            statement = statement.where(CustomerTicket.status == status)
        items = session.exec(statement).all()
    return {"count": len(items), "items": items}


@app.post("/api/customer/tickets")
def create_ticket(payload: TicketPayload, user: User = Depends(current_user)) -> Dict[str, object]:
    if user.role != "customer":
        raise HTTPException(status_code=403, detail="Customer account required")
    if not payload.serial_number.strip():
        raise HTTPException(status_code=422, detail="Serial number is required")
    if payload.product_model == "418" and not payload.project_name.strip():
        raise HTTPException(status_code=422, detail="Project is required for model 418")
    with get_session() as session:
        if payload.product_model == "418" and payload.project_name not in accessible_project_names(session, user):
            raise HTTPException(status_code=403, detail="Project is outside your tenant")
        item = CustomerTicket(**payload.model_dump(exclude={"project_name", "customer_company"}), customer_id=user.id, customer_name=user.customer_name or user.username, customer_company=user.customer_company or user.customer_name or user.username, project_name=payload.project_name if payload.product_model == "418" else "")
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.patch("/api/customer/tickets/{ticket_id}")
def update_ticket(ticket_id: int, payload: TicketUpdatePayload, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(CustomerTicket, ticket_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        item.status, item.staff_reply, item.updated_at = payload.status, payload.staff_reply, datetime.utcnow()
        item.expected_date = payload.expected_date
        item.expected_resolution_date = payload.expected_date
        item.resolved_at = payload.resolved_at or (datetime.utcnow() if payload.status in {"已回复/已解决 (Resolved)", "已关闭 (Closed)"} else None)
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"item": item}


@app.get("/api/after-sales/logs/export")
def export_after_sales_logs(user: User = Depends(require_staff)):
    with get_session() as session:
        rows = session.exec(select(AfterSalesLog).order_by(AfterSalesLog.event_date.asc())).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Country", "Customer", "Project", "Model", "Support", "Category", "Component", "SN", "Status", "Follow-up", "Created By"])
    for row in rows:
        writer.writerow([row.event_date, row.country, row.customer_company or row.customer, row.project_name, row.product_model, row.support_type, row.issue_category, row.fault_component or row.faulty_component, row.serial_number, row.status, row.pending_reason, row.created_by])
    return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=after-sales-logs.csv"})


@app.get("/api/technical-docs/{doc_id}/file")
def get_technical_doc_file(doc_id: int, download: bool = Query(default=False)):
    with get_session() as session:
        item = session.get(TechnicalDoc, doc_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Technical document not found")

    if item.file_url.startswith("http://") or item.file_url.startswith("https://"):
        return RedirectResponse(url=item.file_url, status_code=307)

    local_path = resolve_local_upload_path(item.file_url)
    if local_path is None or not local_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    suffix = local_path.suffix
    filename = f"{item.title}{suffix}" if suffix and not item.title.endswith(suffix) else item.title
    media_type = item.file_type or mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"

    if download:
        return FileResponse(
            path=local_path,
            media_type=media_type,
            filename=filename,
        )

    return FileResponse(
        path=local_path,
        media_type=media_type,
        content_disposition_type="inline",
    )


@app.put("/api/fault-codes/{fault_code}")
def update_fault_code(fault_code: str, payload: FaultCodeUpsert) -> Dict[str, object]:
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
def delete_fault_code(fault_code: str) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(FaultCode, fault_code)
        if item is None:
            raise HTTPException(status_code=404, detail="Fault code not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/after-sales/fault-codes")
def list_after_sales_fault_codes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    module: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
) -> Dict[str, object]:
    with get_session() as session:
        statement = select(AfterSalesFaultCode)

        if module and module.strip():
            statement = statement.where(AfterSalesFaultCode.module == module.strip())

        if keyword and keyword.strip():
            like_keyword = f"%{keyword.strip()}%"
            statement = statement.where(
                or_(
                    AfterSalesFaultCode.fault_code.like(like_keyword),
                    AfterSalesFaultCode.fault_name.like(like_keyword),
                )
            )

        all_items = session.exec(statement.order_by(AfterSalesFaultCode.id.asc())).all()

    total = len(all_items)
    offset = (page - 1) * page_size
    paged_items = all_items[offset: offset + page_size]

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "count": len(paged_items),
        "items": paged_items,
    }


@app.post("/api/after-sales/fault-codes")
def create_after_sales_fault_code(payload: AfterSalesFaultCodeCreate) -> Dict[str, object]:
    normalized_module = payload.module.strip()
    normalized_fault_code = payload.fault_code.strip()
    if not normalized_module or not normalized_fault_code:
        raise HTTPException(status_code=400, detail="module and fault_code are required")

    with get_session() as session:
        exists = session.exec(
            select(AfterSalesFaultCode).where(
                AfterSalesFaultCode.module == normalized_module,
                AfterSalesFaultCode.fault_code == normalized_fault_code,
            )
        ).first()
        if exists is not None:
            raise HTTPException(status_code=409, detail="Fault code already exists in this module")

        item = AfterSalesFaultCode(
            module=normalized_module,
            fault_code=normalized_fault_code,
            fault_name=payload.fault_name.strip(),
            fault_level=payload.fault_level.strip(),
            is_stop=payload.is_stop.strip(),
            recovery=payload.recovery.strip(),
            detection_condition=payload.detection_condition.strip(),
            trigger_logic=payload.trigger_logic.strip(),
            possible_cause=payload.possible_cause.strip(),
            solution=payload.solution.strip(),
        )
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/after-sales/fault-codes/{item_id}")
def update_after_sales_fault_code(item_id: int, payload: AfterSalesFaultCodeUpdate) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(AfterSalesFaultCode, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales fault code not found")

        next_module = payload.module.strip() if payload.module is not None else item.module
        next_fault_code = payload.fault_code.strip() if payload.fault_code is not None else item.fault_code
        if not next_module or not next_fault_code:
            raise HTTPException(status_code=400, detail="module and fault_code are required")

        duplicate = session.exec(
            select(AfterSalesFaultCode).where(
                AfterSalesFaultCode.module == next_module,
                AfterSalesFaultCode.fault_code == next_fault_code,
                AfterSalesFaultCode.id != item.id,
            )
        ).first()
        if duplicate is not None:
            raise HTTPException(status_code=409, detail="Fault code already exists in this module")

        item.module = next_module
        item.fault_code = next_fault_code
        if payload.fault_name is not None:
            item.fault_name = payload.fault_name.strip()
        if payload.fault_level is not None:
            item.fault_level = payload.fault_level.strip()
        if payload.is_stop is not None:
            item.is_stop = payload.is_stop.strip()
        if payload.recovery is not None:
            item.recovery = payload.recovery.strip()
        if payload.detection_condition is not None:
            item.detection_condition = payload.detection_condition.strip()
        if payload.trigger_logic is not None:
            item.trigger_logic = payload.trigger_logic.strip()
        if payload.possible_cause is not None:
            item.possible_cause = payload.possible_cause.strip()
        if payload.solution is not None:
            item.solution = payload.solution.strip()

        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/after-sales/fault-codes/{item_id}")
def delete_after_sales_fault_code(item_id: int) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(AfterSalesFaultCode, item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="After-sales fault code not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.post("/api/after-sales/fault-codes/import")
async def import_after_sales_fault_codes(
    payload: Optional[AfterSalesFaultCodeImportPayload] = Body(default=None),
    file: Optional[UploadFile] = File(default=None),
    overwrite: bool = Query(default=True),
) -> Dict[str, object]:
    parsed_items: List[object] = []

    if file is not None:
        raw_text = (await file.read()).decode("utf-8")
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {exc}") from exc

        if isinstance(data, list):
            parsed_items = data
        elif isinstance(data, dict) and isinstance(data.get("items"), list):
            parsed_items = data["items"]
        else:
            raise HTTPException(status_code=400, detail="JSON must be a list or an object with an 'items' list")
    elif payload is not None:
        parsed_items = [item.model_dump() for item in payload.items]
    else:
        raise HTTPException(status_code=400, detail="Provide request JSON body or upload a JSON file")

    validated_items: List[AfterSalesFaultCodeItem] = []
    validation_errors: List[Dict[str, object]] = []
    for index, item in enumerate(parsed_items):
        try:
            validated_items.append(AfterSalesFaultCodeItem.model_validate(item))
        except ValidationError as exc:
            validation_errors.append({"index": index, "error": exc.errors()})

    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Some records failed validation",
                "errors": validation_errors[:20],
                "error_count": len(validation_errors),
            },
        )

    with get_session() as session:
        result = upsert_after_sales_fault_codes(session, validated_items, overwrite=overwrite)
        session.commit()

    return {
        "message": "imported",
        "source_count": len(parsed_items),
        **result,
    }


@grid_scale_router.get("")
def list_grid_scale_projects(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(
            select(GridScaleProject).order_by(GridScaleProject.cod.asc(), GridScaleProject.project_name.asc())
        ).all()
    return {"count": len(items), "items": items}


@grid_scale_router.post("")
def create_grid_scale_project(payload: GridScaleProjectUpsert, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        if session.get(GridScaleProject, payload.project_name) is not None:
            raise HTTPException(status_code=409, detail="Project already exists")
        item = GridScaleProject(**payload.model_dump())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@grid_scale_router.put("/{project_name}")
def update_grid_scale_project(project_name: str, payload: GridScaleProjectUpsert, _: User = Depends(require_staff)) -> Dict[str, object]:
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
        item.partner_name = payload.partner_name.strip()
        item.customer_company = (payload.customer_company or payload.partner_name).strip()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@grid_scale_router.post("/{project_name}/status")
def update_grid_scale_status(project_name: str, payload: GridScaleStatusUpdate, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        project = session.get(GridScaleProject, project_name)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        project.progress_status = payload.progress_status
        session.add(project)
        session.commit()
        session.refresh(project)
        return {"message": "updated", "item": project}


@grid_scale_router.delete("/{project_name}")
def delete_grid_scale_project(project_name: str, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(GridScaleProject, project_name)
        if item is None:
            raise HTTPException(status_code=404, detail="Project not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@warehouse_inventory_router.get("")
def list_warehouse_inventory_items() -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(WarehouseInventoryItem)).all()
    return {"count": len(items), "items": items}


@warehouse_inventory_router.post("")
def create_warehouse_inventory_item(payload: WarehouseInventoryItemCreate) -> Dict[str, object]:
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


@warehouse_inventory_router.put("/{item_no}")
def update_warehouse_inventory_item(item_no: str, payload: WarehouseInventoryItemUpdate) -> Dict[str, object]:
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


@warehouse_inventory_router.delete("/{item_no}")
def delete_warehouse_inventory_item(item_no: str) -> Dict[str, object]:
    with get_session() as session:
        item = session.get(WarehouseInventoryItem, item_no)
        if item is None:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


app.include_router(warehouse_inventory_router)
app.include_router(grid_scale_router)


@app.get("/api/ledger/ci-deliveries")
def list_ci_deliveries(_: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        items = session.exec(select(CiDealerDelivery)).all()
    return {"count": len(items), "items": items}


@app.post("/api/ledger/ci-deliveries")
def create_ci_delivery(payload: CiDeliveryCreateUpdate, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        if session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == payload.dealer_name)).first() is not None:
            raise HTTPException(status_code=409, detail="Dealer already exists")
        item = CiDealerDelivery(**payload.model_dump(exclude={"customer_company"}), customer_company=(payload.customer_company or payload.dealer_name).strip())
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "created", "item": item}


@app.put("/api/ledger/ci-deliveries/{dealer_name}")
def update_ci_delivery(dealer_name: str, payload: CiDeliveryUpdate, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        item = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == dealer_name)).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Dealer not found")
        item.region = payload.region
        item.delivered_100c = payload.delivered_100c
        item.delivered_250 = payload.delivered_250
        item.customer_company = (payload.customer_company or payload.dealer_name).strip()
        session.add(item)
        session.commit()
        session.refresh(item)
        return {"message": "updated", "item": item}


@app.delete("/api/ledger/ci-deliveries/{dealer_name}")
def delete_ci_delivery(dealer_name: str, _: User = Depends(require_staff)) -> Dict[str, object]:
    with get_session() as session:
        item = session.exec(select(CiDealerDelivery).where(CiDealerDelivery.dealer_name == dealer_name)).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Dealer not found")
        session.delete(item)
        session.commit()
        return {"message": "deleted"}


@app.get("/api/warehouse/summary")
def get_warehouse_summary(warehouse_name: str = Query(default="europe")) -> Dict[str, object]:
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
def create_warehouse_transaction(payload: WarehouseTransactionCreate) -> Dict[str, object]:
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
def update_warehouse_transaction(tx_no: str, payload: WarehouseTransactionUpdate) -> Dict[str, object]:
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
def delete_warehouse_transaction(tx_no: str) -> Dict[str, object]:
    with get_session() as session:
        transaction = session.exec(select(WarehouseTransaction).where(WarehouseTransaction.tx_no == tx_no)).first()
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        delta = transaction.quantity if transaction.tx_type == "国内到货入库" else -transaction.quantity
        apply_inventory_delta(session, transaction.warehouse_name, transaction.product_model, -delta)
        session.delete(transaction)
        session.commit()
        return {"message": "deleted", "summary": get_warehouse_summary(transaction.warehouse_name)}
