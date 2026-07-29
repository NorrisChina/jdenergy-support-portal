from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

from sqlmodel import select


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.database import get_session, init_db  # noqa: E402
from app.models.after_sales import FaultCode as AfterSalesFaultCode  # noqa: E402


def load_fault_code_payload() -> List[Dict[str, object]]:
    candidates = [
        ROOT_DIR / "fault_codes_extracted.json",
        BACKEND_DIR / "fault_codes_extracted.json",
    ]

    source_path = None
    for candidate in candidates:
        if candidate.exists():
            source_path = candidate
            break

    if source_path is None:
        raise FileNotFoundError("fault_codes_extracted.json not found in project root or backend directory")

    with source_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, list):
        raise ValueError("fault_codes_extracted.json must contain a JSON array")

    return payload


def normalize_fault_code_record(item: Dict[str, object]) -> Dict[str, str]:
    return {
        "module": str(item.get("module", "")).strip(),
        "fault_code": str(item.get("fault_code", "")).strip(),
        "fault_name": str(item.get("fault_name", "")).strip(),
        "fault_level": str(item.get("fault_level", "")).strip(),
        "is_stop": str(item.get("is_stop", "")).strip(),
        "recovery": str(item.get("recovery", "")).strip(),
        "detection_condition": str(item.get("detection_condition", "")).strip(),
        "trigger_logic": str(item.get("trigger_logic", "")).strip(),
        "possible_cause": str(item.get("possible_cause", "")).strip(),
        "solution": str(item.get("solution", "")).strip(),
    }


def main() -> None:
    init_db()
    source_rows = load_fault_code_payload()

    created = 0
    updated = 0
    skipped = 0

    with get_session() as session:
        for raw_item in source_rows:
            normalized = normalize_fault_code_record(raw_item)
            if not normalized["module"] or not normalized["fault_code"]:
                skipped += 1
                continue

            existing = session.exec(
                select(AfterSalesFaultCode).where(
                    AfterSalesFaultCode.module == normalized["module"],
                    AfterSalesFaultCode.fault_code == normalized["fault_code"],
                )
            ).first()

            if existing is None:
                session.add(AfterSalesFaultCode(**normalized))
                created += 1
                continue

            existing.fault_name = normalized["fault_name"]
            existing.fault_level = normalized["fault_level"]
            existing.is_stop = normalized["is_stop"]
            existing.recovery = normalized["recovery"]
            existing.detection_condition = normalized["detection_condition"]
            existing.trigger_logic = normalized["trigger_logic"]
            existing.possible_cause = normalized["possible_cause"]
            existing.solution = normalized["solution"]
            session.add(existing)
            updated += 1

        session.commit()

    print(f"after-sales fault codes imported: total={len(source_rows)} created={created} updated={updated} skipped={skipped}")


if __name__ == "__main__":
    main()