from sqlmodel import Session

from db.models import Admin


def register_first_admin(session: Session, user_id: int) -> str:
    admin_count = session.query(Admin).count()
    existing = session.query(Admin).filter_by(user_id=user_id).first()
    if admin_count == 0:
        admin = Admin(user_id=user_id, is_superadmin=True)
        session.add(admin)
        session.commit()
        return "Registered as superadmin"
    if existing:
        return "Welcome back"
    return "Access restricted"
