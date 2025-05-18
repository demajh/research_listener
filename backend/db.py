import os
from sqlalchemy import create_engine, orm, text
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = orm.sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- utility ---------------------------------------------------- #
def init_db():
    import models.user  # noqa: F401  (ensure model modules are imported)
    Base.metadata.create_all(bind=engine)
