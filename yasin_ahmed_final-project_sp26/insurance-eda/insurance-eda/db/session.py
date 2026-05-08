from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from config import Config

engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DATABASE_URL else {},
    pool_pre_ping=True,
    echo=False,
)

_SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(_SessionFactory)
Base = declarative_base()


def init_db():
    import app.models  # noqa: registers all ORM classes
    Base.metadata.create_all(engine)
