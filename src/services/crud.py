from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from src.services import ENGINE


Session = sessionmaker(bind=ENGINE)


@contextmanager
def create_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()