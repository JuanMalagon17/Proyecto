"""
test_factura.py — Pruebas unitarias exclusivas de la entidad Factura.

Actividad 7 — CRUD con mínimo 10 casos de prueba.
Entidad: Factura (modelo + FacturaDao + FacturaController)

Capas cubiertas:
  TestModeloFactura    → validaciones del objeto Factura y LineaFactura
  TestDaoFactura       → CRUD directo sobre FacturaDao (JSON temporal)
  TestControllerFactura→ ciclo de vida: crear, agregar líneas, pagar, anular
  TestMetricasCartera  → métricas financieras vía CarteraController
"""
import json
import os
import tempfile
import unittest

# from src.controllers.cartera_controller import CarteraController
from src.controllers.cliente_controller import ClienteController
from src.controllers.factura_controller import FacturaController
from src.controllers.producto_controller import ProductoController
from src.dao.cliente_dao import ClienteDao
from src.dao.factura_dao import FacturaDao
from src.dao.producto_dao import ProductoDao
from src.models.factura import EstadoFactura, Factura, LineaFactura


# ── Utilidades ────────────────────────────────────────────────────────

def _json_temp() -> str:
    fd, ruta = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"clientes": [], "productos": [], "facturas": []}, f)
    return ruta


def _controllers(ruta: str):
    """Devuelve los cuatro controllers apuntando al mismo JSON temporal."""
    fd = FacturaDao(ruta)
    cd = ClienteDao(ruta)
    pd = ProductoDao(ruta)
    return (
        FacturaController(fd, cd, pd),
        ClienteController(cd, fd),
        ProductoController(pd),
        CarteraController(fd),
    )


def _factura_simple(id_f="F001") -> Factura:
    return Factura(
        id_factura=id_f,
        id_cliente="C001",
        nombre_cliente="Cliente Test",
        fecha_emision="2026-05-01",
        fecha_vencimiento="2026-07-01",
    )


# ── TC-F01–F08: Modelo ────────────────────────────────────────────────

class TestModeloFactura(unittest.TestCase):

    def test_TCF01_id_vacio_lanza_error(self):
        """TC-F01: id_factura vacío debe lanzar ValueError."""
        with self.assertRaises(ValueError):
            Factura("", "C001", "Cliente", "2026-05-01", "2026-07-01")

    def test_TCF02_total_es_suma_de_subtotales(self):
        """TC-F02: total = Σ (cantidad × precio) por línea."""
        f = _factura_simple()
        f.agregar_linea(LineaFactura("P1", "A", 2, 100_000, 40_000))
        f.agregar_linea(LineaFactura("P2", "B", 3,  50_000, 20_000))
        self.assertAlmostEqual(f.total, 350_000)

    def test_TCF03_utilidad_bruta_correcta(self):
        """TC-F03: utilidad_bruta = total − costo_total."""
        f = _factura_simple()
        f.agregar_linea(LineaFactura("P1", "A", 2, 100_000, 40_000))
        self.assertAlmostEqual(f.utilidad_bruta, 120_000)

    def test_TCF04_marcar_pagada_cambia_estado(self):
        """TC-F04: marcar_pagada() → estado PAGADA."""
        f = _factura_simple()
        f.marcar_pagada()
        self.assertEqual(f.estado, EstadoFactura.PAGADA)

    def test_TCF05_pagar_dos_veces_lanza_error(self):
        """TC-F05: Pagar una factura ya pagada lanza ValueError."""
        f = _factura_simple()
        f.marcar_pagada()
        with self.assertRaises(ValueError):
            f.marcar_pagada()

    def test_TCF06_anular_cambia_estado(self):
        """TC-F06: anular() → estado ANULADA."""
        f = _factura_simple()
        f.anular()
        self.assertEqual(f.estado, EstadoFactura.ANULADA)

    def test_TCF07_no_agregar_linea_a_factura_pagada(self):
        """TC-F07: Agregar línea a factura pagada lanza ValueError."""
        f = _factura_simple()
        f.marcar_pagada()
        with self.assertRaises(ValueError):
            f.agregar_linea(LineaFactura("P1", "X", 1, 50_000, 20_000))

    def test_TCF08_serializar_y_deserializar(self):
        """TC-F08: to_dict() → from_dict() reconstruye todos los datos."""
        f = _factura_simple("F-SER")
        f.agregar_linea(LineaFactura("P1", "Prod", 1, 80_000, 30_000))
        f2 = Factura.from_dict(f.to_dict())
        self.assertEqual(f2.id_factura, "F-SER")
        self.assertEqual(len(f2.lineas), 1)
        self.assertAlmostEqual(f2.total, 80_000)


# ── TC-F09–F12: DAO directo ───────────────────────────────────────────

