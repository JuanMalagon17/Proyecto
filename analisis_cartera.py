"""
analisis_cartera.py — Análisis de datos financieros con pandas.

Prepara el proyecto para la fase de Machine Learning:
  - Carga datos del JSON y los convierte a DataFrames
  - Calcula métricas de cartera sobre los DataFrames
  - Detecta clientes en riesgo (morosidad) con reglas simples
  - Genera un reporte exportable a CSV

Uso:
    python analisis_cartera.py

Requieres: pip install pandas
"""
import json
import os
import sys
from datetime import date
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(__file__))

# Usamos minúsculas para que Pylance no lo trate como constante estática inmutable
pd: Any = None
pandas_disponible: bool = False

try:
    import pandas as pd  # type: ignore
    pandas_disponible = True
except ImportError:
    pandas_disponible = False


def cargar_datos(ruta_json: str) -> Dict[str, List[Any]]:
    """Carga defensiva del JSON especificando tipos estructurados."""
    if not os.path.exists(ruta_json):
        return {"clientes": [], "productos": [], "facturas": []}
    
    try:
        with open(ruta_json, "r", encoding="utf-8") as f:
            datos: Dict[str, List[Any]] = json.load(f)
            return datos
    except (json.JSONDecodeError, OSError):
        print(f"⚠ El archivo {ruta_json} está corrupto o inaccesible. Inicializando vacíos.")
        return {"clientes": [], "productos": [], "facturas": []}


