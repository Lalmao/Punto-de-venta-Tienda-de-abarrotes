"""Formas de los datos que llegan desde la pantalla (con validación automática)."""
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class LineaVenta(BaseModel):
    idProducto: int
    cantidad: int = Field(gt=0)


class VentaIn(BaseModel):
    idEmpleado: int
    idCliente: Optional[int] = None
    metodoPago: Literal["EFECTIVO", "TARJETA_DEBITO", "TARJETA_CREDITO", "TRANSFERENCIA"]
    lineas: list[LineaVenta] = Field(min_length=1)


class LineaCompra(BaseModel):
    idProducto: int
    cantidad: int = Field(gt=0)
    costoUnitario: Decimal = Field(ge=0)


class CompraIn(BaseModel):
    idProveedor: int
    idEmpleado: int
    numFactura: str = Field(min_length=1, max_length=30)
    actualizarCosto: bool = False
    lineas: list[LineaCompra] = Field(min_length=1)


class ProductoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precioVenta: Decimal = Field(ge=0)
    precioCosto: Decimal = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    idCategoria: int
    idProveedor: Optional[int] = None


class ClienteIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    telefono: Optional[str] = Field(default=None, max_length=20)
