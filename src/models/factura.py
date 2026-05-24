"""
Modelo: Factura y LineaFactura
Representa el documento de venta y sus líneas de detalle.
Aplica SRP y OCP (abierto a extensión, cerrado a modificación).
"""
from dataclasses import dataclass, field, asdict
from datetime import date
from enum import Enum
from typing import List


class EstadoFactura(str, Enum):
    """Estados posibles del ciclo de vida de una factura."""
    PENDIENTE = "PENDIENTE"
    PAGADA = "PAGADA"
    VENCIDA = "VENCIDA"
    ANULADA = "ANULADA"

@dataclass
class LineaFactura:
    """
    Línea de detalle dentro de una factura.

    Atributos:
        id_producto (str): Referencia al producto facturado.
        nombre_producto (str): Nombre snapshot al momento de la factura.
        cantidad (int): Unidades vendidas.
        precio_unitario (float): Precio al momento de la venta.
        costo_unitario (float): Costo al momento de la venta (para ROA).
    """
    id_producto: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    costo_unitario: float = 0.0

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise ValueError("La cantidad en línea de factura debe ser positiva.")
        if self.precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo.")

    @property
    def subtotal(self) -> float:
        """Valor total de la línea = cantidad × precio."""
        return self.cantidad * self.precio_unitario

    @property
    def costo_total(self) -> float:
        """Costo total de la línea = cantidad × costo."""
        return self.cantidad * self.costo_unitario

    @property
    def utilidad_bruta(self) -> float:
        """Utilidad bruta de la línea = subtotal - costo_total."""
        return self.subtotal - self.costo_total

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "LineaFactura":
        return cls(
            id_producto=data["id_producto"],
            nombre_producto=data["nombre_producto"],
            cantidad=data["cantidad"],
            precio_unitario=data["precio_unitario"],
            costo_unitario=data.get("costo_unitario", 0.0),
        )