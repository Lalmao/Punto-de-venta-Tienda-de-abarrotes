"""Administración de usuarios MySQL: crear, permisos (base / tabla / columna), bloquear, eliminar."""
import re

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError

from .admin_core import (ADMIN_DATABASE_URL, BACKUP_DATABASE_URL, NOMBRE_BD, auditar,
                         engine_mysql_admin, msg_db, requiere_admin)
from .conexiones import ESQUEMA
from .db import DATABASE_URL

router = APIRouter(prefix="/api/admin/usuarios", dependencies=[Depends(requiere_admin)])

RE_USUARIO = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,31}$")
RE_HOST = re.compile(r"^(%|localhost|[A-Za-z0-9_.%\-]{1,60})$")
BASE_OK = {"SELECT", "INSERT", "UPDATE", "DELETE", "LOCK TABLES", "SHOW VIEW", "TRIGGER", "EXECUTE", "ALL PRIVILEGES"}
TABLA_OK = {"SELECT", "INSERT", "UPDATE", "DELETE"}
COL_OK = {"SELECT", "INSERT", "UPDATE"}
SISTEMA = {"root", "mysql.sys", "mysql.session", "mysql.infoschema", "debian-sys-maint", "mariadb.sys"}


def _cuentas_protegidas():
    nombres = set(SISTEMA)
    for u in (DATABASE_URL, ADMIN_DATABASE_URL, BACKUP_DATABASE_URL):
        if u:
            nombres.add((make_url(u).username or "").lower())
    return nombres


# ---- Plantillas: los roles de la actividad 4.5 ----
PLANTILLAS = [
    {"id": "administrador", "nombre": "Administrador", "usuario_sugerido": "admin_abarrotes",
     "descripcion": "Todos los privilegios sobre la base, con GRANT OPTION",
     "permisos": {"base": ["ALL PRIVILEGES"], "con_grant_option": True}},
    {"id": "gerente", "nombre": "Gerencia", "usuario_sugerido": "gerente",
     "descripcion": "SELECT, INSERT, UPDATE, DELETE en toda la base (sin DDL)",
     "permisos": {"base": ["SELECT", "INSERT", "UPDATE", "DELETE"]}},
    {"id": "encargado", "nombre": "Encargado de tienda", "usuario_sugerido": "encargado",
     "descripcion": "Lee todo; INSERT/UPDATE en PRODUCTO, CATEGORIA, COMPRA y DETALLE_COMPRA",
     "permisos": {"base": ["SELECT"], "tablas": {t: ["INSERT", "UPDATE"] for t in
                  ["PRODUCTO", "CATEGORIA", "COMPRA", "DETALLE_COMPRA"]}}},
    {"id": "cajero", "nombre": "Cajero", "usuario_sugerido": "cajero_mat",
     "descripcion": "SELECT en PRODUCTO y CLIENTE; INSERT en VENTA y DETALLE_VENTA",
     "permisos": {"tablas": {"PRODUCTO": ["SELECT"], "CLIENTE": ["SELECT"],
                             "VENTA": ["INSERT"], "DETALLE_VENTA": ["INSERT"]}}},
    {"id": "cajero_puntos", "nombre": "Cajero con puntos", "usuario_sugerido": "cajero_vesp",
     "descripcion": "Como cajero, más UPDATE solo en la columna Puntos_Fidelidad",
     "permisos": {"tablas": {"PRODUCTO": ["SELECT"], "CLIENTE": ["SELECT"],
                             "VENTA": ["INSERT"], "DETALLE_VENTA": ["INSERT"]},
                  "columnas": {"CLIENTE": {"UPDATE": ["Puntos_Fidelidad"]}}}},
    {"id": "reponedor", "nombre": "Reponedor", "usuario_sugerido": "reponedor",
     "descripcion": "SELECT en PRODUCTO y PROVEEDOR; INSERT en COMPRA y DETALLE_COMPRA; UPDATE solo Stock_Actual",
     "permisos": {"tablas": {"PRODUCTO": ["SELECT"], "PROVEEDOR": ["SELECT"],
                             "COMPRA": ["INSERT"], "DETALLE_COMPRA": ["INSERT"]},
                  "columnas": {"PRODUCTO": {"UPDATE": ["Stock_Actual"]}}}},
    {"id": "auditor", "nombre": "Contabilidad / Auditor", "usuario_sugerido": "auditor",
     "descripcion": "Solo SELECT en toda la base", "permisos": {"base": ["SELECT"]}},
    {"id": "analista", "nombre": "Análisis de ventas", "usuario_sugerido": "analista",
     "descripcion": "SELECT solo en VENTA, DETALLE_VENTA, PRODUCTO y CATEGORIA (sin datos de clientes)",
     "permisos": {"tablas": {t: ["SELECT"] for t in ["VENTA", "DETALLE_VENTA", "PRODUCTO", "CATEGORIA"]}}},
    {"id": "respaldos", "nombre": "Usuario de respaldos", "usuario_sugerido": "respaldos",
     "descripcion": "SELECT, LOCK TABLES, SHOW VIEW y TRIGGER (lo que necesita mysqldump)",
     "permisos": {"base": ["SELECT", "LOCK TABLES", "SHOW VIEW", "TRIGGER"]}},
]


