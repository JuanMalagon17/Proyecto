"""
test_patterns.py — Pruebas unitarias de los 7 patrones GoF (Actividad 8)

2 casos de prueba por patrón = 14 pruebas totales.
Usa los cuatro controllers separados (ClienteController, ProductoController,
FacturaController, CarteraController).
"""
import json
import os
import tempfile
import unittest

from src.models.cliente import Cliente
from src.models.factura import Factura, EstadoFactura, LineaFactura
from src.models.producto import Producto
from src.patterns.gof_patterns import (
    FacturaBuilder,
    JsonDaoFactory, 
    InMemoryDaoFactory,
    ConfiguracionApp,
    ValidarLimiteCreditoDecorator, 
    _InMemoryDao, # type: ignore
    ReporteCSV, 
    ReporteJSON,
    GestionCarteraFacade,
    ComandoPagarFactura, 
    HistorialComandos,
)
from src.controllers.cartera_controller import CarteraController
from src.controllers.cliente_controller import ClienteController
from src.controllers.factura_controller import FacturaController
from src.controllers.producto_controller import ProductoController
from src.dao.cliente_dao import ClienteDao
from src.dao.factura_dao import FacturaDao
from src.dao.producto_dao import ProductoDao


# ── Utilidades ────────────────────────────────────────────────────────

def _json_temp() -> str:
    fd, ruta = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"clientes": [], "productos": [], "facturas": []}, f)
    return ruta


def _all_controllers(ruta: str):
    fd = FacturaDao(ruta)
    cd = ClienteDao(ruta)
    pd = ProductoDao(ruta)
    return (
        FacturaController(fd, cd, pd),
        ClienteController(cd, fd),
        ProductoController(pd),
        CarteraController(fd),
    )


# ── 1. BUILDER ───────────────────────────────────────────────────────

class TestBuilder(unittest.TestCase):

    def test_B1_construye_factura_con_lineas(self):
        """B-1: Builder produce Factura con total correcto."""
        # Se agregan todos los parámetros requeridos respetando la firma original
        p = Producto("P-B", "Prod", "Descripcion corta", 100000, 40000, stock=20)
        f = (
            FacturaBuilder()
            .set_identificador("BLD-001")
            .set_cliente("C001", "Cliente")
            .set_vencimiento("2026-09-30")
            .agregar_linea(p, 3)
            .set_notas("Test")
            .build()
        )
        self.assertEqual(f.id_factura, "BLD-001")
        self.assertAlmostEqual(f.total, 300000)

    def test_B2_sin_id_lanza_error(self):
        """B-2: build() sin id_factura lanza ValueError."""
        with self.assertRaises(ValueError):
            FacturaBuilder().set_vencimiento("2026-09-30").build()


# ── 2. FACTORY METHOD ────────────────────────────────────────────────

