"""Create or reset the default JD Energy super_admin and viewer accounts.

Usage:
    ../.venv/bin/python init_admin.py
"""

from app.database import init_db
from app.main import ensure_default_admin


def init_admin() -> None:
    init_db()
    ensure_default_admin()
    print("System accounts ready: admin, JDE")


if __name__ == "__main__":
    init_admin()
