"""Las 9 tablas del modelo relacional, escritas como clases de Python."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Categoria(Base):
    __tablename__ = "CATEGORIA"
    ID_Categoria: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(50))
    Descripcion: Mapped[Optional[str]] = mapped_column(String(255))
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Proveedor(Base):
    __tablename__ = "PROVEEDOR"
    ID_Proveedor: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    NIF_RFC: Mapped[str] = mapped_column(String(20), unique=True)
    Nombre_Empresa: Mapped[str] = mapped_column(String(100))
    Telefono: Mapped[Optional[str]] = mapped_column(String(20))
    Contacto: Mapped[Optional[str]] = mapped_column(String(100))
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Producto(Base):
    __tablename__ = "PRODUCTO"
    ID_Producto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(100))
    Descripcion: Mapped[Optional[str]] = mapped_column(String(255))
    Precio_Venta: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    Precio_Costo: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    Stock_Actual: Mapped[int] = mapped_column(Integer, default=0)
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ID_Categoria: Mapped[int] = mapped_column(ForeignKey("CATEGORIA.ID_Categoria"))
    ID_Proveedor: Mapped[Optional[int]] = mapped_column(ForeignKey("PROVEEDOR.ID_Proveedor"))
    categoria: Mapped["Categoria"] = relationship()


class Cliente(Base):
    __tablename__ = "CLIENTE"
    ID_Cliente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(100))
    Telefono: Mapped[Optional[str]] = mapped_column(String(20))
    Puntos_Fidelidad: Mapped[int] = mapped_column(Integer, default=0)
    Fecha_Registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Empleado(Base):
    __tablename__ = "EMPLEADO"
    ID_Empleado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Nombre: Mapped[str] = mapped_column(String(100))
    Cargo: Mapped[str] = mapped_column(String(50))
    Turno: Mapped[str] = mapped_column(Enum("MATUTINO", "VESPERTINO", "NOCTURNO", name="turno"))
    Activo: Mapped[bool] = mapped_column(Boolean, default=True)


class Venta(Base):
    __tablename__ = "VENTA"
    ID_Venta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Fecha_Hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    Total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    Metodo_Pago: Mapped[str] = mapped_column(
        Enum("EFECTIVO", "TARJETA_DEBITO", "TARJETA_CREDITO", "TRANSFERENCIA", name="metodo_pago")
    )
    ID_Cliente: Mapped[Optional[int]] = mapped_column(ForeignKey("CLIENTE.ID_Cliente"))
    ID_Empleado: Mapped[int] = mapped_column(ForeignKey("EMPLEADO.ID_Empleado"))
    cliente: Mapped[Optional["Cliente"]] = relationship()
    empleado: Mapped["Empleado"] = relationship()
    detalles: Mapped[list["DetalleVenta"]] = relationship()


class DetalleVenta(Base):
    __tablename__ = "DETALLE_VENTA"
    ID_Venta: Mapped[int] = mapped_column(ForeignKey("VENTA.ID_Venta"), primary_key=True)
    ID_Producto: Mapped[int] = mapped_column(ForeignKey("PRODUCTO.ID_Producto"), primary_key=True)
    Cantidad: Mapped[int] = mapped_column(Integer)
    Precio_Unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    Subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    producto: Mapped["Producto"] = relationship()


class Compra(Base):
    __tablename__ = "COMPRA"
    ID_Compra: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Fecha_Hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    Total: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    Num_Factura: Mapped[str] = mapped_column(String(30))
    ID_Proveedor: Mapped[int] = mapped_column(ForeignKey("PROVEEDOR.ID_Proveedor"))
    ID_Empleado: Mapped[int] = mapped_column(ForeignKey("EMPLEADO.ID_Empleado"))
    proveedor: Mapped["Proveedor"] = relationship()
    empleado: Mapped["Empleado"] = relationship()


class DetalleCompra(Base):
    __tablename__ = "DETALLE_COMPRA"
    ID_Compra: Mapped[int] = mapped_column(ForeignKey("COMPRA.ID_Compra"), primary_key=True)
    ID_Producto: Mapped[int] = mapped_column(ForeignKey("PRODUCTO.ID_Producto"), primary_key=True)
    Cantidad: Mapped[int] = mapped_column(Integer)
    Costo_Unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    Subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
