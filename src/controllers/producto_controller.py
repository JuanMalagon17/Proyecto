"""
ProductoController — Capa Controlador del patrón MVC para la entidad Producto.

Responsabilidades (SRP):
  - Orquestar el CRUD del catálogo de productos.
  - Aplicar reglas de negocio del dominio de producto
    (stock, precios, activación/desactivación).
  - NO conoce facturas ni clientes; es completamente independiente.

Principios SOLID aplicados:
  - SRP: un solo motivo de cambio (reglas de negocio del producto).
  - DIP: depende de IDao[Producto], nunca de ProductoDao directamente.
  - OCP: nuevas reglas de catálogo se agregan sin tocar el CRUD.
"""
from typing import List, Optional

from src.dao.interface_dao import IDao
from src.models.producto import Producto


class ProductoController:
    """
    Controlador MVC para la entidad Producto.

    Independiente de Clientes y Facturas; gestiona únicamente
    el catálogo de productos/servicios vendibles.
    """

    def __init__(self, producto_dao: IDao[Producto]) -> None:
        self._dao = producto_dao

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
    def crear_producto(
        self,
        id_producto: str,
        nombre: str,
        descripcion: str,
        precio_unitario: float,
        costo_unitario: float,
        stock: int = 0,
    ) -> Producto:
        """
        Crea y persiste un nuevo producto en el catálogo.

        Raises:
            ValueError: Si los datos violan las reglas del modelo
                        o ya existe un producto con ese id.
        """
        producto = Producto(
            id_producto=id_producto,
            nombre=nombre,
            descripcion=descripcion,
            precio_unitario=precio_unitario,
            costo_unitario=costo_unitario,
            stock=stock,
        )
        return self._dao.guardar(producto)

    # ------------------------------------------------------------------ #
    # READ
    # ------------------------------------------------------------------ #
    def obtener_producto(self, id_producto: str) -> Optional[Producto]:
        """Retorna el producto con ese id, o None si no existe."""
        return self._dao.buscar_por_id(id_producto)

    def listar_productos(self) -> List[Producto]:
        """Retorna todos los productos del catálogo."""
        return self._dao.listar_todos()

    def listar_disponibles(self) -> List[Producto]:
        """Retorna productos activos con stock mayor a cero."""
        return [
            p for p in self._dao.listar_todos()
            if p.activo and p.stock > 0
        ]

    def listar_sin_stock(self) -> List[Producto]:
        """Retorna productos activos que se quedaron sin stock."""
        return [
            p for p in self._dao.listar_todos()
            if p.activo and p.stock == 0
        ]

    # ------------------------------------------------------------------ #
    # UPDATE
    # ------------------------------------------------------------------ #
    def actualizar_producto(self, producto: Producto) -> Producto:
        """
        Persiste los cambios sobre un producto existente.

        Raises:
            ValueError: Si el producto no existe en el DAO.
        """
        return self._dao.actualizar(producto)

    def ajustar_stock(self, id_producto: str, cantidad: int) -> Producto:
        """
        Aumenta o disminuye el stock de un producto.

        Args:
            cantidad: Positivo para entrada de mercancía,
                      negativo para salida (p.ej. devolución manual).
        Raises:
            ValueError: Si el ajuste deja el stock negativo.
        """
        producto = self._obtener_o_error(id_producto)
        nuevo_stock = producto.stock + cantidad
        if nuevo_stock < 0:
            raise ValueError(
                f"Ajuste inválido: dejaría el stock de '{id_producto}' "
                f"en {nuevo_stock} unidades."
            )
        producto.stock = nuevo_stock
        return self._dao.actualizar(producto)

    def actualizar_precio(
        self,
        id_producto: str,
        nuevo_precio: float,
        nuevo_costo: Optional[float] = None,
    ) -> Producto:
        """
        Actualiza el precio de venta y opcionalmente el costo.

        Raises:
            ValueError: Si el precio es negativo o el producto no existe.
        """
        if nuevo_precio < 0:
            raise ValueError("El nuevo precio no puede ser negativo.")
        producto = self._obtener_o_error(id_producto)
        producto.precio_unitario = nuevo_precio
        if nuevo_costo is not None:
            if nuevo_costo < 0:
                raise ValueError("El nuevo costo no puede ser negativo.")
            producto.costo_unitario = nuevo_costo
        return self._dao.actualizar(producto)

    def activar_producto(self, id_producto: str) -> Producto:
        """Reactiva un producto que estaba desactivado."""
        producto = self._obtener_o_error(id_producto)
        producto.activo = True
        return self._dao.actualizar(producto)

    def desactivar_producto(self, id_producto: str) -> Producto:
        """Desactiva un producto (lo saca del catálogo sin eliminarlo)."""
        producto = self._obtener_o_error(id_producto)
        producto.activo = False
        return self._dao.actualizar(producto)

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #
    def eliminar_producto(self, id_producto: str) -> bool:
        """
        Elimina físicamente un producto del catálogo.

        Returns:
            True si fue eliminado, False si no existía.
        """
        return self._dao.eliminar(id_producto)

    # ------------------------------------------------------------------ #
    # Métodos de soporte interno
    # ------------------------------------------------------------------ #
    def _obtener_o_error(self, id_producto: str) -> Producto:
        producto = self._dao.buscar_por_id(id_producto)
        if producto is None:
            raise ValueError(f"No existe producto con id '{id_producto}'.")
        return producto
