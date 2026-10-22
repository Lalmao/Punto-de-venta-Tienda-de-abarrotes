"""Conexión a la base de datos. Lee los datos del archivo .env"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:TU_PASSWORD@localhost:3306/abarrotes_placencia",
)
USAR_TRIGGERS_BD = os.getenv("USAR_TRIGGERS_BD", "false").lower() == "true"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """Entrega una sesión de base de datos por cada petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
