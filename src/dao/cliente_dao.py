import json
import os
from src.models.cliente import Cliente


class ClienteDao:

    def __init__(self):
        self.ruta = "data/clientes.json"

        if not os.path.exists(self.ruta):
            with open(self.ruta, "w") as archivo:
                json.dump([], archivo)

    def guardar(self, cliente: Cliente):

        clientes = self.listar_todos()

        clientes.append(cliente)

        self._guardar_json(clientes)

        return cliente

    def buscar_por_id(self, id_cliente: str):

        clientes = self.listar_todos()

        for cliente in clientes:
            if cliente.id_cliente == id_cliente:
                return cliente

        return None

    def listar_todos(self):

        with open(self.ruta, "r") as archivo:
            data = json.load(archivo)

        return [Cliente.from_dict(cliente) for cliente in data]

    def actualizar(self, cliente_actualizado: Cliente):

        clientes = self.listar_todos()

        for i, cliente in enumerate(clientes):

            if cliente.id_cliente == cliente_actualizado.id_cliente:
                clientes[i] = cliente_actualizado
                self._guardar_json(clientes)
                return cliente_actualizado

        return None

    def eliminar(self, id_cliente: str):

        clientes = self.listar_todos()

        clientes_filtrados = [
            cliente for cliente in clientes
            if cliente.id_cliente != id_cliente
        ]

        self._guardar_json(clientes_filtrados)

        return True

    def listar_activos(self):

        clientes = self.listar_todos()

        return [
            cliente for cliente in clientes
            if cliente.activo
        ]

    def listar_con_saldo_pendiente(self):

        clientes = self.listar_todos()

        return [
            cliente for cliente in clientes
            if cliente.saldo_pendiente > 0
        ]

    def _guardar_json(self, clientes):

        with open(self.ruta, "w") as archivo:

            json.dump(
                [cliente.to_dict() for cliente in clientes],
                archivo,
                indent=4
            )