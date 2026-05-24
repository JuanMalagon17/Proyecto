<<<<<<< HEAD
class Cliente:
    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        email: str,
        telefono: str,
        direccion: str,
        activo: bool = True,
        saldo_pendiente: float = 0.0
    ):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.direccion = direccion
        self.activo = activo
        self.saldo_pendiente = saldo_pendiente

    def agregar_saldo(self, monto: float):
        self.saldo_pendiente += monto

    def reducir_saldo(self, monto: float):
        self.saldo_pendiente -= monto

    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "activo": self.activo,
            "saldo_pendiente": self.saldo_pendiente
        }

    @staticmethod
    def from_dict(data: dict):
        return Cliente(
=======
"""
Modelo: Cliente
Representa la entidad Cliente en el dominio del sistema de gestión de cartera.
Aplica principio SRP (Single Responsibility Principle) - solo modela los datos del cliente.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Cliente:
    """
    Entidad de dominio que representa a un cliente del sistema.

    Atributos:
        id_cliente (str): Identificador único del cliente (NIT o cédula).
        nombre (str): Nombre completo o razón social del cliente.
        email (str): Correo electrónico de contacto.
        telefono (str): Número telefónico.
        direccion (str): Dirección física o fiscal.
        activo (bool): Estado del cliente en cartera (True = activo).
        saldo_pendiente (float): Saldo total de facturas pendientes por pagar.
    """
    id_cliente: str
    nombre: str
    email: str
    telefono: str
    direccion: str
    activo: bool = True
    saldo_pendiente: float = 0.0

    # ------------------------------------------------------------------ #
    # Validaciones de negocio (princpio Tell, Don't Ask)
    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        if not self.id_cliente or not self.id_cliente.strip():
            raise ValueError("El id_cliente no puede estar vacío.")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")
        if "@" not in self.email:
            raise ValueError(f"Email inválido: '{self.email}'.")
        if self.saldo_pendiente < 0:
            raise ValueError("El saldo pendiente no puede ser negativo.")

    # ------------------------------------------------------------------ #
    # Serialización / Deserialización (para persistencia JSON)
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        """Convierte el cliente a diccionario para persistencia JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Cliente":
        """Reconstruye un Cliente desde un diccionario (lectura JSON)."""
        return cls(
>>>>>>> develop
            id_cliente=data["id_cliente"],
            nombre=data["nombre"],
            email=data["email"],
            telefono=data["telefono"],
            direccion=data["direccion"],
            activo=data.get("activo", True),
<<<<<<< HEAD
            saldo_pendiente=data.get("saldo_pendiente", 0.0)
        )
=======
            saldo_pendiente=data.get("saldo_pendiente", 0.0),
        )

    # ------------------------------------------------------------------ #
    # Métodos de negocio
    # ------------------------------------------------------------------ #
    def agregar_saldo(self, monto: float) -> None:
        """Incrementa el saldo pendiente del cliente."""
        if monto < 0:
            raise ValueError("El monto a agregar no puede ser negativo.")
        self.saldo_pendiente += monto

    def reducir_saldo(self, monto: float) -> None:
        """Reduce el saldo pendiente al recibir un pago."""
        if monto < 0:
            raise ValueError("El monto a reducir no puede ser negativo.")
        self.saldo_pendiente = max(0.0, self.saldo_pendiente - monto)

    def __str__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return (
            f"Cliente [{self.id_cliente}] {self.nombre} | "
            f"{estado} | Saldo: ${self.saldo_pendiente:,.2f}"
        )

    def __repr__(self) -> str:
        return f"Cliente(id='{self.id_cliente}', nombre='{self.nombre}')"
>>>>>>> develop
