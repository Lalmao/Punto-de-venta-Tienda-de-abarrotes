"""Respaldo y restauración. MySQL: mysqldump / mysql. PostgreSQL: pg_dump / psql."""
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.engine import make_url

from .admin_core import (ADMIN_DATABASE_URL, BACKUP_DATABASE_URL, BACKUP_DIR, MYSQL_BIN_DIR,
                         NOMBRE_BD, PG_BIN_DIR, PG_DATABASE_URL, auditar, buscar_binario,
                         requiere_admin)

router = APIRouter(prefix="/api/admin/respaldos", dependencies=[Depends(requiere_admin)])
PATRON = re.compile(r"^[A-Za-z0-9_\-]+_(mysql|pg)_\d{8}_\d{6}\.sql$")


class RespaldoIn(BaseModel):
    motor: Literal["mysql", "postgres"]


class RestaurarIn(BaseModel):
    archivo: str
    confirmacion: str


def _bin(nombre, carpeta):
    exe = buscar_binario(nombre, carpeta)
    if not exe:
        raise HTTPException(
            503, f"No encuentro '{nombre}'. Agrega su carpeta al PATH o define MYSQL_BIN_DIR / PG_BIN_DIR en .env")
    return exe


def _url(*candidatas):
    for c in candidatas:
        if c:
            return make_url(c)
    raise HTTPException(503, "Falta la URL de conexión en el archivo .env")


@contextmanager
def _opciones_mysql(url):
    """Archivo temporal con usuario/contraseña, para no ponerlos en la línea de comandos."""
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False, encoding="utf-8") as f:
        pw = (url.password or "").replace("\\", "\\\\").replace('"', '\\"')
        f.write(f'[client]\nuser="{url.username}"\npassword="{pw}"\n'
                f'host="{url.host or "localhost"}"\nport={url.port or 3306}\n')
        ruta = f.name
    try:
        yield ruta
    finally:
        os.remove(ruta)


def _env_pg(url):
    return {**os.environ, "PGPASSWORD": url.password or "", "PGCLIENTENCODING": "UTF8"}


def _pg_args(exe, url):
    return [exe, "-h", url.host or "localhost", "-p", str(url.port or 5432),
            "-U", url.username, "-d", url.database, "--no-password"]


def _ejecutar(cmd, env=None, stdin=None):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, stdin=stdin, timeout=600)
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "La operación tardó demasiado y se canceló")
    if r.returncode != 0:
        raise HTTPException(500, (r.stderr or "Error desconocido").strip()[:600])


def _dump(motor: str, prefijo: str = "abarrotes"):
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = BACKUP_DIR / f"{prefijo}_{'mysql' if motor == 'mysql' else 'pg'}_{sello}.sql"
    try:
        if motor == "mysql":
            exe = _bin("mysqldump", MYSQL_BIN_DIR)
            url = _url(BACKUP_DATABASE_URL, ADMIN_DATABASE_URL)
            with _opciones_mysql(url) as cnf:
                _ejecutar([exe, f"--defaults-extra-file={cnf}", "--default-character-set=utf8mb4",
                           "--routines", "--triggers", "--single-transaction",
                           "--databases", NOMBRE_BD, f"--result-file={ruta}"])
        else:
            exe = _bin("pg_dump", PG_BIN_DIR)
            url = _url(PG_DATABASE_URL)
            _ejecutar(_pg_args(exe, url) + ["--clean", "--if-exists", "--no-owner",
                                            "--no-privileges", "-f", str(ruta)], env=_env_pg(url))
    except Exception:
        ruta.unlink(missing_ok=True)
        raise
    return ruta


def _resumen(ruta, motor):
    txt = ruta.read_text(encoding="utf-8", errors="replace")
    triggers = (len(re.findall(r"TRIGGER\s+`[^`]+`", txt)) if motor == "mysql"
                else len(re.findall(r"CREATE TRIGGER", txt)))
    return {"tablas": len(re.findall(r"CREATE TABLE", txt)), "triggers": triggers}


def _motor_de(nombre):
    return "mysql" if "_mysql_" in nombre else "postgres"


def _ruta_segura(nombre):
    if not PATRON.match(nombre):
        raise HTTPException(400, "Nombre de archivo no válido")
    ruta = BACKUP_DIR / nombre
    if not ruta.is_file():
        raise HTTPException(404, "El respaldo no existe")
    return ruta


@router.get("")
def listar():
    archivos = sorted(BACKUP_DIR.glob("*.sql"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [{"nombre": p.name, "motor": _motor_de(p.name), "kb": round(p.stat().st_size / 1024, 1),
             "fecha": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")}
            for p in archivos if PATRON.match(p.name)]


@router.post("", status_code=201)
def crear(dto: RespaldoIn):
    ruta = _dump(dto.motor)
    res = _resumen(ruta, dto.motor)
    auditar("RESPALDO", f"{dto.motor} -> {ruta.name}")
    return {"nombre": ruta.name, "kb": round(ruta.stat().st_size / 1024, 1), **res}


@router.post("/restaurar")
def restaurar(dto: RestaurarIn):
    if dto.confirmacion != "RESTAURAR":
        raise HTTPException(400, "Falta la confirmación")
    ruta = _ruta_segura(dto.archivo)
    motor = _motor_de(ruta.name)
    seguridad = _dump(motor, "pre_restauracion")  # red de seguridad antes de tocar nada
    if motor == "mysql":
        exe = _bin("mysql", MYSQL_BIN_DIR)
        url = _url(ADMIN_DATABASE_URL)
        with _opciones_mysql(url) as cnf, open(ruta, "rb") as f:
            _ejecutar([exe, f"--defaults-extra-file={cnf}", "--default-character-set=utf8mb4"], stdin=f)
    else:
        exe = _bin("psql", PG_BIN_DIR)
        url = _url(PG_DATABASE_URL)
        _ejecutar(_pg_args(exe, url) + ["-q", "-v", "ON_ERROR_STOP=1", "--single-transaction",
                                        "-f", str(ruta)], env=_env_pg(url))
    auditar("RESTAURACION", f"{ruta.name} (seguridad previa: {seguridad.name})")
    return {"ok": True, "respaldo_de_seguridad": seguridad.name}


@router.get("/{archivo}/descargar")
def descargar(archivo: str):
    ruta = _ruta_segura(archivo)
    auditar("DESCARGA", archivo)
    return FileResponse(ruta, filename=archivo, media_type="application/sql")


@router.delete("/{archivo}")
def eliminar(archivo: str):
    _ruta_segura(archivo).unlink()
    auditar("ELIMINAR_RESPALDO", archivo)
    return {"ok": True}
