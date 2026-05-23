from src.dao.cliente_dao import ClienteDao
from src.models.cliente import Cliente


class ClienteController:

    def __init__(self):
        self.cliente_dao = ClienteDao()

    def crear_cliente(
        self,
        id_cliente: str,
        nombre: str,
        email: str,
        telefono: str,
        direccion: str
    ):

        if not nombre.strip():
            raise ValueError("El nombre es obligatorio")

        if "@" not in email:
            raise ValueError("Correo inválido")

        cliente_existente = self.cliente_dao.buscar_por_id(id_cliente)

        if cliente_existente:
            raise ValueError("El cliente ya existe")

        cliente = Cliente(
            id_cliente=id_cliente,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion
        )

        return self.cliente_dao.guardar(cliente)

    def obtener_cliente(self, id_cliente: str):

        return self.cliente_dao.buscar_por_id(id_cliente)

    def listar_clientes(self):

        return self.cliente_dao.listar_todos()

    def listar_clientes_activos(self):

        return self.cliente_dao.listar_activos()

    def listar_con_saldo_pendiente(self):

        return self.cliente_dao.listar_con_saldo_pendiente()

    def actualizar_cliente(self, cliente: Cliente):

        return self.cliente_dao.actualizar(cliente)

    def activar_cliente(self, id_cliente: str):

        cliente = self.cliente_dao.buscar_por_id(id_cliente)

        if cliente:
            cliente.activo = True
            return self.cliente_dao.actualizar(cliente)

        return None

    def desactivar_cliente(self, id_cliente: str):

        cliente = self.cliente_dao.buscar_por_id(id_cliente)

        if cliente:
            cliente.activo = False
            return self.cliente_dao.actualizar(cliente)

        return None

    def eliminar_cliente(self, id_cliente: str):

        return self.cliente_dao.eliminar(id_cliente)