class TestFactoryMethod(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()

    def tearDown(self):
        if os.path.exists(self._ruta): 
            os.remove(self._ruta)

    def test_FM1_json_factory_crea_tipo_correcto(self):
        """FM-1: JsonDaoFactory produce instancias de ClienteDao."""
        factory = JsonDaoFactory(self._ruta)
        self.assertIsInstance(factory.crear_cliente_dao(), ClienteDao)

    def test_FM2_inmemory_factory_guarda_y_recupera(self):
        """FM-2: InMemoryDaoFactory persiste y recupera en memoria."""
        dao = InMemoryDaoFactory().crear_cliente_dao()
        c = Cliente("C-FM", "Test", "fm@x.co", "300", "Dir")
        dao.guardar(c)
        self.assertEqual(dao.buscar_por_id("C-FM").nombre, "Test") # type: ignore


# ── 3. SINGLETON ─────────────────────────────────────────────────────

class TestSingleton(unittest.TestCase):

    def test_S1_misma_instancia(self):
        """S-1: Dos llamadas retornan el mismo objeto."""
        self.assertIs(ConfiguracionApp(), ConfiguracionApp())

    def test_S2_config_persiste(self):
        """S-2: Valor establecido en una instancia visible en la siguiente."""
        ConfiguracionApp().establecer("_test_", "valor99")
        self.assertEqual(ConfiguracionApp().obtener("_test_"), "valor99")
        ConfiguracionApp().establecer("_test_", None)


# ── 4. DECORATOR ─────────────────────────────────────────────────────

class TestDecorator(unittest.TestCase):

    def _factura(self, total: float) -> Factura:
        f = Factura("DEC-001", "C001", "Test", "2026-05-01", "2026-06-01")
        f.agregar_linea(LineaFactura("P1", "Prod", 1, total, total * 0.4))
        return f

    def test_D1_bloquea_factura_sobre_limite(self):
        """D-1: ValidarLimiteCreditoDecorator rechaza total > límite."""
        dao = ValidarLimiteCreditoDecorator(_InMemoryDao[Factura](), 500000)
        with self.assertRaises(ValueError):
            dao.guardar(self._factura(1000000))

    def test_D2_permite_factura_bajo_limite(self):
        """D-2: Factura dentro del límite se guarda sin error."""
        dao = ValidarLimiteCreditoDecorator(_InMemoryDao[Factura](), 5000000)
        resultado = dao.guardar(self._factura(2000000))
        self.assertEqual(resultado.id_factura, "DEC-001")


# ── 5. STRATEGY ──────────────────────────────────────────────────────

class TestStrategy(unittest.TestCase):

    _DATOS = [{"id": "P001", "nombre": "ERP", "utilidad": 4800000, "margen": 75.0}] # type: ignore

    def test_ST1_csv_incluye_encabezados(self):
        """ST-1: ReporteCSV genera encabezados de columna."""
        resultado = ReporteCSV().generar(self._DATOS, "Test") # type: ignore
        self.assertIn("id", resultado)
        self.assertIn("utilidad", resultado)

    def test_ST2_json_genera_estructura_valida(self):
        """ST-2: ReporteJSON produce JSON parseable con clave 'datos'."""
        resultado = json.loads(ReporteJSON().generar(self._DATOS, "Test")) # type: ignore
        self.assertIn("datos", resultado)
        self.assertEqual(resultado["datos"][0]["id"], "P001")


# ── 6. FACADE ────────────────────────────────────────────────────────

class TestFacade(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._factory = JsonDaoFactory(self._ruta)
        self._facade = GestionCarteraFacade(factory_dao=self._factory)
        
        # Poblar datos base requeridos con firmas posicionales completas
        f_ctrl, c_ctrl, p_ctrl, _ = _all_controllers(self._ruta) # type: ignore
        c_ctrl.crear_cliente("C-FAC", "Cliente Facade", "f@x.co", "300", "Dir")
        p_ctrl.crear_producto("P-FAC", "Prod Facade", "Mobiliario", 200000, 80000, stock=50)

    def tearDown(self):
        if os.path.exists(self._ruta): 
            os.remove(self._ruta)

    def test_FA1_registrar_venta_crea_factura(self):
        """FA-1: registrar_venta() crea factura con total correcto."""
        f = self._facade.registrar_venta("FAC-001", "C-FAC", "P-FAC", 5, "2026-08-01")
        self.assertEqual(f.id_factura, "FAC-001")
        self.assertAlmostEqual(f.total, 1000000)

    def test_FA2_dashboard_contiene_datos(self):
        """FA-2: dashboard_financiero() renderiza la información de rentabilidad."""
        self._facade.registrar_venta("FAC-002", "C-FAC", "P-FAC", 2, "2026-08-01")
        reporte = self._facade.dashboard_financiero("texto")
        self.assertIn("Rentabilidad por Producto", reporte)


# ── 7. COMMAND ───────────────────────────────────────────────────────

class TestCommand(unittest.TestCase):

    def setUp(self):
        self._ruta = _json_temp()
        self._f, self._c, self._p, _ = _all_controllers(self._ruta)
        self._c.crear_cliente("C-CMD", "Cmd", "c@x.co", "300", "Dir")
        self._p.crear_producto("P-CMD", "Prod", "Mesa", 300000, 120000, stock=10)
        self._f.crear_factura("F-CMD", "C-CMD", "2026-09-01")
        self._f.agregar_linea_a_factura("F-CMD", "P-CMD", 2)

    def tearDown(self):
        if os.path.exists(self._ruta): 
            os.remove(self._ruta)

    def test_CMD1_pagar_cambia_estado(self):
        """CMD-1: ComandoPagarFactura lleva la factura a PAGADA."""
        h = HistorialComandos()
        h.ejecutar(ComandoPagarFactura(self._f, "F-CMD"))
        self.assertEqual(self._f.obtener_factura("F-CMD").estado, EstadoFactura.PAGADA) # type: ignore

    def test_CMD2_historial_registra_operaciones(self):
        """CMD-2: HistorialComandos guarda la descripción del comando."""
        h = HistorialComandos()
        h.ejecutar(ComandoPagarFactura(self._f, "F-CMD"))
        self.assertEqual(len(h.ver_historial()), 1)
        self.assertIn("F-CMD", h.ver_historial()[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)