class TestDaoFactura(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._dao  = FacturaDao(self._ruta)

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCF09_guardar_y_buscar_por_id(self):
        """TC-F09: guardar() persiste y buscar_por_id() recupera."""
        self._dao.guardar(_factura_simple("F009"))
        self.assertIsNotNone(self._dao.buscar_por_id("F009"))

    def test_TCF10_id_duplicado_lanza_error(self):
        """TC-F10: Guardar dos facturas con mismo ID lanza ValueError."""
        self._dao.guardar(_factura_simple("F010"))
        with self.assertRaises(ValueError):
            self._dao.guardar(_factura_simple("F010"))

    def test_TCF11_actualizar_persiste_cambio_de_estado(self):
        """TC-F11: actualizar() sobreescribe el estado en el JSON."""
        f = _factura_simple("F011")
        self._dao.guardar(f)
        f.marcar_pagada()
        self._dao.actualizar(f)
        self.assertEqual(self._dao.buscar_por_id("F011").estado, EstadoFactura.PAGADA)

    def test_TCF12_eliminar_existente_retorna_true(self):
        """TC-F12: eliminar() borra la factura y retorna True."""
        self._dao.guardar(_factura_simple("F012"))
        self.assertTrue(self._dao.eliminar("F012"))
        self.assertIsNone(self._dao.buscar_por_id("F012"))


# ── TC-F13–F19: Controller (ciclo de vida) ───────────────────────────

class TestControllerFactura(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._f, self._c, self._p, self._k = _controllers(self._ruta)
        self._c.crear_cliente("C001", "Empresa Test", "e@t.co", "300", "Dir")
        self._p.crear_producto("P001", "Servicio", "Desc", 200_000, 80_000, stock=50)

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCF13_crear_factura_persiste_en_json(self):
        """TC-F13: crear_factura() guarda y se puede recuperar."""
        self._f.crear_factura("F013", "C001", "2026-08-01")
        f = self._f.obtener_factura("F013")
        self.assertIsNotNone(f)
        self.assertEqual(f.estado, EstadoFactura.PENDIENTE)

    def test_TCF14_crear_factura_cliente_inexistente_lanza_error(self):
        """TC-F14: Cliente inexistente lanza ValueError."""
        with self.assertRaises(ValueError):
            self._f.crear_factura("F014", "C_NO_EXISTE", "2026-08-01")

    def test_TCF15_agregar_linea_descuenta_stock_y_actualiza_saldo(self):
        """TC-F15: Línea agregada = stock baja y saldo del cliente sube."""
        self._f.crear_factura("F015", "C001", "2026-08-01")
        self._f.agregar_linea_a_factura("F015", "P001", 4)
        self.assertAlmostEqual(self._f.obtener_factura("F015").total, 800_000)
        self.assertEqual(self._p.obtener_producto("P001").stock, 46)
        self.assertAlmostEqual(self._c.obtener_cliente("C001").saldo_pendiente, 800_000)

    def test_TCF16_listar_facturas_retorna_todas(self):
        """TC-F16: listar_facturas() devuelve exactamente las creadas."""
        self._f.crear_factura("F016A", "C001", "2026-08-01")
        self._f.crear_factura("F016B", "C001", "2026-09-01")
        self.assertEqual(len(self._f.listar_facturas()), 2)

    def test_TCF17_pagar_factura_cambia_estado_y_reduce_saldo(self):
        """TC-F17: pagar_factura() → PAGADA y saldo cliente = 0."""
        self._f.crear_factura("F017", "C001", "2026-08-01")
        self._f.agregar_linea_a_factura("F017", "P001", 1)
        self._f.pagar_factura("F017")
        self.assertEqual(self._f.obtener_factura("F017").estado, EstadoFactura.PAGADA)
        self.assertAlmostEqual(self._c.obtener_cliente("C001").saldo_pendiente, 0.0)

    def test_TCF18_anular_factura_revierte_saldo(self):
        """TC-F18: anular_factura() pendiente → saldo cliente vuelve a 0."""
        self._f.crear_factura("F018", "C001", "2026-08-01")
        self._f.agregar_linea_a_factura("F018", "P001", 2)
        self._f.anular_factura("F018")
        self.assertEqual(self._f.obtener_factura("F018").estado, EstadoFactura.ANULADA)
        self.assertAlmostEqual(self._c.obtener_cliente("C001").saldo_pendiente, 0.0)

    def test_TCF19_eliminar_factura_la_borra(self):
        """TC-F19: eliminar_factura() retorna True y ya no existe."""
        self._f.crear_factura("F019", "C001", "2026-08-01")
        self.assertTrue(self._f.eliminar_factura("F019"))
        self.assertIsNone(self._f.obtener_factura("F019"))


# ── TC-F20–F22: Métricas (CarteraController) ─────────────────────────

class TestMetricasCartera(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._f, self._c, self._p, self._k = _controllers(self._ruta)
        self._c.crear_cliente("C001", "Cliente", "t@t.co", "300", "Dir")
        self._p.crear_producto("P001", "Prod", "Desc", 100_000, 60_000, stock=100)
        self._f.crear_factura("F001", "C001", "2026-09-01")
        self._f.agregar_linea_a_factura("F001", "P001", 10)

    def tearDown(self):
        if os.path.exists(self._ruta):
            os.remove(self._ruta)

    def test_TCF20_resumen_cartera_totales_correctos(self):
        """TC-F20: calcular_resumen_cartera() devuelve totales exactos."""
        r = self._k.calcular_resumen_cartera()
        self.assertAlmostEqual(r["total_facturado"], 1_000_000)
        self.assertAlmostEqual(r["utilidad_bruta"],    400_000)
        self.assertAlmostEqual(r["margen_bruto_pct"],      40.0)

    def test_TCF21_tasa_cobranza_sube_al_pagar(self):
        """TC-F21: Pagar la factura sube la tasa de cobranza a 100%."""
        self._f.pagar_factura("F001")
        self.assertAlmostEqual(
            self._k.calcular_resumen_cartera()["tasa_cobranza_pct"], 100.0
        )

    def test_TCF22_rentabilidad_por_producto_correcta(self):
        """TC-F22: rentabilidad_por_producto() agrupa por SKU y calcula margen."""
        datos = self._k.rentabilidad_por_producto()
        self.assertEqual(len(datos), 1)
        self.assertAlmostEqual(datos[0]["utilidad_bruta"], 400_000)
        self.assertAlmostEqual(datos[0]["margen_pct"], 40.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
