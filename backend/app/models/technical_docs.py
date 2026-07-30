from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


TECHNICAL_DOC_PRODUCT_SERIES = ["418", "250", "100C", "418/250"]

TECHNICAL_DOC_CATEGORIES = [
    "安装手册",
    "调试手册",
    "运维手册",
    "安装视频",
    "其他手册",
]


class TechnicalDoc(SQLModel, table=True):
    __tablename__ = "technical_docs"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_series: str = Field(index=True)
    category: str = Field(index=True)
    title: str
    file_url: str
    file_type: str = ""
    file_size: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


TECHNICAL_DOCS_SEED = [
    {
        "product_series": "418",
        "category": "安装手册",
        "title": "418 安装手册（示例）",
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "file_type": "application/pdf",
        "file_size": "13 KB",
    },
    {
        "product_series": "250",
        "category": "安装视频",
        "title": "250 安装教学视频（示例）",
        "file_url": "https://www.w3schools.com/html/mov_bbb.mp4",
        "file_type": "video/mp4",
        "file_size": "-",
    },
    {
        "product_series": "100C",
        "category": "调试手册",
        "title": "100C 调试手册（示例）",
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "file_type": "application/pdf",
        "file_size": "13 KB",
    },
    {
        "product_series": "100C",
        "category": "运维手册",
        "title": "100C 运维手册（示例）",
        "file_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "file_type": "application/pdf",
        "file_size": "13 KB",
    },
]