"""Create or reset the default JD Energy administrator account.

Usage:
    ../.venv/bin/python init_admin.py
"""

from app.database import get_session, init_db
from app.main import hash_password
from app.models.portal import User
from sqlmodel import select

DEFAULT_USERNAME = "JDE"
DEFAULT_PASSWORD = "123"


def init_admin() -> None:
    init_db()
    with get_session() as session:
        admin = session.exec(select(User).where(User.username == DEFAULT_USERNAME)).first()
        if admin is None:
            admin = User(username=DEFAULT_USERNAME, password_hash=hash_password(DEFAULT_PASSWORD))
        admin.password_hash = hash_password(DEFAULT_PASSWORD)
        admin.role = "admin"
        admin.is_staff = True
        admin.is_active = True
        admin.customer_name = admin.customer_name or "JD Energy"
        admin.customer_company = admin.customer_company or "JD Energy"
        session.add(admin)
        session.commit()
        print(f"Default admin ready: {DEFAULT_USERNAME}")


if __name__ == "__main__":
    init_admin()
