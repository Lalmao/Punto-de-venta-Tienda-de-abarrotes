"""Piezas compartidas del panel de administración: clave, conexiones extra y bitácora."""
import os
import secrets
import shutil
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from fastapi import Header, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from .db import DATABASE_URL  # importar .db primero carga el archivo .env

ADMIN_KEY = os.getenv("ADMIN_KEY", "")
ADMIN_DATABASE_URL = os.getenv("ADMIN_DATABASE_URL", "")
BACKUP_DATABASE_URL = os.getenv("BACKUP_DATABASE_URL", "")
PG_DATABASE_URL = os.getenv("PG_DATABASE_URL", "")
MYSQL_BIN_DIR = os.getenv("MYSQL_BIN_DIR", "")
PG_BIN_DIR = os.getenv("PG_BIN_DIR", "")
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "respaldos")).resolve()
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
NOMBRE_BD = make_url(DATABASE_URL).database


def requiere_admin(x_admin_key: str | None = Header(default=None)):
    """Protege todo el panel: la pantalla manda la clave en cada petición."""
    if not ADMIN_KEY:
        raise HTTPException(503, "Panel deshabilitado: define ADMIN_KEY en el archivo .env")
    if not x_admin_key or not secrets.compare_digest(x_admin_key.encode(), ADMIN_KEY.encode()):
        raise HTTPException(401, "Clave de administrador incorrecta")


@lru_cache
def engine_mysql_admin():
    if not ADMIN_DATABASE_URL:
        raise HTTPException(503, "Falta ADMIN_DATABASE_URL en el archivo .env")
    return create_engine(ADMIN_DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})


@lru_cache
def engine_pg():
    """La conexión EXTRA a PostgreSQL."""
    if not PG_DATABASE_URL:
        raise HTTPException(503, "Falta PG_DATABASE_URL en el archivo .env")
    return create_engine(PG_DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})


def buscar_binario(nombre: str, carpeta: str = "") -> str | None:
    exe = nombre + (".exe" if os.name == "nt" else "")
    if carpeta and (Path(carpeta) / exe).exists():
        return str(Path(carpeta) / exe)
    return shutil.which(nombre)


def msg_db(e: Exception) -> str:
    """Saca el texto limpio del error de MySQL/PostgreSQL."""
    orig = getattr(e, "orig", e)
    args = getattr(orig, "args", None)
    return str(args[-1]) if args else str(orig)


def auditar(accion: str, detalle: str = ""):
    """Bitácora: quién hizo qué y cuándo (nunca se guardan contraseñas)."""
    with open(BACKUP_DIR / "auditoria.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {accion} | {detalle}\n")
