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
            id_cliente=data["id_cliente"],
            nombre=data["nombre"],
            email=data["email"],
            telefono=data["telefono"],
            direccion=data["direccion"],
            activo=data.get("activo", True),
            saldo_pendiente=data.get("saldo_pendiente", 0.0)
        )