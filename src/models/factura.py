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