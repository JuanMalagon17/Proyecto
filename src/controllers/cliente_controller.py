<<<<<<< HEAD
from src.dao.cliente_dao import ClienteDao
from src.models.cliente import Cliente


class ClienteController:

    def __init__(self):
        self.cliente_dao = ClienteDao()

=======
"""
ClienteController — Capa Controlador del patrón MVC para la entidad Cliente.

Responsabilidades (SRP):
  - Orquestar el CRUD de clientes usando el DAO.
  - Aplicar reglas de negocio propias del cliente
    (ej: no eliminar si tiene facturas pendientes activas).
  - NO conoce nada de Facturas ni Productos directamente;
    recibe el DAO de facturas solo para la regla de negocio de eliminación.

Principios SOLID aplicados:
  - SRP: un solo motivo de cambio (reglas de negocio del cliente).
  - DIP: depende de IDao[Cliente] e IDao[Factura], nunca de concretos.
  - OCP: nuevas reglas de negocio se agregan sin modificar el CRUD.
"""
from typing import List, Optional

from src.dao.interface_dao import IDao
from src.models.cliente import Cliente
from src.models.factura import EstadoFactura, Factura


class ClienteController:
    """
    Controlador MVC para la entidad Cliente.

    Recibe sus dependencias por inyección de constructor (DIP),
    lo que permite sustituir implementaciones en pruebas unitarias
    sin modificar este código.
    """

    def __init__(
        self,
        cliente_dao: IDao[Cliente],
        factura_dao: IDao[Factura],
    ) -> None:
        self._cliente_dao = cliente_dao
        self._factura_dao = factura_dao

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
>>>>>>> develop
    def crear_cliente(
        self,
        id_cliente: str,
        nombre: str,
        email: str,
        telefono: str,
<<<<<<< HEAD
        direccion: str
    ):

        if not nombre.strip():
            raise ValueError("El nombre es obligatorio")

        if "@" not in email:
            raise ValueError("Correo inválido")

        cliente_existente = self.cliente_dao.buscar_por_id(id_cliente)

        if cliente_existente:
            raise ValueError("El cliente ya existe")

=======
        direccion: str,
    ) -> Cliente:
        """
        Crea y persiste un nuevo cliente.

        Raises:
            ValueError: Si los datos son inválidos (delegado al modelo)
                        o si ya existe un cliente con ese id.
        """
>>>>>>> develop
        cliente = Cliente(
            id_cliente=id_cliente,
            nombre=nombre,
            email=email,
            telefono=telefono,
<<<<<<< HEAD
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
=======
            direccion=direccion,
        )
        return self._cliente_dao.guardar(cliente)

    # ------------------------------------------------------------------ #
    # READ
    # ------------------------------------------------------------------ #
    def obtener_cliente(self, id_cliente: str) -> Optional[Cliente]:
        """Retorna el cliente con ese id, o None si no existe."""
        return self._cliente_dao.buscar_por_id(id_cliente)

    def listar_clientes(self) -> List[Cliente]:
        """Retorna todos los clientes registrados."""
        return self._cliente_dao.listar_todos()

    def listar_clientes_activos(self) -> List[Cliente]:
        """Retorna solo los clientes con estado activo = True."""
        return [c for c in self._cliente_dao.listar_todos() if c.activo]

    def listar_con_saldo_pendiente(self) -> List[Cliente]:
        """Retorna clientes con saldo pendiente mayor a cero."""
        return [
            c for c in self._cliente_dao.listar_todos()
            if c.saldo_pendiente > 0
        ]

    # ------------------------------------------------------------------ #
    # UPDATE
    # ------------------------------------------------------------------ #
    def actualizar_cliente(self, cliente: Cliente) -> Cliente:
        """
        Persiste los cambios sobre un cliente existente.

        Raises:
            ValueError: Si el cliente no existe en el DAO.
        """
        return self._cliente_dao.actualizar(cliente)

    def activar_cliente(self, id_cliente: str) -> Cliente:
        """Reactiva un cliente que estaba inactivo."""
        cliente = self._obtener_o_error(id_cliente)
        cliente.activo = True
        return self._cliente_dao.actualizar(cliente)

    def desactivar_cliente(self, id_cliente: str) -> Cliente:
        """Marca un cliente como inactivo (baja lógica)."""
        cliente = self._obtener_o_error(id_cliente)
        cliente.activo = False
        return self._cliente_dao.actualizar(cliente)

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #
    def eliminar_cliente(self, id_cliente: str) -> bool:
        """
        Elimina físicamente un cliente del sistema.

        Regla de negocio: no se puede eliminar si tiene facturas PENDIENTES.
        Si las tiene, lanza ValueError con el detalle.

        Returns:
            True si fue eliminado, False si no existía.
        """
        pendientes = [
            f for f in self._factura_dao.listar_todos()
            if f.id_cliente == id_cliente
            and f.estado == EstadoFactura.PENDIENTE
        ]
        if pendientes:
            raise ValueError(
                f"No se puede eliminar el cliente '{id_cliente}': "
                f"tiene {len(pendientes)} factura(s) pendiente(s) por cobrar."
            )
        return self._cliente_dao.eliminar(id_cliente)

    # ------------------------------------------------------------------ #
    # Métodos de soporte interno
    # ------------------------------------------------------------------ #
    def _obtener_o_error(self, id_cliente: str) -> Cliente:
        cliente = self._cliente_dao.buscar_por_id(id_cliente)
        if cliente is None:
            raise ValueError(f"No existe cliente con id '{id_cliente}'.")
        return cliente
>>>>>>> develop
