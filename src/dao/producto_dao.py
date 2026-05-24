"""
ProductoDao - Implementación JSON del DAO para la entidad Producto.

Aplica:
  - DIP: implementa IDao[Producto] (depende de la abstracción).
  - SRP: solo gestiona la persistencia de productos.
  - LSP: puede sustituir a IDao[Producto] sin alterar el comportamiento.
"""
import json
import os
from typing import Any, List, Optional, cast

from src.dao.interface_dao import IDao
from src.models.producto import Producto


class ProductoDao(IDao[Producto]):
    """DAO concreto que persiste Productos en un archivo JSON."""

    def __init__(self, ruta_json: str) -> None:
        """
        Args:
            ruta_json: Ruta al archivo JSON de persistencia.
        """
        self._ruta: str = ruta_json
        self._clave: str = "productos"
        self._asegurar_archivo()

    # ------------------------------------------------------------------ #
    # Infraestructura interna
    # ------------------------------------------------------------------ #
    def _asegurar_archivo(self) -> None:
        """Crea el archivo JSON con estructura base si no existe."""
        if not os.path.exists(self._ruta):
            ruta_dir = os.path.dirname(self._ruta)
            if ruta_dir:
                os.makedirs(ruta_dir, exist_ok=True)
            self._escribir({self._clave: []})
        else:
            datos = self._leer()
            if self._clave not in datos:
                datos[self._clave] = []
                self._escribir(datos)

    def _leer(self) -> dict[str, Any]:
        """Lee y retorna el contenido completo del JSON."""
        with open(self._ruta, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
            if isinstance(datos_raw, dict):
                return cast(dict[str, Any], datos_raw)
            return {self._clave: []}

    def _escribir(self, datos: dict[str, Any]) -> None:
        """Escribe el diccionario completo en el JSON."""
        with open(self._ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _obtener_lista(self) -> List[dict[str, Any]]:
        lista_raw = self._leer().get(self._clave, [])
        if isinstance(lista_raw, list):
            return cast(List[dict[str, Any]], lista_raw)
        return []

    def _guardar_lista(self, lista: List[dict[str, Any]]) -> None:
        datos = self._leer()
        datos[self._clave] = lista
        self._escribir(datos)

    # ------------------------------------------------------------------ #
    # Implementación del contrato IDao
    # ------------------------------------------------------------------ #
    def guardar(self, entidad: Producto) -> Producto:
        """Persiste un nuevo producto. Lanza ValueError si ya existe."""
        lista = self._obtener_lista()
        if any(str(p.get("id_producto")) == entidad.id_producto for p in lista):
            raise ValueError(
                f"Ya existe un producto con id '{entidad.id_producto}'."
            )
        lista.append(entidad.to_dict())
        self._guardar_lista(lista)
        return entidad

    def buscar_por_id(self, id_entidad: str) -> Optional[Producto]:
        """Busca un producto por su id. Retorna None si no existe."""
        for datos in self._obtener_lista():
            if str(datos.get("id_producto")) == id_entidad:
                return Producto.from_dict(datos)
        return None

    def listar_todos(self) -> List[Producto]:
        """Retorna todos los productos persistidos."""
        return [Producto.from_dict(d) for d in self._obtener_lista()]

    def actualizar(self, entidad: Producto) -> Producto:
        """Actualiza un producto existente. Lanza ValueError si no existe."""
        lista = self._obtener_lista()
        for i, datos in enumerate(lista):
            if str(datos.get("id_producto")) == entidad.id_producto:
                lista[i] = entidad.to_dict()
                self._guardar_lista(lista)
                return entidad
        raise ValueError(
            f"No se encontró producto con id '{entidad.id_producto}'."
        )

    def eliminar(self, id_entidad: str) -> bool:
        """Elimina un producto. Retorna True si fue eliminado."""
        lista = self._obtener_lista()
        nueva = [p for p in lista if str(p.get("id_producto")) != id_entidad]
        if len(nueva) == len(lista):
            return False
        self._guardar_lista(nueva)
        return True

    # ------------------------------------------------------------------ #
    # Consultas adicionales de dominio
    # ------------------------------------------------------------------ #
    def listar_con_stock_disponible(self) -> List[Producto]:
        """Retorna productos con stock > 0 y activos."""
        return [
            Producto.from_dict(d)
            for d in self._obtener_lista()
            if int(d.get("stock", 0)) > 0 and bool(d.get("activo", True))
        ]

    def buscar_por_nombre(self, nombre: str) -> List[Producto]:
        """Busca productos cuyo nombre contenga el texto dado (case-insensitive)."""
        nombre_lower = nombre.lower()
        return [
            Producto.from_dict(d)
            for d in self._obtener_lista()
            if nombre_lower in str(d.get("nombre", "")).lower()
        ]