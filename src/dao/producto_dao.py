"""
ProductoDao - Implementación JSON del DAO para la entidad Producto.
"""
import json
import os
from typing import List, Optional

from src.dao.interface_dao import IDao
from src.models.producto import Producto


class ProductoDao(IDao[Producto]):
    """DAO concreto que persiste Productos en un archivo JSON."""

    def __init__(self, ruta_json: str) -> None:
        self._ruta = ruta_json
        self._clave = "productos"
        self._asegurar_archivo()

    def _asegurar_archivo(self) -> None:
        if not os.path.exists(self._ruta):
            os.makedirs(os.path.dirname(self._ruta), exist_ok=True)
            self._escribir({self._clave: []})
        else:
            datos = self._leer()
            if self._clave not in datos:
                datos[self._clave] = []
                self._escribir(datos)

    def _leer(self) -> dict:
        with open(self._ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def _escribir(self, datos: dict) -> None:
        with open(self._ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _obtener_lista(self) -> List[dict]:
        return self._leer().get(self._clave, [])

    def _guardar_lista(self, lista: List[dict]) -> None:
        datos = self._leer()
        datos[self._clave] = lista
        self._escribir(datos)

    # ------------------------------------------------------------------ #
    # Implementación IDao
    # ------------------------------------------------------------------ #
    def guardar(self, producto: Producto) -> Producto:
        lista = self._obtener_lista()
        if any(p["id_producto"] == producto.id_producto for p in lista):
            raise ValueError(
                f"Ya existe un producto con id '{producto.id_producto}'."
            )
        lista.append(producto.to_dict())
        self._guardar_lista(lista)
        return producto

    def buscar_por_id(self, id_producto: str) -> Optional[Producto]:
        for datos in self._obtener_lista():
            if datos["id_producto"] == id_producto:
                return Producto.from_dict(datos)
        return None

    def listar_todos(self) -> List[Producto]:
        return [Producto.from_dict(d) for d in self._obtener_lista()]

    def actualizar(self, producto: Producto) -> Producto:
        lista = self._obtener_lista()
        for i, datos in enumerate(lista):
            if datos["id_producto"] == producto.id_producto:
                lista[i] = producto.to_dict()
                self._guardar_lista(lista)
                return producto
        raise ValueError(
            f"No se encontró producto con id '{producto.id_producto}'."
        )

    def eliminar(self, id_producto: str) -> bool:
        lista = self._obtener_lista()
        nueva = [p for p in lista if p["id_producto"] != id_producto]
        if len(nueva) == len(lista):
            return False
        self._guardar_lista(nueva)
        return True

    # ------------------------------------------------------------------ #
    # Consultas adicionales
    # ------------------------------------------------------------------ #
    def listar_con_stock_disponible(self) -> List[Producto]:
        """Retorna productos con stock > 0 y activos."""
        return [
            Producto.from_dict(d)
            for d in self._obtener_lista()
            if d.get("stock", 0) > 0 and d.get("activo", True)
        ]

    def buscar_por_nombre(self, nombre: str) -> List[Producto]:
        nombre_lower = nombre.lower()
        return [
            Producto.from_dict(d)
            for d in self._obtener_lista()
            if nombre_lower in d["nombre"].lower()
        ]
