"""
ClienteDao - Implementación JSON del DAO para la entidad Cliente.

Aplica:
  - DIP: implementa IDao[Cliente] (depende de la abstracción).
  - SRP: solo gestiona la persistencia de clientes.
  - LSP: puede sustituir a IDao[Cliente] sin alterar el comportamiento.
"""
import json
import os
from typing import Any, List, Optional, cast

from src.dao.interface_dao import IDao
from src.models.cliente import Cliente


class ClienteDao(IDao[Cliente]):
    """
    DAO concreto que persiste Clientes en un archivo JSON.
    
    El archivo JSON tiene la estructura:
    {
        "clientes": [ {...}, {...} ],
        ...
    }
    """

    def __init__(self, ruta_json: str) -> None:
        """
        Args:
            ruta_json: Ruta al archivo JSON de persistencia.
        """
        self._ruta: str = ruta_json
        self._clave: str = "clientes"
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
    def guardar(self, entidad: Cliente) -> Cliente:
        """Persiste un nuevo cliente. Lanza ValueError si ya existe."""
        lista = self._obtener_lista()
        if any(str(c.get("id_cliente")) == entidad.id_cliente for c in lista):
            raise ValueError(
                f"Ya existe un cliente con id '{entidad.id_cliente}'."
            )
        lista.append(entidad.to_dict())
        self._guardar_lista(lista)
        return entidad

    def buscar_por_id(self, id_entidad: str) -> Optional[Cliente]:
        """Busca un cliente por su id. Retorna None si no existe."""
        for datos in self._obtener_lista():
            if str(datos.get("id_cliente")) == id_entidad:
                return Cliente.from_dict(datos)
        return None

    def listar_todos(self) -> List[Cliente]:
        """Retorna todos los clientes persistidos."""
        return [Cliente.from_dict(d) for d in self._obtener_lista()]

    def actualizar(self, entidad: Cliente) -> Cliente:
        """Actualiza un cliente existente. Lanza ValueError si no existe."""
        lista = self._obtener_lista()
        for i, datos in enumerate(lista):
            if str(datos.get("id_cliente")) == entidad.id_cliente:
                lista[i] = entidad.to_dict()
                self._guardar_lista(lista)
                return entidad
        raise ValueError(
            f"No se encontró cliente con id '{entidad.id_cliente}' para actualizar."
        )

    def eliminar(self, id_entidad: str) -> bool:
        """Elimina un cliente. Retorna True si fue eliminado."""
        lista = self._obtener_lista()
        nueva_lista = [c for c in lista if str(c.get("id_cliente")) != id_entidad]
        if len(nueva_lista) == len(lista):
            return False
        self._guardar_lista(nueva_lista)
        return True

    # ------------------------------------------------------------------ #
    # Consultas adicionales de dominio
    # ------------------------------------------------------------------ #
    def buscar_por_nombre(self, nombre: str) -> List[Cliente]:
        """Busca clientes cuyo nombre contenga el texto dado (case-insensitive)."""
        nombre_lower = nombre.lower()
        return [
            Cliente.from_dict(d)
            for d in self._obtener_lista()
            if nombre_lower in str(d.get("nombre", "")).lower()
        ]

    def listar_activos(self) -> List[Cliente]:
        """Retorna solo los clientes activos."""
        return [
            Cliente.from_dict(d)
            for d in self._obtener_lista()
            if bool(d.get("activo", True))
        ]

    def listar_con_saldo_pendiente(self) -> List[Cliente]:
        """Retorna clientes con saldo pendiente mayor a cero."""
        return [
            Cliente.from_dict(d)
            for d in self._obtener_lista()
            if float(d.get("saldo_pendiente", 0.0)) > 0
        ]