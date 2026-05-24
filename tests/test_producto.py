"""
test_producto.py — Pruebas unitarias exclusivas de la entidad Producto.

Actividad 7 — CRUD con mínimo 10 casos de prueba.
Entidad: Producto (modelo + ProductoDao + ProductoController)

Capas cubiertas:
  TestModeloProducto    → validaciones del objeto Producto
  TestDaoProducto       → CRUD directo sobre ProductoDao (JSON temporal)
  TestControllerProducto→ catálogo, stock y precios vía ProductoController
"""
import json
import os
import tempfile
import unittest

from src.controllers.producto_controller import ProductoController
from src.dao.producto_dao import ProductoDao
from src.models.producto import Producto


# ── Utilidades ────────────────────────────────────────────────────────

def _json_temp() -> str:
    fd, ruta = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"clientes": [], "productos": [], "facturas": []}, f)
    return ruta


def _producto_demo(id_p="P001", stock=20) -> Producto:
    return Producto(id_p, "Licencia ERP", "Software empresarial",
                    4_800_000, 1_200_000, stock=stock)


# ── TC-P01–P11: Modelo ───────────────────────────────────────────────

class TestModeloProducto(unittest.TestCase):

    def test_TCP01_crear_producto_valido(self):
        """TC-P01: Producto con datos correctos se instancia sin errores."""
        p = _producto_demo()
        self.assertEqual(p.id_producto, "P001")
        self.assertEqual(p.stock, 20)
        self.assertTrue(p.activo)

    def test_TCP02_id_vacio_lanza_error(self):
        """TC-P02: id_producto vacío lanza ValueError."""
        with self.assertRaises(ValueError):
            Producto("", "Prod", "Desc", 100_000, 50_000)

    def test_TCP03_precio_negativo_lanza_error(self):
        """TC-P03: precio_unitario negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            Producto("P003", "Prod", "Desc", -1, 50_000)

    def test_TCP04_costo_negativo_lanza_error(self):
        """TC-P04: costo_unitario negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            Producto("P004", "Prod", "Desc", 100_000, -1)

    def test_TCP05_stock_negativo_lanza_error(self):
        """TC-P05: stock negativo lanza ValueError."""
        with self.assertRaises(ValueError):
            Producto("P005", "Prod", "Desc", 100_000, 50_000, stock=-1)

    def test_TCP06_margen_bruto_correcto(self):
        """TC-P06: margen_bruto = precio - costo."""
        p = Producto("P006", "Laptop", "15\"", 3_000_000, 2_000_000, stock=5)
        self.assertAlmostEqual(p.margen_bruto, 1_000_000)

    def test_TCP07_margen_porcentual_correcto(self):
        """TC-P07: margen_porcentual = (margen / precio) × 100."""
        p = Producto("P007", "Laptop", "Desc", 4_000_000, 1_000_000, stock=5)
        self.assertAlmostEqual(p.margen_porcentual, 75.0)

    def test_TCP08_reducir_stock_descuenta(self):
        """TC-P08: reducir_stock() resta correctamente."""
        p = _producto_demo(stock=10)
        p.reducir_stock(4)
        self.assertEqual(p.stock, 6)

    def test_TCP09_reducir_stock_insuficiente_lanza_error(self):
        """TC-P09: Reducir más del disponible lanza ValueError."""
        p = _producto_demo(stock=3)
        with self.assertRaises(ValueError):
            p.reducir_stock(5)

    def test_TCP10_hay_stock_suficiente(self):
        """TC-P10: hay_stock_suficiente() retorna True/False correctamente."""
        p = _producto_demo(stock=5)
        self.assertTrue(p.hay_stock_suficiente(5))
        self.assertFalse(p.hay_stock_suficiente(6))

    def test_TCP11_serializar_y_deserializar(self):
        """TC-P11: to_dict() → from_dict() reconstruye fielmente."""
        p = _producto_demo("P-SER", stock=15)
        p2 = Producto.from_dict(p.to_dict())
        self.assertEqual(p2.id_producto, "P-SER")
        self.assertEqual(p2.stock, 15)
        self.assertAlmostEqual(p2.precio_unitario, 4_800_000)


# ── TC-P12–P20: DAO directo ──────────────────────────────────────────

