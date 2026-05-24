"""
CarteraController — Controlador de métricas financieras de cartera.

Responsabilidades (SRP):
  - Calcular indicadores financieros agregados: ROA, márgenes,
    tasa de cobranza, top clientes, rentabilidad por producto.
  - NO realiza operaciones CRUD sobre ninguna entidad.
  - Consume solo datos de lectura (listar_todos) de los DAOs.

Por qué está separado de FacturaController:
  Las métricas son un "eje de cambio" distinto: el cálculo del ROA
  puede evolucionar (nuevas fórmulas, filtros por fecha, etc.) sin
  afectear en nada el ciclo de vida de una factura, y viceversa.

Principios SOLID aplicados:
  - SRP: único motivo de cambio = fórmulas / métricas financieras.
  - DIP: depende de IDao[Factura], nunca de FacturaDao directamente.
  - OCP: agregar una nueva métrica = nuevo método, sin tocar los existentes.
"""
from datetime import date
from typing import Any, Dict, List, Tuple

from src.dao.interface_dao import IDao
from src.models.factura import EstadoFactura, Factura


class CarteraController:
    """
    Controlador de análisis financiero de cartera.

    Solo necesita el DAO de facturas porque todas las métricas
    se derivan de las facturas y sus líneas.
    """

    def __init__(self, factura_dao: IDao[Factura]) -> None:
        self._factura_dao: IDao[Factura] = factura_dao

    # ------------------------------------------------------------------ #
    # Resumen ejecutivo
    # ------------------------------------------------------------------ #
    def calcular_resumen_cartera(self) -> Dict[str, Any]:
        """
        Genera el resumen financiero global de la cartera.

        Métricas:
          - total_facturas      : cantidad de facturas activas (no anuladas)
          - total_facturado     : suma de todos los totales activos
          - total_cobrado       : suma de facturas PAGADAS
          - total_pendiente     : suma de facturas PENDIENTES
          - utilidad_bruta      : total_facturado − costo_total
          - margen_bruto_pct    : (utilidad / total_facturado) × 100
          - roa_cartera_pct     : igual al margen bruto (activos = cartera total)
          - tasa_cobranza_pct   : (cobrado / facturado) × 100

        Returns:
            Diccionario con todas las métricas redondeadas a 2 decimales.
        """
        activas = [
            f for f in self._factura_dao.listar_todos()
            if f.estado != EstadoFactura.ANULADA
        ]

        total_facturado = sum(f.total for f in activas)
        total_cobrado   = sum(f.total for f in activas if f.estado == EstadoFactura.PAGADA)
        total_pendiente = sum(f.total for f in activas if f.estado == EstadoFactura.PENDIENTE)
        utilidad_bruta  = sum(f.utilidad_bruta for f in activas)

        def pct(num: float, den: float) -> float:
            return round((num / den * 100) if den > 0 else 0.0, 2)

        return {
            "total_facturas": len(activas),
            "total_facturado": round(total_facturado, 2),
            "total_cobrado": round(total_cobrado, 2),
            "total_pendiente": round(total_pendiente, 2),
            "utilidad_bruta": round(utilidad_bruta, 2),
            "margen_bruto_pct": pct(utilidad_bruta, total_facturado),
            "roa_cartera_pct": pct(utilidad_bruta, total_facturado),
            "tasa_cobranza_pct": pct(total_cobrado, total_facturado),
        }

    # ------------------------------------------------------------------ #
    # Ranking de clientes
    # ------------------------------------------------------------------ #
    def top_clientes_por_ventas(self, n: int = 5) -> List[Tuple[str, float]]:
        """
        Retorna los N clientes con mayor volumen de ventas (facturas activas).

        Returns:
            Lista de tuplas (nombre_cliente, total_facturado) ordenada desc.
        """
        acumulado: Dict[str, float] = {}
        nombres: Dict[str, str] = {}

        for f in self._factura_dao.listar_todos():
            if f.estado != EstadoFactura.ANULADA:
                acumulado[f.id_cliente] = acumulado.get(f.id_cliente, 0.0) + f.total
                nombres[f.id_cliente] = f.nombre_cliente

        ranking = sorted(
            [(nombres[k], v) for k, v in acumulado.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        return ranking[:n]

    # ------------------------------------------------------------------ #
    # Rentabilidad por producto
    # ------------------------------------------------------------------ #
    def rentabilidad_por_producto(self) -> List[Dict[str, Any]]:
        """
        Agrega la utilidad bruta generada por cada SKU en todas las facturas.

        Returns:
            Lista de dicts ordenada por utilidad_bruta desc, con:
              id_producto, nombre, unidades_vendidas,
              total_vendido, utilidad_bruta, margen_pct.
        """
        # Tipamos explícitamente el diccionario intermedio para evitar que Pylance infiera tipos parciales
        acumulado: Dict[str, Dict[str, Any]] = {}

        for f in self._factura_dao.listar_todos():
            if f.estado == EstadoFactura.ANULADA:
                continue
            for linea in f.lineas:
                pid = linea.id_producto
                if pid not in acumulado:
                    acumulado[pid] = {
                        "id_producto": pid,
                        "nombre": linea.nombre_producto,
                        "total_vendido": 0.0,
                        "costo_total": 0.0,
                        "unidades": 0,
                    }
                acumulado[pid]["total_vendido"] = float(acumulado[pid]["total_vendido"]) + linea.subtotal
                acumulado[pid]["costo_total"] = float(acumulado[pid]["costo_total"]) + linea.costo_total
                acumulado[pid]["unidades"] = int(acumulado[pid]["unidades"]) + linea.cantidad

        resultado: List[Dict[str, Any]] = []
        for d in acumulado.values():
            total_vendido = float(d["total_vendido"])
            costo_total = float(d["costo_total"])
            
            utilidad = total_vendido - costo_total
            margen = (utilidad / total_vendido * 100) if total_vendido > 0 else 0.0
            
            resultado.append({
                "id_producto": str(d["id_producto"]),
                "nombre": str(d["nombre"]),
                "unidades_vendidas": int(d["unidades"]),
                "total_vendido": round(total_vendido, 2),
                "utilidad_bruta": round(utilidad, 2),
                "margen_pct": round(margen, 2),
            })

        return sorted(resultado, key=lambda x: float(x["utilidad_bruta"]), reverse=True)

    # ------------------------------------------------------------------ #
    # Análisis de morosidad
    # ------------------------------------------------------------------ #
    def calcular_indice_morosidad(self) -> Dict[str, Any]:
        """
        Calcula el índice de morosidad de la cartera.

        Morosidad = facturas PENDIENTES cuya fecha_vencimiento ya pasó.

        Returns:
            Dict con monto_vencido, monto_pendiente_total e indice_pct.
        """
        hoy = date.today().isoformat()

        pendientes = [
            f for f in self._factura_dao.listar_todos()
            if f.estado == EstadoFactura.PENDIENTE
        ]
        monto_total = sum(f.total for f in pendientes)
        monto_vencido = sum(f.total for f in pendientes if f.fecha_vencimiento < hoy)
        indice = (monto_vencido / monto_total * 100) if monto_total > 0 else 0.0

        return {
            "monto_vencido": round(monto_vencido, 2),
            "monto_pendiente_total": round(monto_total, 2),
            "indice_morosidad_pct": round(indice, 2),
        }