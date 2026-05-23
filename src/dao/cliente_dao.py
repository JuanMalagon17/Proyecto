"""
ClienteDao - Implementación JSON del DAO para la entidad Cliente.

Aplica:
  - DIP: implementa IDao[Cliente] (depende de la abstracción).
  - SRP: solo gestiona la persistencia de clientes.
  - LSP: puede sustituir a IDao[Cliente] sin alterar el comportamiento.
"""
import json
import os
from typing import List, Optional

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
        self._ruta = ruta_json
        self._clave = "clientes"
        self._asegurar_archivo()

    # ------------------------------------------------------------------ #
    # Infraestructura interna
    # ------------------------------------------------------------------ #
    def _asegurar_archivo(self) -> None:
        """Crea el archivo JSON con estructura base si no existe."""
        if not os.path.exists(self._ruta):
            os.makedirs(os.path.dirname(self._ruta), exist_ok=True)
            self._escribir({self._clave: []})
        else:
            datos = self._leer()
            if self._clave not in datos:
                datos[self._clave] = []
                self._escribir(datos)

    def _leer(self) -> dict:
        """Lee y retorna el contenido completo del JSON."""
        with open(self._ruta, "r", encoding="utf-8") as f:
            return json.load(f)

    def _escribir(self, datos: dict) -> None:
        """Escribe el diccionario completo en el JSON."""
        with open(self._ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _obtener_lista(self) -> List[dict]:
        return self._leer().get(self._clave, [])

    def _guardar_lista(self, lista: List[dict]) -> None:
        datos = self._leer()
        datos[self._clave] = lista
        self._escribir(datos)

    # ------------------------------------------------------------------ #
    # Implementación del contrato IDao
    # ------------------------------------------------------------------ #
    def guardar(self, cliente: Cliente) -> Cliente:
        """Persiste un nuevo cliente. Lanza ValueError si ya existe."""
        lista = self._obtener_lista()
        if any(c["id_cliente"] == cliente.id_cliente for c in lista):
            raise ValueError(
                f"Ya existe un cliente con id '{cliente.id_cliente}'."
            )
        lista.append(cliente.to_dict())
        self._guardar_lista(lista)
        return cliente

    def buscar_por_id(self, id_cliente: str) -> Optional[Cliente]:
        """Busca un cliente por su id. Retorna None si no existe."""
        for datos in self._obtener_lista():
            if datos["id_cliente"] == id_cliente:
                return Cliente.from_dict(datos)
        return None

    def listar_todos(self) -> List[Cliente]:
        """Retorna todos los clientes persistidos."""
        return [Cliente.from_dict(d) for d in self._obtener_lista()]

    def actualizar(self, cliente: Cliente) -> Cliente:
        """Actualiza un cliente existente. Lanza ValueError si no existe."""
        lista = self._obtener_lista()
        for i, datos in enumerate(lista):
            if datos["id_cliente"] == cliente.id_cliente:
                lista[i] = cliente.to_dict()
                self._guardar_lista(lista)
                return cliente
        raise ValueError(
            f"No se encontró cliente con id '{cliente.id_cliente}' para actualizar."
        )

    def eliminar(self, id_cliente: str) -> bool:
        """Elimina un cliente. Retorna True si fue eliminado."""
        lista = self._obtener_lista()
        nueva_lista = [c for c in lista if c["id_cliente"] != id_cliente]
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
            if nombre_lower in d["nombre"].lower()
        ]

    def listar_activos(self) -> List[Cliente]:
        """Retorna solo los clientes activos."""
        return [
            Cliente.from_dict(d)
            for d in self._obtener_lista()
            if d.get("activo", True)
        ]

    def listar_con_saldo_pendiente(self) -> List[Cliente]:
        """Retorna clientes con saldo pendiente mayor a cero."""
        return [
            Cliente.from_dict(d)
            for d in self._obtener_lista()
            if d.get("saldo_pendiente", 0.0) > 0
        ]
