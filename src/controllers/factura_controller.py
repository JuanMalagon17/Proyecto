"""
FacturaController — Capa Controlador del patrón MVC para la entidad Factura.

Responsabilidades (SRP):
  - Orquestar el ciclo de vida de una Factura (crear, agregar líneas,
    pagar, anular, eliminar).
  - Coordinar los efectos secundarios de cada operación sobre
    Cliente (saldo) y Producto (stock).
  - NO calcula métricas de cartera (eso es CarteraController).

Principios SOLID aplicados:
  - SRP: un solo motivo de cambio (ciclo de vida de la factura).
  - DIP: depende de IDao[T], nunca de implementaciones concretas.
  - OCP: nuevos tipos de operación se agregan sin modificar el CRUD base.
"""