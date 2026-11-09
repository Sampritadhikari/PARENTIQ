from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine


def init_db(db: Session = None) -> None:
    # Creates all tables declared on Base
    Base.metadata.create_all(bind=engine)

