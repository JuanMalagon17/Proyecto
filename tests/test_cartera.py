"""
test_cartera.py — Pruebas unitarias exclusivas para CarteraController.

Valida la exactitud matemática de las métricas agregadas del negocio:
  - Resumen financiero global (Ingresos, recaudos, pendientes).
  - Márgenes de ganancia y tasas de cobranza.
  - Rankings de clientes (Top volumen de ventas).
  - Rentabilidad desglosada por SKU/Producto.
  - Índices de morosidad basados en fechas de vencimiento.
"""
import unittest
from datetime import date, timedelta
from typing import Any, Dict, List

from src.controllers.cartera_controller import CarteraController
from src.dao.interface_dao import IDao
from src.models.factura import EstadoFactura, Factura, LineaFactura


# ── Implementación Mock/Fake de IDao para Facturas ────────────────────

class FakeFacturaDao(IDao[Factura]):
    """Implementación en memoria (Fake) para evitar E/S de archivos en los tests de métricas."""

    def __init__(self) -> None:
        self.facturas: Dict[str, Factura] = {}

    def guardar(self, entidad: Factura) -> Factura:
        self.facturas[entidad.id_factura] = entidad
        return entidad

    def buscar_por_id(self, id_entidad: str) -> Any:
        return self.facturas.get(id_entidad)

    def listar_todos(self) -> List[Factura]:
        return list(self.facturas.values())

    def actualizar(self, entidad: Factura) -> Factura:
        self.facturas[entidad.id_factura] = entidad
        return entidad

    def eliminar(self, id_entidad: str) -> bool:
        if id_entidad in self.facturas:
            del self.facturas[id_entidad]
            return True
        return False


# ── Suite de Pruebas ──────────────────────────────────────────────────

