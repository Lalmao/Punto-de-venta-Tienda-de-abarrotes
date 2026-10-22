"""Diagnóstico y la conexión extra a PostgreSQL: estado, comparación de conteos y vista de tablas."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text

from . import models as m
from .admin_core import (MYSQL_BIN_DIR, NOMBRE_BD, PG_BIN_DIR, BACKUP_DIR, buscar_binario,
                         engine_mysql_admin, engine_pg, msg_db, requiere_admin)

router = APIRouter(prefix="/api/admin", dependencies=[Depends(requiere_admin)])
ESQUEMA = {t.name: [c.name for c in t.columns] for t in m.Base.metadata.sorted_tables}


def _probar(fabrica, sql):
    try:
        with fabrica().connect() as c:
            return {"ok": True, "detalle": str(c.execute(text(sql)).scalar())[:60]}
    except HTTPException as e:
        return {"ok": False, "detalle": e.detail}
    except Exception as e:
        return {"ok": False, "detalle": msg_db(e)[:200]}


@router.get("/estado")
def estado():
    herramientas = {n: buscar_binario(n, d) for n, d in [
        ("mysqldump", MYSQL_BIN_DIR), ("mysql", MYSQL_BIN_DIR),
        ("pg_dump", PG_BIN_DIR), ("psql", PG_BIN_DIR)]}
    return {"mysql": _probar(engine_mysql_admin, "SELECT VERSION()"),
            "postgres": _probar(engine_pg, "SELECT version()"),
            "herramientas": herramientas, "base": NOMBRE_BD, "carpeta_respaldos": str(BACKUP_DIR)}


@router.get("/esquema")
def esquema():
    return ESQUEMA


@router.get("/bd/comparar")
def comparar():
    """Cuenta filas por tabla en MySQL y en PostgreSQL (la verificación de la migración)."""
    filas = []
    for t in ESQUEMA:
        fila = {"tabla": t, "mysql": None, "postgres": None}
        for motor, fabrica, sql in [
            ("mysql", engine_mysql_admin, f"SELECT COUNT(*) FROM `{NOMBRE_BD}`.`{t}`"),
            ("postgres", engine_pg, f'SELECT COUNT(*) FROM "{t.lower()}"'),
        ]:
            try:
                with fabrica().connect() as c:
                    fila[motor] = c.execute(text(sql)).scalar()
            except HTTPException as e:
                fila["error_" + motor] = e.detail
            except Exception as e:
                fila["error_" + motor] = msg_db(e)[:120]
        fila["coincide"] = fila["mysql"] is not None and fila["mysql"] == fila["postgres"]
        filas.append(fila)
    return filas


@router.get("/bd/tabla/{motor}/{tabla}")
def ver_tabla(motor: Literal["mysql", "postgres"], tabla: str, limite: int = 20):
    if tabla not in ESQUEMA:
        raise HTTPException(404, "Tabla no existe")
    limite = max(1, min(limite, 200))
    if motor == "mysql":
        eng, sql = engine_mysql_admin(), f"SELECT * FROM `{NOMBRE_BD}`.`{tabla}` LIMIT {limite}"
    else:
        eng, sql = engine_pg(), f'SELECT * FROM "{tabla.lower()}" LIMIT {limite}'
    try:
        with eng.connect() as c:
            r = c.execute(text(sql))
            return {"columnas": list(r.keys()), "filas": jsonable_encoder([list(x) for x in r.fetchall()])}
    except Exception as e:
        raise HTTPException(400, msg_db(e))
