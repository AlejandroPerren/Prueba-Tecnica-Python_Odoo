from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

# Construct the SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.MYSQL_CONFIG['user']}:{settings.MYSQL_CONFIG['password']}"
    f"@{settings.MYSQL_CONFIG['host']}:{settings.MYSQL_CONFIG.get('port', 3306)}"
    f"/{settings.MYSQL_CONFIG['database']}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function to get a database session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
