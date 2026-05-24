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
