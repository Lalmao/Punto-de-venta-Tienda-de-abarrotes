"""Servidor web. Arranca con:  uvicorn app.main:app --reload"""
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from . import services
from .db import get_db
from .schemas import ClienteIn, CompraIn, ProductoIn, VentaIn

app = FastAPI(title="Abarrotes Placencia")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(STATIC / "index.html")


def _producto(p: m.Producto) -> dict:
    return {
        "ID_Producto": p.ID_Producto, "Nombre": p.Nombre, "Descripcion": p.Descripcion,
        "Precio_Venta": float(p.Precio_Venta), "Precio_Costo": float(p.Precio_Costo),
        "Stock_Actual": p.Stock_Actual, "Activo": p.Activo,
        "Categoria": p.categoria.Nombre, "ID_Proveedor": p.ID_Proveedor,
    }


# ---------- Catálogos (lectura) ----------
@app.get("/api/categorias")
def categorias(db: Session = Depends(get_db)):
    rows = db.scalars(select(m.Categoria).where(m.Categoria.Activo.is_(True))).all()
    return [{"ID_Categoria": c.ID_Categoria, "Nombre": c.Nombre} for c in rows]


@app.get("/api/proveedores")
def proveedores(db: Session = Depends(get_db)):
    rows = db.scalars(select(m.Proveedor).where(m.Proveedor.Activo.is_(True))).all()
    return [{"ID_Proveedor": p.ID_Proveedor, "Nombre_Empresa": p.Nombre_Empresa} for p in rows]


@app.get("/api/empleados")
def empleados(db: Session = Depends(get_db)):
    rows = db.scalars(select(m.Empleado).where(m.Empleado.Activo.is_(True))).all()
    return [{"ID_Empleado": e.ID_Empleado, "Nombre": e.Nombre, "Cargo": e.Cargo} for e in rows]


@app.get("/api/clientes")
def clientes(q: str = "", db: Session = Depends(get_db)):
    stmt = select(m.Cliente).where(m.Cliente.Activo.is_(True))
    if q:
        stmt = stmt.where(m.Cliente.Nombre.like(f"%{q}%") | m.Cliente.Telefono.like(f"%{q}%"))
    rows = db.scalars(stmt.limit(50)).all()
    return [{"ID_Cliente": c.ID_Cliente, "Nombre": c.Nombre, "Telefono": c.Telefono,
             "Puntos_Fidelidad": c.Puntos_Fidelidad} for c in rows]


@app.post("/api/clientes", status_code=201)
def crear_cliente(dto: ClienteIn, db: Session = Depends(get_db)):
    c = m.Cliente(Nombre=dto.nombre, Telefono=dto.telefono)
    db.add(c)
    db.commit()
    return {"ID_Cliente": c.ID_Cliente}


# ---------- Productos ----------
@app.get("/api/productos")
def productos(q: str = "", todos: bool = False, db: Session = Depends(get_db)):
    stmt = select(m.Producto)
    if not todos:
        stmt = stmt.where(m.Producto.Activo.is_(True))
    if q:
        stmt = stmt.where(m.Producto.Nombre.like(f"%{q}%"))
    return [_producto(p) for p in db.scalars(stmt.order_by(m.Producto.Nombre)).all()]


@app.get("/api/productos/stock-bajo")
def stock_bajo(umbral: int = 10, db: Session = Depends(get_db)):
    stmt = select(m.Producto).where(m.Producto.Activo.is_(True), m.Producto.Stock_Actual <= umbral)
    return [_producto(p) for p in db.scalars(stmt.order_by(m.Producto.Stock_Actual)).all()]


@app.post("/api/productos", status_code=201)
def crear_producto(dto: ProductoIn, db: Session = Depends(get_db)):
    if db.get(m.Categoria, dto.idCategoria) is None:
        raise HTTPException(400, "La categoría no existe")
    p = m.Producto(
        Nombre=dto.nombre, Descripcion=dto.descripcion, Precio_Venta=dto.precioVenta,
        Precio_Costo=dto.precioCosto, Stock_Actual=dto.stock,
        ID_Categoria=dto.idCategoria, ID_Proveedor=dto.idProveedor,
    )
    db.add(p)
    db.commit()
    return {"ID_Producto": p.ID_Producto}


@app.patch("/api/productos/{id_producto}/estado")
def cambiar_estado(id_producto: int, activo: bool, db: Session = Depends(get_db)):
    """Borrado lógico: nunca se borra, solo se desactiva."""
    p = db.get(m.Producto, id_producto)
    if p is None:
        raise HTTPException(404, "Producto no existe")
    p.Activo = activo
    db.commit()
    return {"ok": True}


# ---------- Ventas y compras ----------
@app.post("/api/ventas", status_code=201)
def registrar_venta(dto: VentaIn, db: Session = Depends(get_db)):
    try:
        resultado = services.crear_venta(db, dto)
        db.commit()
        return resultado
    except Exception:
        db.rollback()  # si algo falla, no se guarda nada
        raise


@app.get("/api/ventas")
def listar_ventas(db: Session = Depends(get_db)):
    rows = db.scalars(select(m.Venta).order_by(m.Venta.ID_Venta.desc()).limit(100)).all()
    return [{
        "ID_Venta": v.ID_Venta, "Fecha_Hora": v.Fecha_Hora.isoformat(sep=" ", timespec="minutes"),
        "Total": float(v.Total), "Metodo_Pago": v.Metodo_Pago, "Empleado": v.empleado.Nombre,
        "Cliente": v.cliente.Nombre if v.cliente else "Público general",
    } for v in rows]


@app.get("/api/ventas/{id_venta}")
def detalle_venta(id_venta: int, db: Session = Depends(get_db)):
    v = db.get(m.Venta, id_venta)
    if v is None:
        raise HTTPException(404, "Venta no existe")
    return {
        "ID_Venta": v.ID_Venta, "Total": float(v.Total),
        "lineas": [{"Producto": d.producto.Nombre, "Cantidad": d.Cantidad,
                    "Precio_Unitario": float(d.Precio_Unitario), "Subtotal": float(d.Subtotal)}
                   for d in v.detalles],
    }


@app.post("/api/compras", status_code=201)
def registrar_compra(dto: CompraIn, db: Session = Depends(get_db)):
    try:
        resultado = services.crear_compra(db, dto)
        db.commit()
        return resultado
    except Exception:
        db.rollback()
        raise


@app.get("/api/compras")
def listar_compras(db: Session = Depends(get_db)):
    rows = db.scalars(select(m.Compra).order_by(m.Compra.ID_Compra.desc()).limit(100)).all()
    return [{
        "ID_Compra": c.ID_Compra, "Fecha_Hora": c.Fecha_Hora.isoformat(sep=" ", timespec="minutes"),
        "Total": float(c.Total), "Num_Factura": c.Num_Factura,
        "Proveedor": c.proveedor.Nombre_Empresa, "Empleado": c.empleado.Nombre,
    } for c in rows]
