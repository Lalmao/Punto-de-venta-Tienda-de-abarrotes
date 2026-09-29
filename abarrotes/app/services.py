"""Lógica de negocio: registrar ventas y compras.
Todo ocurre en UNA transacción: si algo falla, no se guarda nada."""
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from .db import USAR_TRIGGERS_BD
from .schemas import CompraIn, VentaIn


def _bloquear_producto(db: Session, id_producto: int) -> m.Producto:
    """Trae el producto y lo bloquea para que dos ventas simultáneas no se pisen el stock."""
    p = db.execute(
        select(m.Producto).where(m.Producto.ID_Producto == id_producto).with_for_update()
    ).scalar_one_or_none()
    if p is None:
        raise HTTPException(404, f"El producto {id_producto} no existe")
    return p


def crear_venta(db: Session, dto: VentaIn) -> dict:
    # Si un producto viene repetido, se suman las cantidades (por la llave compuesta)
    lineas: dict[int, int] = {}
    for l in dto.lineas:
        lineas[l.idProducto] = lineas.get(l.idProducto, 0) + l.cantidad

    emp = db.get(m.Empleado, dto.idEmpleado)
    if emp is None or not emp.Activo:
        raise HTTPException(400, "Empleado no válido o inactivo")

    cliente = None
    if dto.idCliente is not None:
        cliente = db.get(m.Cliente, dto.idCliente)
        if cliente is None or not cliente.Activo:
            raise HTTPException(400, "Cliente no válido o inactivo")

    venta = m.Venta(
        Metodo_Pago=dto.metodoPago,
        ID_Cliente=dto.idCliente,
        ID_Empleado=dto.idEmpleado,
        Total=Decimal("0.00"),
    )
    db.add(venta)
    db.flush()  # así se genera el folio (ID_Venta)

    total = Decimal("0.00")
    for id_prod in sorted(lineas):  # ordenadas para evitar bloqueos cruzados
        cant = lineas[id_prod]
        p = _bloquear_producto(db, id_prod)
        if not p.Activo:
            raise HTTPException(409, f"'{p.Nombre}' está inactivo y no se puede vender")
        if p.Stock_Actual < cant:
            raise HTTPException(
                409, f"Stock insuficiente de '{p.Nombre}': hay {p.Stock_Actual}, se piden {cant}"
            )
        precio = p.Precio_Venta  # el precio lo pone el servidor, nunca la pantalla
        subtotal = precio * cant
        db.add(m.DetalleVenta(
            ID_Venta=venta.ID_Venta, ID_Producto=id_prod,
            Cantidad=cant, Precio_Unitario=precio, Subtotal=subtotal,
        ))
        if not USAR_TRIGGERS_BD:
            p.Stock_Actual -= cant
        total += subtotal

    puntos = 0
    if not USAR_TRIGGERS_BD:
        venta.Total = total
        if cliente is not None:
            puntos = int(total // 10)  # 1 punto por cada $10
            cliente.Puntos_Fidelidad += puntos
    db.flush()
    return {"idVenta": venta.ID_Venta, "total": float(total), "puntosGanados": puntos}


def crear_compra(db: Session, dto: CompraIn) -> dict:
    emp = db.get(m.Empleado, dto.idEmpleado)
    if emp is None or not emp.Activo:
        raise HTTPException(400, "Empleado no válido o inactivo")
    prov = db.get(m.Proveedor, dto.idProveedor)
    if prov is None or not prov.Activo:
        raise HTTPException(400, "Proveedor no válido o inactivo")

    repetida = db.execute(
        select(m.Compra.ID_Compra).where(
            m.Compra.ID_Proveedor == dto.idProveedor, m.Compra.Num_Factura == dto.numFactura
        )
    ).first()
    if repetida:
        raise HTTPException(409, "Ese proveedor ya tiene una compra con ese número de factura")

    # Si un producto viene repetido: se suman cantidades y se usa el último costo
    lineas: dict[int, dict] = {}
    for l in dto.lineas:
        if l.idProducto in lineas:
            lineas[l.idProducto]["cantidad"] += l.cantidad
            lineas[l.idProducto]["costo"] = l.costoUnitario
        else:
            lineas[l.idProducto] = {"cantidad": l.cantidad, "costo": l.costoUnitario}

    compra = m.Compra(
        Num_Factura=dto.numFactura, ID_Proveedor=dto.idProveedor,
        ID_Empleado=dto.idEmpleado, Total=Decimal("0.00"),
    )
    db.add(compra)
    db.flush()

    total = Decimal("0.00")
    for id_prod in sorted(lineas):
        cant, costo = lineas[id_prod]["cantidad"], lineas[id_prod]["costo"]
        p = _bloquear_producto(db, id_prod)
        subtotal = costo * cant
        db.add(m.DetalleCompra(
            ID_Compra=compra.ID_Compra, ID_Producto=id_prod,
            Cantidad=cant, Costo_Unitario=costo, Subtotal=subtotal,
        ))
        if not USAR_TRIGGERS_BD:
            p.Stock_Actual += cant
        if dto.actualizarCosto:
            p.Precio_Costo = costo
        total += subtotal

    if not USAR_TRIGGERS_BD:
        compra.Total = total
    db.flush()
    return {"idCompra": compra.ID_Compra, "total": float(total)}