class TestDaoProducto(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._dao  = ProductoDao(self._ruta)

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCP12_guardar_y_buscar_por_id(self):
        """TC-P12: guardar() persiste y buscar_por_id() recupera."""
        self._dao.guardar(_producto_demo("P012"))
        self.assertIsNotNone(self._dao.buscar_por_id("P012"))

    def test_TCP13_id_duplicado_lanza_error(self):
        """TC-P13: Guardar dos productos con mismo ID lanza ValueError."""
        self._dao.guardar(_producto_demo("P013"))
        with self.assertRaises(ValueError):
            self._dao.guardar(_producto_demo("P013"))

    def test_TCP14_buscar_inexistente_retorna_none(self):
        """TC-P14: ID inexistente retorna None."""
        self.assertIsNone(self._dao.buscar_por_id("NO_EXISTE"))

    def test_TCP15_listar_todos_retorna_completo(self):
        """TC-P15: listar_todos() devuelve exactamente los guardados."""
        self._dao.guardar(_producto_demo("P015A"))
        self._dao.guardar(_producto_demo("P015B"))
        self._dao.guardar(_producto_demo("P015C"))
        self.assertEqual(len(self._dao.listar_todos()), 3)

    def test_TCP16_listar_vacio_retorna_lista_vacia(self):
        """TC-P16: listar_todos() sin datos retorna []."""
        self.assertEqual(self._dao.listar_todos(), [])

    def test_TCP17_actualizar_persiste_nuevo_precio(self):
        """TC-P17: actualizar() sobreescribe el precio en el JSON."""
        p = _producto_demo("P017")
        self._dao.guardar(p)
        p.precio_unitario = 5_500_000
        self._dao.actualizar(p)
        self.assertAlmostEqual(self._dao.buscar_por_id("P017").precio_unitario, 5_500_000)

    def test_TCP18_actualizar_inexistente_lanza_error(self):
        """TC-P18: Actualizar producto inexistente lanza ValueError."""
        with self.assertRaises(ValueError):
            self._dao.actualizar(_producto_demo("NO_EXISTE"))

    def test_TCP19_eliminar_existente_retorna_true(self):
        """TC-P19: eliminar() retorna True y borra el producto."""
        self._dao.guardar(_producto_demo("P019"))
        self.assertTrue(self._dao.eliminar("P019"))
        self.assertIsNone(self._dao.buscar_por_id("P019"))

    def test_TCP20_eliminar_inexistente_retorna_false(self):
        """TC-P20: eliminar() sobre ID inexistente retorna False."""
        self.assertFalse(self._dao.eliminar("NO_EXISTE"))


# ── TC-P21–P26: Controller ───────────────────────────────────────────

class TestControllerProducto(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._ctrl = ProductoController(ProductoDao(self._ruta))

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCP21_crear_y_obtener_via_controller(self):
        """TC-P21: crear_producto() + obtener_producto() end-to-end."""
        self._ctrl.crear_producto("P021", "Mouse", "Inalámbrico", 80_000, 35_000, stock=50)
        p = self._ctrl.obtener_producto("P021")
        self.assertIsNotNone(p)
        self.assertEqual(p.stock, 50)

    def test_TCP22_ajustar_stock_entrada(self):
        """TC-P22: ajustar_stock(+n) aumenta el stock correctamente."""
        self._ctrl.crear_producto("P022", "Teclado", "Mecánico", 250_000, 100_000, stock=10)
        p = self._ctrl.ajustar_stock("P022", 15)
        self.assertEqual(p.stock, 25)

    def test_TCP23_ajustar_stock_negativo_lanza_error(self):
        """TC-P23: ajustar_stock() que deja stock negativo lanza ValueError."""
        self._ctrl.crear_producto("P023", "Monitor", "4K", 1_200_000, 500_000, stock=3)
        with self.assertRaises(ValueError):
            self._ctrl.ajustar_stock("P023", -10)

    def test_TCP24_actualizar_precio_via_controller(self):
        """TC-P24: actualizar_precio() persiste el nuevo valor."""
        self._ctrl.crear_producto("P024", "SSD", "1TB", 400_000, 180_000, stock=20)
        p = self._ctrl.actualizar_precio("P024", 450_000, 190_000)
        self.assertAlmostEqual(p.precio_unitario, 450_000)
        self.assertAlmostEqual(p.costo_unitario, 190_000)

    def test_TCP25_desactivar_y_activar_producto(self):
        """TC-P25: desactivar/activar cambian el flag activo."""
        self._ctrl.crear_producto("P025", "RAM", "16GB", 200_000, 80_000, stock=30)
        self._ctrl.desactivar_producto("P025")
        self.assertFalse(self._ctrl.obtener_producto("P025").activo)
        self._ctrl.activar_producto("P025")
        self.assertTrue(self._ctrl.obtener_producto("P025").activo)

    def test_TCP26_listar_disponibles_filtra_sin_stock(self):
        """TC-P26: listar_disponibles() excluye productos con stock = 0."""
        self._ctrl.crear_producto("P026A", "Con stock",  "D", 100_000, 40_000, stock=5)
        self._ctrl.crear_producto("P026B", "Sin stock",  "D", 100_000, 40_000, stock=0)
        ids = [p.id_producto for p in self._ctrl.listar_disponibles()]
        self.assertIn("P026A", ids)
        self.assertNotIn("P026B", ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
