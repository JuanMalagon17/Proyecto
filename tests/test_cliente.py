<<<<<<< HEAD
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
=======
"""
test_cliente.py — Pruebas unitarias exclusivas de la entidad Cliente.

Actividad 7 — CRUD con mínimo 10 casos de prueba.
Entidad: Cliente (modelo + ClienteDao + ClienteController)

Capas cubiertas:
  TestModeloCliente    → validaciones del objeto Cliente
  TestDaoCliente       → CRUD directo sobre ClienteDao (JSON temporal)
  TestControllerCliente→ reglas de negocio via ClienteController
"""
import json
import os
import tempfile
import unittest

from src.controllers.cliente_controller import ClienteController
from src.controllers.factura_controller import FacturaController
from src.controllers.producto_controller import ProductoController
from src.dao.cliente_dao import ClienteDao
from src.dao.factura_dao import FacturaDao
from src.dao.producto_dao import ProductoDao
from src.models.cliente import Cliente


# ── Utilidades ────────────────────────────────────────────────────────

def _json_temp() -> str:
    fd, ruta = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"clientes": [], "productos": [], "facturas": []}, f)
    return ruta


def _cliente_demo(id_c="C001") -> Cliente:
    return Cliente(id_c, "Juan Pérez", "juan@mail.com", "3101234567", "Cra 7 #45-12")


def _controllers(ruta: str):
    fd = FacturaDao(ruta)
    cd = ClienteDao(ruta)
    pd = ProductoDao(ruta)
    return (
        ClienteController(cd, fd),
        FacturaController(fd, cd, pd),
        ProductoController(pd),
    )


# ── TC-C01–C09: Modelo ────────────────────────────────────────────────

class TestModeloCliente(unittest.TestCase):

    def test_TCC01_crear_cliente_valido(self):
        """TC-C01: Cliente con datos correctos se instancia sin errores."""
        c = _cliente_demo()
        self.assertEqual(c.id_cliente, "C001")
        self.assertTrue(c.activo)
        self.assertAlmostEqual(c.saldo_pendiente, 0.0)

    def test_TCC02_id_vacio_lanza_error(self):
        """TC-C02: id_cliente vacío lanza ValueError."""
        with self.assertRaises(ValueError):
            Cliente("", "Ana", "a@x.com", "300", "Dir")

    def test_TCC03_id_solo_espacios_lanza_error(self):
        """TC-C03: id_cliente con solo espacios lanza ValueError."""
        with self.assertRaises(ValueError):
            Cliente("   ", "Ana", "a@x.com", "300", "Dir")

    def test_TCC04_email_sin_arroba_lanza_error(self):
        """TC-C04: Email sin '@' lanza ValueError."""
        with self.assertRaises(ValueError):
            Cliente("C002", "Luis", "correo_invalido", "300", "Dir")

    def test_TCC05_nombre_vacio_lanza_error(self):
        """TC-C05: Nombre vacío lanza ValueError."""
        with self.assertRaises(ValueError):
            Cliente("C003", "", "x@x.com", "300", "Dir")

    def test_TCC06_saldo_negativo_lanza_error(self):
        """TC-C06: saldo_pendiente negativo en constructor lanza ValueError."""
        with self.assertRaises(ValueError):
            Cliente("C004", "María", "m@x.com", "300", "Dir", saldo_pendiente=-1.0)

    def test_TCC07_agregar_saldo_acumula_correctamente(self):
        """TC-C07: agregar_saldo() suma sobre el saldo pendiente."""
        c = _cliente_demo()
        c.agregar_saldo(500_000)
        c.agregar_saldo(300_000)
        self.assertAlmostEqual(c.saldo_pendiente, 800_000)

    def test_TCC08_reducir_saldo_no_baja_de_cero(self):
        """TC-C08: reducir_saldo() nunca produce saldo negativo."""
        c = _cliente_demo()
        c.agregar_saldo(200_000)
        c.reducir_saldo(999_999)
        self.assertAlmostEqual(c.saldo_pendiente, 0.0)

    def test_TCC09_serializar_y_deserializar(self):
        """TC-C09: to_dict() → from_dict() reconstruye fielmente."""
        c = _cliente_demo("C-SER")
        c.agregar_saldo(150_000)
        c2 = Cliente.from_dict(c.to_dict())
        self.assertEqual(c2.id_cliente, "C-SER")
        self.assertAlmostEqual(c2.saldo_pendiente, 150_000)


# ── TC-C10–C18: DAO directo ───────────────────────────────────────────