class TestCarteraController(unittest.TestCase):

    def setUp(self) -> None:
        """Configura el entorno inyectando el DAO en memoria al controlador."""
        self._dao = FakeFacturaDao()
        self._ctrl = CarteraController(self._dao)
        
        # Helper de fechas para pruebas de morosidad
        self._hoy = date.today()
        self._hace_un_mes = (self._hoy - timedelta(days=30)).isoformat()
        self._en_un_mes = (self._hoy + timedelta(days=30)).isoformat()

    def test_TCC01_resumen_cartera_vacia(self) -> None:
        """TC-C01: Calcular métricas en un sistema sin facturas retorna valores en cero."""
        resumen = self._ctrl.calcular_resumen_cartera()
        
        self.assertEqual(resumen["total_facturas"], 0)
        self.assertAlmostEqual(resumen["total_facturado"], 0.0)
        self.assertAlmostEqual(resumen["total_cobrado"], 0.0)
        self.assertAlmostEqual(resumen["total_pendiente"], 0.0)
        self.assertAlmostEqual(resumen["margen_bruto_pct"], 0.0)
        self.assertAlmostEqual(resumen["tasa_cobranza_pct"], 0.0)

    def test_TCC02_calculo_resumen_financiero_exitoso(self) -> None:
        """TC-C02: Valida sumatorias de facturados, cobrados y pendientes con datos mixtos."""
        # Factura 1: PAGADA. Total = 1,500,000, Costo = 900,000 -> Utilidad = 600,000
        f1 = Factura("F001", "C001", "Sebastian Gutierrez", self._hace_un_mes, self._hoy.isoformat())
        f1.estado = EstadoFactura.PAGADA
        f1.lineas.append(LineaFactura("P001", "Mesa Comedor Colmena", 1, 1500000.0, 900000.0))
        self._dao.guardar(f1)

        # Factura 2: PENDIENTE. Total = 2,000,000, Costo = 1,200,000 -> Utilidad = 800,000
        f2 = Factura("F002", "C002", "Carlos Pena", self._hace_un_mes, self._en_un_mes)
        f2.estado = EstadoFactura.PENDIENTE
        f2.lineas.append(LineaFactura("P002", "Cama Doble Rosa", 1, 2000000.0, 1200000.0))
        self._dao.guardar(f2)

        resumen = self._ctrl.calcular_resumen_cartera()
        
        # Verificaciones monetarias
        self.assertEqual(resumen["total_facturas"], 2)
        self.assertAlmostEqual(resumen["total_facturado"], 3500000.0)
        self.assertAlmostEqual(resumen["total_cobrado"], 1500000.0)
        self.assertAlmostEqual(resumen["total_pendiente"], 2000000.0)
        self.assertAlmostEqual(resumen["utilidad_bruta"], 1400000.0)
        
        # Verificaciones porcentuales
        # Margen = (1,400,000 / 3,500,000) * 100 = 40.0%
        self.assertAlmostEqual(resumen["margen_bruto_pct"], 40.0)
        # Tasa de cobranza = (1,500,000 / 3,500,000) * 100 = 42.86%
        self.assertAlmostEqual(resumen["tasa_cobranza_pct"], 42.86)

    def test_TCC03_facturas_anuladas_se_excluyen_de_metricas(self) -> None:
        """TC-C03: Las facturas con estado ANULADA no alteran los acumulados económicos."""
        f1 = Factura("F003", "C001", "Sebastian Gutierrez", self._hace_un_mes, self._hoy.isoformat())
        f1.estado = EstadoFactura.ANULADA
        f1.lineas.append(LineaFactura("P001", "Mesa Comedor", 1, 1000000.0, 500000.0))
        self._dao.guardar(f1)

        resumen = self._ctrl.calcular_resumen_cartera()
        self.assertEqual(resumen["total_facturas"], 0)
        self.assertAlmostEqual(resumen["total_facturado"], 0.0)

    def test_TCC04_ranking_top_clientes(self) -> None:
        """TC-C04: Identifica correctamente a los clientes con mayores volúmenes de compra."""
        # Cliente A: Compra 1,000,000
        fa = Factura("F_A", "C_A", "Cliente Alfa", self._hace_un_mes, self._en_un_mes)
        fa.lineas.append(LineaFactura("P001", "Prod", 1, 1000000.0, 500000.0))
        self._dao.guardar(fa)

        # Cliente B: Compra 3,500,000
        fb = Factura("F_B", "C_B", "Cliente Beta", self._hace_un_mes, self._en_un_mes)
        fb.lineas.append(LineaFactura("P001", "Prod", 1, 3500000.0, 1500000.0))
        self._dao.guardar(fb)

        # Cliente C: Compra 2,000,000
        fc = Factura("F_C", "C_C", "Cliente Gamma", self._hace_un_mes, self._en_un_mes)
        fc.lineas.append(LineaFactura("P001", "Prod", 1, 2000000.0, 1000000.0))
        self._dao.guardar(fc)

        top_3 = self._ctrl.top_clientes_por_ventas(n=3)
        
        self.assertEqual(len(top_3), 3)
        # El primero debe ser Cliente Beta (3,500,000)
        self.assertEqual(top_3[0][0], "Cliente Beta")
        self.assertAlmostEqual(top_3[0][1], 3500000.0)
        # El segundo debe ser Cliente Gamma (2,000,000)
        self.assertEqual(top_3[1][0], "Cliente Gamma")
        # El tercero debe ser Cliente Alfa (1,000,000)
        self.assertEqual(top_3[2][0], "Cliente Alfa")

    def test_TCC05_rentabilidad_por_producto_agregada(self) -> None:
        """TC-C05: Consolida ventas múltiples del mismo SKU y ordena descendentemente por utilidad."""
        # Factura 1 vende 2 Sillas Comedor (SKU: S01)
        f1 = Factura("F1", "C1", "Cliente X", self._hace_un_mes, self._en_un_mes)
        f1.lineas.append(LineaFactura("S01", "Silla Comedor Gris", 2, 300000.0, 150000.0)) # Subtotal=600K, Costo=300K
        self._dao.guardar(f1)

        # Factura 2 vende 1 Silla Comedor (SKU: S01) y 1 Centro de Entretenimiento (SKU: E05)
        f2 = Factura("F2", "C2", "Cliente Y", self._hace_un_mes, self._en_un_mes)
        f2.lineas.append(LineaFactura("S01", "Silla Comedor Gris", 1, 300000.0, 150000.0)) # Subtotal=300K, Costo=150K
        f2.lineas.append(LineaFactura("E05", "Centro TV Flotante", 1, 800000.0, 300000.0)) # Subtotal=800K, Costo=300K -> Utilidad=500K
        self._dao.guardar(f2)

        rentabilidad = self._ctrl.rentabilidad_por_producto()
        
        self.assertEqual(len(rentabilidad), 2)
        
        # El primer ítem en el ranking de utilidad debe ser el Centro TV Flotante (Utilidad = 500,000)
        self.assertEqual(rentabilidad[0]["id_producto"], "E05")
        self.assertAlmostEqual(rentabilidad[0]["utilidad_bruta"], 500000.0)
        
        # El segundo ítem debe ser la Silla Comedor Gris (Unidades consolidadas = 3, Utilidad total = 450,000)
        self.assertEqual(rentabilidad[1]["id_producto"], "S01")
        self.assertEqual(rentabilidad[1]["unidades_vendidas"], 3)
        self.assertAlmostEqual(rentabilidad[1]["utilidad_bruta"], 450000.0)
        self.assertAlmostEqual(rentabilidad[1]["margen_pct"], 50.0)

    def test_TCC06_analisis_morosidad_y_vencimientos(self) -> None:
        """TC-C06: Calcula correctamente el índice analizando facturas cuya fecha de vencimiento ya expiró."""
        # Factura A: Pendiente pero NO vencida (vence en un mes) -> 1,200,000
        fa = Factura("F_A", "C1", "Cliente 1", self._hace_un_mes, self._en_un_mes)
        fa.estado = EstadoFactura.PENDIENTE
        fa.lineas.append(LineaFactura("P1", "Mueble", 1, 1200000.0, 600000.0))
        self._dao.guardar(fa)

        # Factura B: Pendiente y YA VENCIDA (su vencimiento fue ayer) -> 800,000
        ayer = (self._hoy - timedelta(days=1)).isoformat()
        fb = Factura("F_B", "C2", "Cliente 2", self._hace_un_mes, ayer)
        fb.estado = EstadoFactura.PENDIENTE
        fb.lineas.append(LineaFactura("P2", "Estante", 1, 800000.0, 400000.0))
        self._dao.guardar(fb)

        morosidad = self._ctrl.calcular_indice_morosidad()
        
        # Monto Pendiente Total = 1,200,000 + 800,000 = 2,000,000
        # Monto Vencido = 800,000
        # Índice = (800,000 / 2,000,000) * 100 = 40.0%
        self.assertAlmostEqual(morosidad["monto_pendiente_total"], 2000000.0)
        self.assertAlmostEqual(morosidad["monto_vencido"], 800000.0)
        self.assertAlmostEqual(morosidad["indice_morosidad_pct"], 40.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)