def analizar_cartera(ruta_json: str) -> None:
    """Ejecuta el análisis completo de cartera financiera silenciando alertas de Pylance Strict."""
    def sep(t: str = "") -> None:
        print(f"\n{'='*60}\n  {t}\n{'='*60}" if t else "\n" + "="*60)

    # Si no hay pandas, abortamos de inmediato. Esto le asegura a Pylance que abajo 'pd' NUNCA estará unbound
    if not pandas_disponible:
        print("⚠ pandas no está instalado. Ejecuta: pip install pandas")
        print("   El análisis de datos requiere estas librerías.")
        _analisis_sin_pandas(ruta_json)
        return

    datos = cargar_datos(ruta_json)
    facturas_raw: List[Dict[str, Any]] = datos.get("facturas", [])

    if not facturas_raw:
        sep("AVISO DEL SISTEMA DE CARTERA")
        print("⚠ No hay datos suficientes de facturas para analizar.")
        print("  Asegúrate de que el archivo 'facturas.json' exista y contenga transacciones.")
        print("  Ejecuta primero la simulación o el flujo principal del programa.")
        sep()
        return

    # Aplanar facturas con sus líneas de forma segura
    filas_facturas: List[Dict[str, Any]] = []
    for f in facturas_raw:
        if "id_factura" not in f or "id_cliente" not in f:
            continue
        lineas: List[Dict[str, Any]] = f.get("lineas", [])
        for linea in lineas:
            cantidad: int = linea.get("cantidad", 0)
            precio_unitario: float = linea.get("precio_unitario", 0.0)
            costo_unitario: float = linea.get("costo_unitario", 0.0)
            
            filas_facturas.append({
                "id_factura":       f["id_factura"],
                "id_cliente":       f["id_cliente"],
                "nombre_cliente":   f.get("nombre_cliente", "Cliente Anónimo"),
                "fecha_emision":    f.get("fecha_emision", date.today().isoformat()),
                "fecha_vencimiento":f.get("fecha_vencimiento", date.today().isoformat()),
                "estado":           f.get("estado", "PENDIENTE"),
                "id_producto":      linea.get("id_producto", "P_DESCONOCIDO"),
                "nombre_producto":  linea.get("nombre_producto", "Producto genérico"),
                "cantidad":         cantidad,
                "precio_unitario":  precio_unitario,
                "costo_unitario":   costo_unitario,
                "subtotal":         cantidad * precio_unitario,
                "costo_total":      cantidad * costo_unitario,
            })

    if not filas_facturas:
        print("⚠ Estructuras de facturas detectadas, pero sin líneas de detalle válidas.")
        return

    df = pd.DataFrame(filas_facturas)
    df["utilidad_linea"] = df["subtotal"] - df["costo_total"]
    df["fecha_emision"]    = pd.to_datetime(df["fecha_emision"])
    df["fecha_vencimiento"]= pd.to_datetime(df["fecha_vencimiento"])
    hoy = pd.Timestamp(date.today())

    df_activas = df[df["estado"] != "ANULADA"].copy()

    if df_activas.empty:
        print("⚠ Todas las facturas registradas en el sistema se encuentran en estado ANULADA.")
        return

    # ------------------------------------------------------------------ #
    sep("1. RESUMEN EJECUTIVO DE CARTERA")
    # ------------------------------------------------------------------ #
    total_fac: float = float(df_activas["subtotal"].sum())
    utilidad: float = float(df_activas["utilidad_linea"].sum())
    cobrado: float = float(df_activas[df_activas["estado"]=="PAGADA"]["subtotal"].sum())
    pendiente: float = float(df_activas[df_activas["estado"]=="PENDIENTE"]["subtotal"].sum())
    margen: float = (utilidad / total_fac * 100) if total_fac else 0.0
    roa: float = margen  
    cobranza: float = (cobrado / total_fac * 100) if total_fac else 0.0

    print(f"  Total facturado      : ${total_fac:>18,.2f} COP")
    print(f"  Total cobrado        : ${cobrado:>18,.2f} COP")
    print(f"  Total pendiente      : ${pendiente:>18,.2f} COP")
    print(f"  Utilidad bruta       : ${utilidad:>18,.2f} COP")
    print(f"  Margen bruto         : {margen:>18.2f} %")
    print(f"  ROA de cartera       : {roa:>18.2f} %")
    print(f"  Tasa de cobranza     : {cobranza:>18.2f} %")

    # ------------------------------------------------------------------ #
    sep("2. VENTAS POR CLIENTE (Top 5)")
    # ------------------------------------------------------------------ #
    por_cliente = (
        df_activas.groupby(["id_cliente", "nombre_cliente"])
        .agg(
            total_ventas=("subtotal", "sum"),
            utilidad=("utilidad_linea", "sum"),
            n_facturas=("id_factura", "nunique"),
        )
        .sort_values("total_ventas", ascending=False)
        .head(5)
        .reset_index()
    )
    por_cliente["margen_pct"] = (por_cliente["utilidad"] / por_cliente["total_ventas"] * 100).round(2)
    print(por_cliente[["nombre_cliente","total_ventas","utilidad","margen_pct","n_facturas"]].to_string(index=False))




    # ------------------------------------------------------------------ #
    sep("3. RENTABILIDAD POR PRODUCTO")
    # ------------------------------------------------------------------ #

    por_producto = (
        df_activas.groupby(["id_producto", "nombre_producto"])  # type: ignore
        .agg(
            unidades=("cantidad", "sum"),
            ingresos=("subtotal", "sum"),
            costos=("costo_total", "sum"),
        )
        .assign(utilidad=lambda x: x["ingresos"] - x["costos"]) # type: ignore
        .assign(margen=lambda x: (x["utilidad"] / x["ingresos"] * 100).round(2)) # type: ignore
        .sort_values("utilidad", ascending=False)
        .reset_index()
    )
    print(por_producto[["nombre_producto","unidades","ingresos","utilidad","margen"]].to_string(index=False))

    # ------------------------------------------------------------------ #
    sep("4. ANÁLISIS DE MOROSIDAD (Detección temprana de riesgo)")
    # ------------------------------------------------------------------ #
    df_pendientes = df_activas[df_activas["estado"] == "PENDIENTE"].copy()
    if not df_pendientes.empty:
        df_pendientes["dias_vencimiento"] = (df_pendientes["fecha_vencimiento"] - hoy).dt.days
        df_pendientes["riesgo"] = pd.cut(
            df_pendientes["dias_vencimiento"],
            bins=[-9999, 0, 7, 30, 9999],
            labels=["🔴 VENCIDA", "🟠 CRÍTICO (<7d)", "🟡 ALERTA (<30d)", "🟢 OK"],
        )
        resumen_riesgo = (
            df_pendientes.groupby(["id_cliente","nombre_cliente","riesgo"], observed=True)  # type: ignore
            .agg(monto_pendiente=("subtotal","sum"), facturas=("id_factura","nunique"))
            .sort_values("monto_pendiente", ascending=False)
            .reset_index()
        )
        print(resumen_riesgo.to_string(index=False))

        vencido: float = float(df_pendientes[df_pendientes["dias_vencimiento"] <= 0]["subtotal"].sum())
        idx_morosidad: float = (vencido / pendiente * 100) if pendiente else 0.0
        print(f"\n  Índice de morosidad  : {idx_morosidad:.2f} %")
        print(f"  (Monto vencido: ${vencido:,.2f} / Pendiente total: ${pendiente:,.2f})")
    else:
        print("  ✅ No hay facturas pendientes. Cartera saneada.")

    # ------------------------------------------------------------------ #
    sep("5. EVOLUCIÓN MENSUAL DE VENTAS")
    # ------------------------------------------------------------------ #
    df_activas_copy = df_activas.copy()
    df_activas_copy["mes"] = df_activas_copy["fecha_emision"].dt.to_period("M")
    mensual = (
        df_activas_copy.groupby("mes")  # type: ignore
        .agg(ingresos=("subtotal","sum"), utilidad=("utilidad_linea","sum"))
        .assign(margen=lambda x: (x["utilidad"]/x["ingresos"]*100).round(2)) # type: ignore
        .reset_index()
    )
    print(mensual.to_string(index=False))

    # ------------------------------------------------------------------ #
    sep("6. EXPORTAR DATOS PARA ML")
    # ------------------------------------------------------------------ #
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    df_activas.to_csv(os.path.join(output_dir, "cartera_detalle.csv"), index=False, encoding="utf-8")
    por_cliente.to_csv(os.path.join(output_dir, "clientes_rentabilidad.csv"), index=False, encoding="utf-8")
    por_producto.to_csv(os.path.join(output_dir, "productos_rentabilidad.csv"), index=False, encoding="utf-8")
    print("  ✅ Archivos CSV exportados con éxito en data/:")
    print("     · cartera_detalle.csv        (datos crudos para entrenamiento ML)")
    print("     · clientes_rentabilidad.csv (features de clientes)")
    print("     · productos_rentabilidad.csv(features de productos)")
    sep()


def _analisis_sin_pandas(ruta_json: str) -> None:
    """Análisis básico sin pandas usando tipado explícito."""
    datos = cargar_datos(ruta_json)
    facturas: List[Dict[str, Any]] = datos.get("facturas", [])
    if not facturas:
        print("No hay datos de facturas para calcular consolidados.")
        return

    total: float = sum(
        int(l.get("cantidad", 0)) * float(l.get("precio_unitario", 0.0))
        for f in facturas if f.get("estado") != "ANULADA"
        for l in f.get("lineas", [])
    )
    print(f"\n  Total facturado (sin pandas): ${total:,.2f}")
    print("  Instala pandas para el análisis completo: pip install pandas")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, "data", "facturas.json")
    analizar_cartera(ruta)