"""
FacturaDao - Implementación JSON del DAO para la entidad Factura.
"""
import json
import os
from typing import Any, List, Optional, cast

from src.dao.interface_dao import IDao
from src.models.factura import Factura, EstadoFactura


class FacturaDao(IDao[Factura]):
    """DAO concreto que persiste Facturas en un archivo JSON."""

    def __init__(self, ruta_json: str) -> None:
        self._ruta: str = ruta_json
        self._clave: str = "facturas"
        self._asegurar_archivo()

    def _asegurar_archivo(self) -> None:
        if not os.path.exists(self._ruta):
            # Creamos el directorio si no existe asegurando que os.path.dirname devuelva str
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
        with open(self._ruta, "r", encoding="utf-8") as f:
            # Forzamos a que el JSON leído se entienda como un diccionario de Python válido
            datos_raw = json.load(f)
            if isinstance(datos_raw, dict):
                return cast(dict[str, Any], datos_raw)
            return {self._clave: []}

    def _escribir(self, datos: dict[str, Any]) -> None:
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
    # Implementación IDao
    # ------------------------------------------------------------------ #
    def guardar(self, entidad: Factura) -> Factura:
        lista = self._obtener_lista()
        if any(str(f.get("id_factura")) == entidad.id_factura for f in lista):
            raise ValueError(
                f"Ya existe una factura con id '{entidad.id_factura}'."
            )
        lista.append(entidad.to_dict())
        self._guardar_lista(lista)
        return entidad

    def buscar_por_id(self, id_entidad: str) -> Optional[Factura]:
        for datos in self._obtener_lista():
            if str(datos.get("id_factura")) == id_entidad:
                return Factura.from_dict(datos)
        return None

    def listar_todos(self) -> List[Factura]:
        return [Factura.from_dict(d) for d in self._obtener_lista()]

    def actualizar(self, entidad: Factura) -> Factura:
        lista = self._obtener_lista()
        for i, datos in enumerate(lista):
            if str(datos.get("id_factura")) == entidad.id_factura:
                lista[i] = entidad.to_dict()
                self._guardar_lista(lista)
                return entidad
        raise ValueError(
            f"No se encontró factura con id '{entidad.id_factura}'."
        )

    def eliminar(self, id_entidad: str) -> bool:
        lista = self._obtener_lista()
        nueva = [f for f in lista if str(f.get("id_factura")) != id_entidad]
        if len(nueva) == len(lista):
            return False
        self._guardar_lista(nueva)
        return True

    # ------------------------------------------------------------------ #
    # Consultas de dominio financiero
    # ------------------------------------------------------------------ #
    def listar_por_cliente(self, id_cliente: str) -> List[Factura]:
        """Retorna todas las facturas de un cliente específico."""
        return [
            Factura.from_dict(d)
            for d in self._obtener_lista()
            if str(d.get("id_cliente")) == id_cliente
        ]

    def listar_por_estado(self, estado: EstadoFactura) -> List[Factura]:
        """Retorna facturas filtradas por estado."""
        return [
            Factura.from_dict(d)
            for d in self._obtener_lista()
            if str(d.get("estado")) == estado.value
        ]

    def listar_pendientes(self) -> List[Factura]:
        """Retorna solo las facturas pendientes de pago."""
        return self.listar_por_estado(EstadoFactura.PENDIENTE)