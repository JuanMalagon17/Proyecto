"""
Modelo: Factura y LineaFactura
Representa el documento de venta y sus líneas de detalle.
Aplica SRP y OCP (abierto a extensión, cerrado a modificación).
"""
from dataclasses import dataclass, field, asdict
from datetime import date
from enum import Enum
from typing import Any, List, cast


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

    def to_dict(self) -> dict[str, Any]:
        # Especificamos dict[str, Any] para evitar 'MissingTypeArgument'
        res: dict[str, Any] = asdict(self)
        return res

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LineaFactura":
        # Aseguramos el tipo extrayendo explícitamente los valores para evitar 'UnknownArgumentType'
        return cls(
            id_producto=str(data["id_producto"]),
            nombre_producto=str(data["nombre_producto"]),
            cantidad=int(data["cantidad"]),
            precio_unitario=float(data["precio_unitario"]),
            costo_unitario=float(data.get("costo_unitario", 0.0)),
        )


@dataclass
class Factura:
    """
    Entidad principal de dominio: Factura de venta.

    Atributos:
        id_factura (str): Número único de la factura.
        id_cliente (str): Cliente al que se emite.
        nombre_cliente (str): Nombre snapshot del cliente.
        fecha_emision (str): Fecha de emisión (ISO 8601: YYYY-MM-DD).
        fecha_vencimiento (str): Fecha límite de pago.
        lineas (List[LineaFactura]): Detalle de productos/servicios.
        estado (EstadoFactura): Estado actual de la factura.
        notes (str): Observaciones adicionales.
    """
    id_factura: str
    id_cliente: str
    nombre_cliente: str
    fecha_emision: str
    fecha_vencimiento: str
    lineas: List[LineaFactura] = field(default_factory=list[LineaFactura])
    estado: EstadoFactura = EstadoFactura.PENDIENTE
    notas: str = ""

    def __post_init__(self) -> None:
        if not self.id_factura or not self.id_factura.strip():
            raise ValueError("El id_factura no puede estar vacío.")
        if not self.id_cliente or not self.id_cliente.strip():
            raise ValueError("El id_cliente no puede estar vacío.")
        
        # Evitamos 'UnnecessaryIsInstance' comparando el tipo exacto directamente
        if type(self.estado) is str:
            estado_enum = EstadoFactura(self.estado)
            object.__setattr__(self, "estado", estado_enum)

    # ------------------------------------------------------------------ #
    # Métricas financieras
    # ------------------------------------------------------------------ #
    @property
    def total(self) -> float:
        """Valor total de la factura (suma de subtotales)."""
        return sum(l.subtotal for l in self.lineas)

    @property
    def costo_total(self) -> float:
        """Costo total de todos los productos facturados."""
        return sum(l.costo_total for l in self.lineas)

    @property
    def utilidad_bruta(self) -> float:
        """Utilidad bruta = total - costo_total."""
        return self.total - self.costo_total

    @property
    def margen_bruto_porcentual(self) -> float:
        """Margen bruto % sobre ventas."""
        if self.total == 0:
            return 0.0
        return (self.utilidad_bruta / self.total) * 100

    @property
    def esta_vencida(self) -> bool:
        """True si la fecha de vencimiento ya pasó y la factura no está pagada."""
        hoy = date.today().isoformat()
        return (
            self.estado == EstadoFactura.PENDIENTE
            and self.fecha_vencimiento < hoy
        )

    # ------------------------------------------------------------------ #
    # Operaciones
    # ------------------------------------------------------------------ #
    def agregar_linea(self, linea: LineaFactura) -> None:
        """Agrega una línea de detalle a la factura."""
        if self.estado != EstadoFactura.PENDIENTE:
            raise ValueError(
                f"No se puede modificar una factura en estado '{self.estado.value}'."
            )
        self.lineas.append(linea)

    def marcar_pagada(self) -> None:
        if self.estado != EstadoFactura.PENDIENTE:
            raise ValueError("Solo se puede pagar una factura PENDIENTE.")
        self.estado = EstadoFactura.PAGADA

    def anular(self) -> None:
        if self.estado == EstadoFactura.ANULADA:
            raise ValueError("La factura ya está anulada.")
        self.estado = EstadoFactura.ANULADA

    # ------------------------------------------------------------------ #
    # Serialización / Deserialización
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict[str, Any]:
        # Declaramos explícitamente dict[str, Any] para resolver los retornos parciales
        data: dict[str, Any] = {
            "id_factura": self.id_factura,
            "id_cliente": self.id_cliente,
            "nombre_cliente": self.nombre_cliente,
            "fecha_emision": self.fecha_emision,
            "fecha_vencimiento": self.fecha_vencimiento,
            "lineas": [l.to_dict() for l in self.lineas],
            "estado": self.estado.value,
            "notas": self.notas,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Factura":
        # Aseguramos que sea una lista de objetos Any originalmente
        lineas_raw: List[Any] = data.get("lineas", []) if isinstance(data.get("lineas"), list) else []
            
        lineas: List[LineaFactura] = []
        for elemento in lineas_raw:
            if isinstance(elemento, dict):
                # Al castear el elemento aquí, garantizamos que no haya rastros de Unknown
                sub_dict: dict[str, Any] = cast(dict[str, Any], elemento)
                lineas.append(LineaFactura.from_dict(sub_dict))
        
        return cls(
            id_factura=str(data["id_factura"]),
            id_cliente=str(data["id_cliente"]),
            nombre_cliente=str(data["nombre_cliente"]),
            fecha_emision=str(data["fecha_emision"]),
            fecha_vencimiento=str(data["fecha_vencimiento"]),
            lineas=lineas,
            estado=EstadoFactura(data.get("estado", "PENDIENTE")),
            notas=str(data.get("notas", "")),
        )

    def __str__(self) -> str:
        return (
            f"Factura [{self.id_factura}] - Cliente: {self.nombre_cliente} | "
            f"Total: ${self.total:,.2f} | Estado: {self.estado.value}"
        )

    def __repr__(self) -> str:
        return f"Factura(id='{self.id_factura}', cliente='{self.id_cliente}', total={self.total})"