from typing import Iterator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool
from utils.config import config

def getEngine():
    return create_engine(config.secrets.db_url, poolclass=NullPool)

def createSession() -> Iterator[Session]:
    """Create new database session. Yields: Database session. """
    with SessionFactory() as session:
        try:
            yield session
        except Exception as e:
            # rollback or other operation.
            session.rollback()
            raise e
        finally:
            session.close()

# create session factory to generate new database sessions
SessionFactory = sessionmaker(
    bind=getEngine(),
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)