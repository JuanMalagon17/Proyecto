"""
Modelo: Producto
Representa la entidad Producto/Servicio en el catálogo de ventas.
Aplica principio SRP - solo modela los datos del producto.
"""
from dataclasses import dataclass, asdict


@dataclass
class Producto:
    """
    Entidad de dominio que representa un producto o servicio vendible.

    Atributos:
        id_producto (str): Código único del producto (SKU).
        nombre (str): Nombre del producto o servicio.
        descripcion (str): Descripción detallada.
        precio_unitario (float): Precio de venta por unidad.
        costo_unitario (float): Costo de adquisición/producción por unidad.
        stock (int): Unidades disponibles en inventario.
        activo (bool): Si el producto está disponible para venta.
    """
    id_producto: str
    nombre: str
    descripcion: str
    precio_unitario: float
    costo_unitario: float
    stock: int = 0
    activo: bool = True

    def __post_init__(self) -> None:
        if not self.id_producto or not self.id_producto.strip():
            raise ValueError("El id_producto no puede estar vacío.")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if self.precio_unitario < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        if self.costo_unitario < 0:
            raise ValueError("El costo unitario no puede ser negativo.")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo.")

    # ------------------------------------------------------------------ #
    # Serialización / Deserialización
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        return cls(
            id_producto=data["id_producto"],
            nombre=data["nombre"],
            descripcion=data["descripcion"],
            precio_unitario=data["precio_unitario"],
            costo_unitario=data["costo_unitario"],
            stock=data.get("stock", 0),
            activo=data.get("activo", True),
        )

    # ------------------------------------------------------------------ #
    # Métricas financieras del producto
    # ------------------------------------------------------------------ #
    @property
    def margen_bruto(self) -> float:
        """Margen bruto unitario = precio - costo."""
        return self.precio_unitario - self.costo_unitario

    @property
    def margen_porcentual(self) -> float:
        """Margen porcentual sobre el precio de venta."""
        if self.precio_unitario == 0:
            return 0.0
        return (self.margen_bruto / self.precio_unitario) * 100

    def hay_stock_suficiente(self, cantidad: int) -> bool:
        """Verifica si hay stock para atender una cantidad pedida."""
        return self.stock >= cantidad

    def reducir_stock(self, cantidad: int) -> None:
        """Descuenta unidades del stock tras una venta."""
        if cantidad <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva.")
        if not self.hay_stock_suficiente(cantidad):
            raise ValueError(
                f"Stock insuficiente. Disponible: {self.stock}, solicitado: {cantidad}."
            )
        self.stock -= cantidad

    def __str__(self) -> str:
        return (
            f"Producto [{self.id_producto}] {self.nombre} | "
            f"Precio: ${self.precio_unitario:,.2f} | Stock: {self.stock}"
        )

    def __repr__(self) -> str:
        return f"Producto(id='{self.id_producto}', nombre='{self.nombre}')"
