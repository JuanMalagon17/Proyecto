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