class TestDaoCliente(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._dao  = ClienteDao(self._ruta)

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCC10_guardar_y_buscar_por_id(self):
        """TC-C10: guardar() persiste y buscar_por_id() recupera."""
        self._dao.guardar(_cliente_demo("C010"))
        c = self._dao.buscar_por_id("C010")
        self.assertIsNotNone(c)
        self.assertEqual(c.nombre, "Juan Pérez")

    def test_TCC11_id_duplicado_lanza_error(self):
        """TC-C11: Guardar dos clientes con mismo ID lanza ValueError."""
        self._dao.guardar(_cliente_demo("C011"))
        with self.assertRaises(ValueError):
            self._dao.guardar(_cliente_demo("C011"))

    def test_TCC12_buscar_inexistente_retorna_none(self):
        """TC-C12: ID inexistente retorna None."""
        self.assertIsNone(self._dao.buscar_por_id("NO_EXISTE"))

    def test_TCC13_listar_todos_retorna_completo(self):
        """TC-C13: listar_todos() devuelve exactamente los guardados."""
        self._dao.guardar(_cliente_demo("C013A"))
        self._dao.guardar(_cliente_demo("C013B"))
        self.assertEqual(len(self._dao.listar_todos()), 2)

    def test_TCC14_listar_vacio_retorna_lista_vacia(self):
        """TC-C14: listar_todos() sin datos retorna []."""
        self.assertEqual(self._dao.listar_todos(), [])

    def test_TCC15_actualizar_persiste_cambio(self):
        """TC-C15: actualizar() sobreescribe el email en el JSON."""
        c = _cliente_demo("C015")
        self._dao.guardar(c)
        c.email = "nuevo@test.com"
        self._dao.actualizar(c)
        self.assertEqual(self._dao.buscar_por_id("C015").email, "nuevo@test.com")

    def test_TCC16_actualizar_inexistente_lanza_error(self):
        """TC-C16: Actualizar cliente inexistente lanza ValueError."""
        with self.assertRaises(ValueError):
            self._dao.actualizar(_cliente_demo("NO_EXISTE"))

    def test_TCC17_eliminar_existente_retorna_true(self):
        """TC-C17: eliminar() retorna True y borra el cliente."""
        self._dao.guardar(_cliente_demo("C017"))
        self.assertTrue(self._dao.eliminar("C017"))
        self.assertIsNone(self._dao.buscar_por_id("C017"))

    def test_TCC18_eliminar_inexistente_retorna_false(self):
        """TC-C18: eliminar() sobre ID inexistente retorna False."""
        self.assertFalse(self._dao.eliminar("NO_EXISTE"))


# ── TC-C19–C23: Controller ───────────────────────────────────────────

class TestControllerCliente(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._c, self._f, self._p = _controllers(self._ruta)

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCC19_crear_y_obtener_via_controller(self):
        """TC-C19: crear_cliente() + obtener_cliente() funciona end-to-end."""
        self._c.crear_cliente("C019", "Empresa SA", "e@sa.co", "601", "Bogotá")
        c = self._c.obtener_cliente("C019")
        self.assertIsNotNone(c)
        self.assertEqual(c.nombre, "Empresa SA")

    def test_TCC20_actualizar_via_controller(self):
        """TC-C20: actualizar_cliente() persiste el nuevo teléfono."""
        self._c.crear_cliente("C020", "Pepe", "p@x.co", "300", "Dir")
        c = self._c.obtener_cliente("C020")
        c.telefono = "999999999"
        self._c.actualizar_cliente(c)
        self.assertEqual(self._c.obtener_cliente("C020").telefono, "999999999")

    def test_TCC21_desactivar_y_activar_cliente(self):
        """TC-C21: desactivar/activar cambian el flag activo correctamente."""
        self._c.crear_cliente("C021", "Toggle", "t@x.co", "300", "Dir")
        self._c.desactivar_cliente("C021")
        self.assertFalse(self._c.obtener_cliente("C021").activo)
        self._c.activar_cliente("C021")
        self.assertTrue(self._c.obtener_cliente("C021").activo)

    def test_TCC22_listar_con_saldo_pendiente(self):
        """TC-C22: listar_con_saldo_pendiente() filtra correctamente."""
        self._c.crear_cliente("C022A", "Con Saldo", "a@x.co", "300", "Dir")
        self._c.crear_cliente("C022B", "Sin Saldo", "b@x.co", "300", "Dir")
        c = self._c.obtener_cliente("C022A")
        c.agregar_saldo(100_000)
        self._c.actualizar_cliente(c)
        con_saldo = self._c.listar_con_saldo_pendiente()
        ids = [x.id_cliente for x in con_saldo]
        self.assertIn("C022A", ids)
        self.assertNotIn("C022B", ids)

    def test_TCC23_eliminar_con_factura_pendiente_lanza_error(self):
        """TC-C23: Eliminar cliente con factura PENDIENTE lanza ValueError."""
        self._c.crear_cliente("C023", "Deudor", "d@x.co", "300", "Dir")
        self._p.crear_producto("P023", "Prod", "D", 100_000, 40_000, stock=10)
        self._f.crear_factura("F023", "C023", "2026-09-01")
        self._f.agregar_linea_a_factura("F023", "P023", 1)
        with self.assertRaises(ValueError):
            self._c.eliminar_cliente("C023")


if __name__ == "__main__":
    unittest.main(verbosity=2)
>>>>>>> develop
