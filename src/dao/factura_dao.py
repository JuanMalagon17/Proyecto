"""
FacturaDao - Implementación JSON del DAO para la entidad Factura.
"""
import json
import os
from typing import List, Optional

from src.dao.interface_dao import IDao
from src.models.factura import Factura, EstadoFactura


class FacturaDao(IDao[Factura]):
    """DAO concreto que persiste Facturas en un archivo JSON."""

    def __init__(self, ruta_json: str) -> None:
        self._ruta = ruta_json
        self._clave = "facturas"
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
    def guardar(self, factura: Factura) -> Factura:
        lista = self._obtener_lista()
        if any(f["id_factura"] == factura.id_factura for f in lista):
            raise ValueError(
                f"Ya existe una factura con id '{factura.id_factura}'."
            )
        lista.append(factura.to_dict())
        self._guardar_lista(lista)
        return factura

    def buscar_por_id(self, id_factura: str) -> Optional[Factura]:
        for datos in self._obtener_lista():
            if datos["id_factura"] == id_factura:
                return Factura.from_dict(datos)
        return None

    def listar_todos(self) -> List[Factura]:
        return [Factura.from_dict(d) for d in self._obtener_lista()]

    def actualizar(self, factura: Factura) -> Factura:
        lista = self._obtener_lista()
        for i, datos in enumerate(lista):
            if datos["id_factura"] == factura.id_factura:
                lista[i] = factura.to_dict()
                self._guardar_lista(lista)
                return factura
        raise ValueError(
            f"No se encontró factura con id '{factura.id_factura}'."
        )

    def eliminar(self, id_factura: str) -> bool:
        lista = self._obtener_lista()
        nueva = [f for f in lista if f["id_factura"] != id_factura]
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
            if d["id_cliente"] == id_cliente
        ]

    def listar_por_estado(self, estado: EstadoFactura) -> List[Factura]:
        """Retorna facturas filtradas por estado."""
        return [
            Factura.from_dict(d)
            for d in self._obtener_lista()
            if d.get("estado") == estado.value
        ]

    def listar_pendientes(self) -> List[Factura]:
        """Retorna solo las facturas pendientes de pago."""
        return self.listar_por_estado(EstadoFactura.PENDIENTE)
