"""
Interfaz DAO Genérica - Principio de Inversión de Dependencias (DIP)
Define el contrato que todos los DAOs concretos deben cumplir.

Aplica:
  - DIP (Dependency Inversion Principle): módulos de alto nivel (controllers)
    dependen de esta abstracción, no de implementaciones concretas.
  - ISP (Interface Segregation Principle): interfaz mínima y cohesiva.
  - OCP (Open/Closed Principle): agregar un nuevo storage (BD, API)
    solo requiere una nueva implementación, sin tocar el controlador.
"""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

# Tipo genérico para la entidad que maneja el DAO
T = TypeVar("T")


class IDao(ABC, Generic[T]):
    """
    Interfaz genérica Data Access Object.
    
    Define las operaciones CRUD estándar que cualquier DAO debe implementar,
    independientemente del mecanismo de persistencia subyacente (JSON, SQLite,
    REST API, etc.).
    """

    @abstractmethod
    def guardar(self, entidad: T) -> T:
        """
        Persiste una nueva entidad.
        
        Args:
            entidad: La entidad a guardar.
        Returns:
            La entidad guardada (con id asignado si aplica).
        Raises:
            ValueError: Si la entidad ya existe o los datos son inválidos.
        """
        ...

    @abstractmethod
    def buscar_por_id(self, id_entidad: str) -> Optional[T]:
        """
        Busca una entidad por su identificador único.
        
        Args:
            id_entidad: Identificador de la entidad.
        Returns:
            La entidad si existe, None en caso contrario.
        """
        ...

    @abstractmethod
    def listar_todos(self) -> List[T]:
        """
        Retorna todas las entidades persistidas.
        
        Returns:
            Lista (puede estar vacía) con todas las entidades.
        """
        ...

    @abstractmethod
    def actualizar(self, entidad: T) -> T:
        """
        Actualiza una entidad existente.
        
        Args:
            entidad: La entidad con los datos actualizados.
        Returns:
            La entidad actualizada.
        Raises:
            ValueError: Si la entidad no existe.
        """
        ...

    @abstractmethod
    def eliminar(self, id_entidad: str) -> bool:
        """
        Elimina una entidad por su identificador.
        
        Args:
            id_entidad: Identificador de la entidad a eliminar.
        Returns:
            True si fue eliminada, False si no existía.
        """
        ...