class Permisos(BaseModel):
    base: list[str] = []
    con_grant_option: bool = False
    tablas: dict[str, list[str]] = {}
    columnas: dict[str, dict[str, list[str]]] = {}


class UsuarioNuevo(BaseModel):
    usuario: str
    host: str = "localhost"
    password: str = Field(min_length=8, max_length=64)
    permisos: Permisos


class CambioPermisos(BaseModel):
    usuario: str
    host: str = "localhost"
    permisos: Permisos


class CambioPassword(BaseModel):
    usuario: str
    host: str = "localhost"
    password: str = Field(min_length=8, max_length=64)


class Bloqueo(BaseModel):
    usuario: str
    host: str = "localhost"
    bloquear: bool


def _cuenta(usuario: str, host: str):
    if not RE_USUARIO.match(usuario):
        raise HTTPException(400, "Usuario: 3-32 caracteres, empieza con letra; solo letras, números y _")
    if not RE_HOST.match(host):
        raise HTTPException(400, "Host no válido (usa localhost, % o una IP)")
    return usuario, host


def _modificable(usuario: str):
    if usuario.lower() in _cuentas_protegidas():
        raise HTTPException(400, f"'{usuario}' es una cuenta protegida (del sistema o de la propia aplicación)")


def _sentencias(p: Permisos) -> list[str]:
    """Convierte los permisos en GRANT. Todo identificador pasa por lista blanca (anti inyección)."""
    db = NOMBRE_BD
    if not re.fullmatch(r"[A-Za-z0-9_]+", db or ""):
        raise HTTPException(500, "Nombre de base de datos no válido en DATABASE_URL")
    q = lambda x: f"`{x}`"
    sents = []
    base = [x.upper() for x in p.base]
    if base:
        if any(x not in BASE_OK for x in base):
            raise HTTPException(400, "Privilegio de base no permitido")
        if "ALL PRIVILEGES" in base:
            base = ["ALL PRIVILEGES"]
        grant = " WITH GRANT OPTION" if (p.con_grant_option and base == ["ALL PRIVILEGES"]) else ""
        sents.append(f"GRANT {', '.join(base)} ON {q(db)}.* TO %s@%s{grant}")
    for t, privs in p.tablas.items():
        privs = [x.upper() for x in privs]
        if t not in ESQUEMA or any(x not in TABLA_OK for x in privs):
            raise HTTPException(400, f"Permiso de tabla no válido: {t}")
        if privs:
            sents.append(f"GRANT {', '.join(privs)} ON {q(db)}.{q(t)} TO %s@%s")
    for t, porpriv in p.columnas.items():
        if t not in ESQUEMA:
            raise HTTPException(400, f"Tabla no válida: {t}")
        for priv, cols in porpriv.items():
            priv = priv.upper()
            if priv not in COL_OK or any(c not in ESQUEMA[t] for c in cols):
                raise HTTPException(400, f"Permiso de columna no válido en {t}")
            if cols:
                sents.append(f"GRANT {priv} ({', '.join(q(c) for c in cols)}) ON {q(db)}.{q(t)} TO %s@%s")
    if not sents:
        raise HTTPException(400, "Elige al menos un permiso")
    return sents


