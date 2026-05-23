from src.controllers.cliente_controller import ClienteController


def test_crear_cliente():

    controller = ClienteController()

    cliente = controller.crear_cliente(
        id_cliente="1",
        nombre="Rossana",
        email="rossana@email.com",
        telefono="123456789",
        direccion="Bogotá"
    )

    assert cliente.nombre == "Rossana"


def test_obtener_cliente():

    controller = ClienteController()

    cliente = controller.obtener_cliente("1")

    assert cliente is not None


def test_listar_clientes():

    controller = ClienteController()

    clientes = controller.listar_clientes()

    assert isinstance(clientes, list)


def test_cliente_activo():

    controller = ClienteController()

    controller.activar_cliente("1")

    cliente = controller.obtener_cliente("1")

    assert cliente.activo is True


def test_desactivar_cliente():

    controller = ClienteController()

    controller.desactivar_cliente("1")

    cliente = controller.obtener_cliente("1")

    assert cliente.activo is False