@router.get("/plantillas")
def plantillas():
    return [{**p, "permisos": {"base": [], "con_grant_option": False, "tablas": {}, "columnas": {}, **p["permisos"]}}
            for p in PLANTILLAS]


@router.get("")
def listar():
    protegidas = _cuentas_protegidas()
    try:
        with engine_mysql_admin().connect() as c:
            filas = c.exec_driver_sql("SELECT user, host, account_locked FROM mysql.user ORDER BY user, host").all()
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))
    return [{"usuario": u, "host": h, "bloqueado": b == "Y", "protegido": u.lower() in protegidas}
            for u, h, b in filas]


@router.get("/grants")
def ver_grants(usuario: str, host: str = "localhost"):
    _cuenta(usuario, host)
    try:
        with engine_mysql_admin().connect() as c:
            return [r[0] for r in c.exec_driver_sql("SHOW GRANTS FOR %s@%s", (usuario, host)).all()]
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))


@router.post("", status_code=201)
def crear(dto: UsuarioNuevo):
    u, h = _cuenta(dto.usuario, dto.host)
    _modificable(u)
    sents = _sentencias(dto.permisos)  # se valida TODO antes de crear la cuenta
    try:
        with engine_mysql_admin().begin() as c:
            c.exec_driver_sql("CREATE USER %s@%s IDENTIFIED BY %s", (u, h, dto.password))
            try:
                for s in sents:
                    c.exec_driver_sql(s, (u, h))
            except Exception:
                c.exec_driver_sql("DROP USER %s@%s", (u, h))  # no dejar cuentas a medias
                raise
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))
    auditar("CREAR_USUARIO", f"{u}@{h} ({len(sents)} grants)")
    return {"ok": True}


@router.post("/permisos")
def reemplazar_permisos(dto: CambioPermisos):
    u, h = _cuenta(dto.usuario, dto.host)
    _modificable(u)
    sents = _sentencias(dto.permisos)
    try:
        with engine_mysql_admin().begin() as c:
            c.exec_driver_sql("REVOKE ALL PRIVILEGES, GRANT OPTION FROM %s@%s", (u, h))
            for s in sents:
                c.exec_driver_sql(s, (u, h))
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))
    auditar("CAMBIAR_PERMISOS", f"{u}@{h}")
    return {"ok": True}


@router.post("/password")
def cambiar_password(dto: CambioPassword):
    u, h = _cuenta(dto.usuario, dto.host)
    _modificable(u)
    try:
        with engine_mysql_admin().begin() as c:
            c.exec_driver_sql("ALTER USER %s@%s IDENTIFIED BY %s", (u, h, dto.password))
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))
    auditar("CAMBIAR_PASSWORD", f"{u}@{h}")
    return {"ok": True}


@router.post("/bloqueo")
def bloquear(dto: Bloqueo):
    u, h = _cuenta(dto.usuario, dto.host)
    _modificable(u)
    estado = "LOCK" if dto.bloquear else "UNLOCK"
    try:
        with engine_mysql_admin().begin() as c:
            c.exec_driver_sql(f"ALTER USER %s@%s ACCOUNT {estado}", (u, h))
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))
    auditar("BLOQUEAR" if dto.bloquear else "DESBLOQUEAR", f"{u}@{h}")
    return {"ok": True}


@router.delete("")
def eliminar(usuario: str, host: str = "localhost"):
    u, h = _cuenta(usuario, host)
    _modificable(u)
    try:
        with engine_mysql_admin().begin() as c:
            c.exec_driver_sql("DROP USER %s@%s", (u, h))
    except DBAPIError as e:
        raise HTTPException(400, msg_db(e))
    auditar("ELIMINAR_USUARIO", f"{u}@{h}")
    return {"ok": True}
