"""
main.py — Vista (View) del patrón MVC.

Responsabilidades:
  - Cablear DAOs → Controllers (único lugar donde se instancian concretos).
  - Recibir input del usuario y delegar TODO al controller correspondiente.
  - Presentar resultados; nunca contiene lógica de negocio.

Arquitectura de controllers:
  ClienteController  → CRUD de clientes
  ProductoController → CRUD de productos y catálogo
  CarteraController  → métricas financieras de cartera
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from src.controllers.cartera_controller import CarteraController
from src.controllers.cliente_controller import ClienteController
from src.controllers.factura_controller import FacturaController
from src.controllers.producto_controller import ProductoController
from src.dao.cliente_dao import ClienteDao
from src.dao.factura_dao import FacturaDao
from src.dao.producto_dao import ProductoDao
# from src.models.factura import EstadoFactura

# ── Ensamblaje de dependencias (DIP) ──────────────────────────────────
RUTA_JSON = os.path.join(os.path.dirname(__file__), "data", "facturas.json")

_factura_dao  = FacturaDao(RUTA_JSON)
_cliente_dao  = ClienteDao(RUTA_JSON)
_producto_dao = ProductoDao(RUTA_JSON)

_clientes  = ClienteController(_cliente_dao, _factura_dao)
_productos = ProductoController(_producto_dao)
_facturas  = FacturaController(_factura_dao, _cliente_dao, _producto_dao)
_cartera   = CarteraController(_factura_dao)

# ── Utilidades de presentación ────────────────────────────────────────

def _sep(titulo: str = "", ancho: int = 62) -> None:
    print("\n" + "─" * ancho)
    if titulo:
        print(f"  {titulo}")
        print("─" * ancho)

def _input(prompt: str) -> str:
    return input(f"  → {prompt}: ").strip()

def _pausar() -> None:
    input("\n  [Presiona Enter para continuar...]")

def _limpiar() -> None:
    os.system("cls" if os.name == "nt" else "clear")

# ── Submenú Clientes ─────────────────────────────────────────────────

def menu_clientes() -> None:
    while True:
        _sep("GESTIÓN DE CLIENTES")
        print("  1. Crear cliente")
        print("  2. Ver cliente por ID")
        print("  3. Listar todos los clientes")
        print("  4. Actualizar cliente")
        print("  5. Desactivar / Activar cliente")
        print("  6. Eliminar cliente")
        print("  0. Volver")
        op = _input("Opción")

        if op == "1":
            _sep("CREAR CLIENTE")
            try:
                c = _clientes.crear_cliente(
                    _input("ID / NIT"), _input("Nombre"), _input("Email"),
                    _input("Teléfono"), _input("Dirección"),
                )
                print(f"\n  ✅ {c}")
            except ValueError as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "2":
            _sep("BUSCAR CLIENTE")
            c = _clientes.obtener_cliente(_input("ID del cliente"))
            if c:
                print(f"\n  {c}\n  Email: {c.email} | Tel: {c.telefono}")
                print(f"  Dirección: {c.direccion}")
            else:
                print("  ❌ No encontrado.")
            _pausar()

        elif op == "3":
            _sep("LISTADO DE CLIENTES")
            cs = _clientes.listar_clientes()
            print("  (vacío)" if not cs else "")
            for c in cs:
                print(f"  • {c}")
            _pausar()

        elif op == "4":
            _sep("ACTUALIZAR CLIENTE")
            c = _clientes.obtener_cliente(_input("ID del cliente"))
            if not c:
                print("  ❌ No encontrado.")
            else:
                print(f"  Actual: {c}")
                nuevo_nombre    = _input(f"Nombre    [{c.nombre}]")    or c.nombre
                nuevo_email     = _input(f"Email     [{c.email}]")     or c.email
                nuevo_telefono  = _input(f"Teléfono  [{c.telefono}]")  or c.telefono
                nuevo_direccion = _input(f"Dirección [{c.direccion}]") or c.direccion
                
                # Modificamos los campos únicamente si pasa la validación del controlador
                try:
                    c.nombre = nuevo_nombre
                    c.email = nuevo_email
                    c.telefono = nuevo_telefono
                    c.direccion = nuevo_direccion
                    _clientes.actualizar_cliente(c)
                    print(f"\n  ✅ Actualizado con éxito.")
                except ValueError as e:
                    print(f"\n  ❌ Error de validación: {e}")
            _pausar()

        elif op == "5":
            _sep("CAMBIAR ESTADO")
            id_c = _input("ID del cliente")
            accion = _input("¿Activar o Desactivar? [a/d]").lower()
            try:
                c = _clientes.activar_cliente(id_c) if accion == "a" else _clientes.desactivar_cliente(id_c)
                print(f"\n  ✅ {c}")
            except ValueError as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "6":
            _sep("ELIMINAR CLIENTE")
            try:
                ok = _clientes.eliminar_cliente(_input("ID del cliente"))
                print(f"\n  {'✅ Eliminado.' if ok else '❌ No encontrado.'}")
            except ValueError as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "0":
            break

# ── Submenú Productos ─────────────────────────────────────────────────

def menu_productos() -> None:
    while True:
        _sep("GESTIÓN DE PRODUCTOS / SERVICIOS")
        print("  1. Crear producto")
        print("  2. Ver producto por ID")
        print("  3. Listar todos los productos")
        print("  4. Actualizar producto")
        print("  5. Ajustar stock")
        print("  6. Actualizar precio")
        print("  7. Eliminar producto")
        print("  0. Volver")
        op = _input("Opción")

        if op == "1":
            _sep("CREAR PRODUCTO")
            try:
                id_sku = _input("ID / SKU")
                nombre = _input("Nombre")
                desc = _input("Descripción")
                precio = float(_input("Precio unitario (COP)") or "0")
                costo = float(_input("Costo unitario (COP)") or "0")
                stock = int(_input("Stock inicial") or "0")
                
                p = _productos.crear_producto(id_sku, nombre, desc, precio, costo, stock)
                print(f"\n  ✅ {p} | Margen: {p.margen_porcentual:.1f}%")
            except ValueError as e:
                print(f"\n  ❌ Dato numérico inválido o error de negocio: {e}")
            _pausar()

        elif op == "2":
            _sep("BUSCAR PRODUCTO")
            p = _productos.obtener_producto(_input("ID del producto"))
            if p:
                print(f"\n  {p}\n  Costo: ${p.costo_unitario:,.0f} | Margen: {p.margen_porcentual:.1f}%")
            else:
                print("  ❌ No encontrado.")
            _pausar()

        elif op == "3":
            _sep("CATÁLOGO DE PRODUCTOS")
            ps = _productos.listar_productos()
            print("  (vacío)" if not ps else "")
            for p in ps:
                print(f"  • {p} | Margen: {p.margen_porcentual:.1f}%")
            _pausar()

        elif op == "4":
            _sep("ACTUALIZAR PRODUCTO")
            p = _productos.obtener_producto(_input("ID del producto"))
            if not p:
                print("  ❌ No encontrado.")
            else:
                nuevo_n = _input(f"Nombre [{p.nombre}]") or p.nombre
                nuevo_d = _input(f"Desc   [{p.descripcion}]") or p.descripcion
                try:
                    p.nombre = nuevo_n
                    p.descripcion = nuevo_d
                    _productos.actualizar_producto(p)
                    print(f"\n  ✅ Actualizado con éxito.")
                except ValueError as e:
                    print(f"\n  ❌ {e}")
            _pausar()

        elif op == "5":
            _sep("AJUSTAR STOCK")
            try:
                id_p = _input("ID del producto")
                cant = int(_input("Cantidad (+entrada / -salida)") or "0")
                p = _productos.ajustar_stock(id_p, cant)
                print(f"\n  ✅ Stock actualizado: {p}")
            except ValueError as e:
                print(f"\n  ❌ Entrada no válida: {e}")
            _pausar()

        elif op == "6":
            _sep("ACTUALIZAR PRECIO")
            try:
                id_p   = _input("ID del producto")
                precio = float(_input("Nuevo precio unitario") or "0")
                costo_str = _input("Nuevo costo (dejar vacío para no cambiar)")
                costo  = float(costo_str) if costo_str else None
                p = _productos.actualizar_precio(id_p, precio, costo)
                print(f"\n  ✅ {p} | Nuevo margen: {p.margen_porcentual:.1f}%")
            except ValueError as e:
                print(f"\n  ❌ Entrada económica inválida: {e}")
            _pausar()

        elif op == "7":
            _sep("ELIMINAR PRODUCTO")
            ok = _productos.eliminar_producto(_input("ID del producto"))
            print(f"\n  {'✅ Eliminado.' if ok else '❌ No encontrado.'}")
            _pausar()

        elif op == "0":
            break

# ── Submenú Facturas ──────────────────────────────────────────────────

def menu_facturas() -> None:
    while True:
        _sep("GESTIÓN DE FACTURAS")
        print("  1. Crear nueva factura")
        print("  2. Agregar línea a factura")
        print("  3. Ver factura por ID")
        print("  4. Listar todas las facturas")
        print("  5. Listar facturas de un cliente")
        print("  6. Listar facturas pendientes")
        print("  7. Registrar pago")
        print("  8. Anular factura")
        print("  9. Eliminar factura")
        print("  0. Volver")
        op = _input("Opción")

        if op == "1":
            _sep("CREAR FACTURA")
            try:
                f = _facturas.crear_factura(
                    _input("Número de factura (ej: FAC-2026-001)"),
                    _input("ID del cliente"),
                    _input("Fecha vencimiento (YYYY-MM-DD)"),
                    _input("Notas (opcional)"),
                )
                print(f"\n  ✅ {f}")
            except ValueError as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "2":
            _sep("AGREGAR LÍNEA")
            try:
                id_fac = _input("Número de factura")
                id_prd = _input("ID del producto")
                cantidad = int(_input("Cantidad") or "0")
                f = _facturas.agregar_linea_a_factura(id_fac, id_prd, cantidad)
                print(f"\n  ✅ Línea agregada. Total: ${f.total:,.0f}")
            except ValueError as e:
                print(f"\n  ❌ Cantidad incorrecta o error de negocio: {e}")
            _pausar()

        elif op == "3":
            _sep("VER FACTURA")
            f = _facturas.obtener_factura(_input("Número de factura"))
            if f:
                print(f"\n  {f}")
                print(f"  Emitida: {f.fecha_emision}  Vence: {f.fecha_vencimiento}")
                print(f"\n  {'Producto':<30} {'Cant':>5} {'P.Unit':>12} {'Subtotal':>14}")
                print(f"  {'─'*63}")
                for l in f.lineas:
                    print(f"  {l.nombre_producto:<30} {l.cantidad:>5} ${l.precio_unitario:>11,.0f} ${l.subtotal:>13,.0f}")
                print(f"  {'─'*63}")
                print(f"  {'TOTAL':>47} ${f.total:>13,.0f}")
                print(f"  {'Utilidad bruta':>47} ${f.utilidad_bruta:>13,.0f}")
            else:
                print("  ❌ No encontrada.")
            _pausar()

        elif op == "4":
            _sep("TODAS LAS FACTURAS")
            for f in _facturas.listar_facturas() or []:
                print(f"  • {f}")
            _pausar()

        elif op == "5":
            _sep("FACTURAS POR CLIENTE")
            for f in _facturas.listar_facturas_por_cliente(_input("ID del cliente")) or []:
                print(f"  • {f}")
            _pausar()

        elif op == "6":
            _sep("FACTURAS PENDIENTES")
            ps = _facturas.listar_pendientes()
            for f in ps:
                alerta = " ⚠ VENCIDA" if f.esta_vencida else ""
                print(f"  • {f}{alerta}")
            if not ps:
                print("  ✅ No hay facturas pendientes.")
            _pausar()

        elif op == "7":
            _sep("REGISTRAR PAGO")
            try:
                f = _facturas.pagar_factura(_input("Número de factura"))
                print(f"\n  ✅ {f}")
            except ValueError as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "8":
            _sep("ANULAR FACTURA")
            try:
                f = _facturas.anular_factura(_input("Número de factura"))
                print(f"\n  ✅ {f}")
            except ValueError as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "9":
            _sep("ELIMINAR FACTURA")
            ok = _facturas.eliminar_factura(_input("Número de factura"))
            print(f"\n  {'✅ Eliminada.' if ok else '❌ No encontrada.'}")
            _pausar()

        elif op == "0":
            break

# ── Submenú Reportes ──────────────────────────────────────────────────

def menu_reportes() -> None:
    while True:
        _sep("REPORTES FINANCIEROS DE CARTERA")
        print("  1. Resumen ejecutivo")
        print("  2. Top clientes por ventas")
        print("  3. Rentabilidad por producto")
        print("  4. Índice de morosidad")
        print("  5. Análisis avanzado (requiere pandas)")
        print("  0. Volver")
        op = _input("Opción")

        if op == "1":
            _sep("RESUMEN EJECUTIVO")
            r = _cartera.calcular_resumen_cartera()
            print(f"  Facturas activas   : {r['total_facturas']}")
            print(f"  Total facturado    : ${r['total_facturado']:>18,.2f}")
            print(f"  Total cobrado      : ${r['total_cobrado']:>18,.2f}")
            print(f"  Total pendiente    : ${r['total_pendiente']:>18,.2f}")
            print(f"  Utilidad bruta     : ${r['utilidad_bruta']:>18,.2f}")
            print(f"  Margen bruto       : {r['margen_bruto_pct']:>17.2f} %")
            print(f"  ROA de cartera     : {r['roa_cartera_pct']:>17.2f} %")
            print(f"  Tasa de cobranza   : {r['tasa_cobranza_pct']:>17.2f} %")
            _pausar()

        elif op == "2":
            _sep("TOP CLIENTES")
            try:
                n = int(_input("¿Cuántos clientes? [5]") or "5")
                print(f"\n  {'#':<4} {'Cliente':<35} {'Total Ventas':>14}")
                print(f"  {'─'*55}")
                for i, (nombre, total) in enumerate(_cartera.top_clientes_por_ventas(n), 1):
                    print(f"  {i:<4} {nombre:<35} ${total:>13,.0f}")
            except ValueError:
                print("\n  ❌ Por favor, introduce un número entero válido.")
            _pausar()

        elif op == "3":
            _sep("RENTABILIDAD POR PRODUCTO")
            datos = _cartera.rentabilidad_por_producto()
            if not datos:
                print("  (Sin datos de ventas)")
            else:
                print(f"\n  {'Producto':<30} {'Uds':>5} {'Ingresos':>14} {'Utilidad':>14} {'Margen':>7}")
                print(f"  {'─'*72}")
                for d in datos:
                    print(f"  {d['nombre']:<30} {d['unidades_vendidas']:>5} "
                          f"${d['total_vendido']:>13,.0f} ${d['utilidad_bruta']:>13,.0f} "
                          f"{d['margen_pct']:>6.1f}%")
            _pausar()

        elif op == "4":
            _sep("ÍNDICE DE MOROSIDAD")
            m = _cartera.calcular_indice_morosidad()
            print(f"  Monto pendiente total : ${m['monto_pendiente_total']:>14,.2f}")
            print(f"  Monto vencido          : ${m['monto_vencido']:>14,.2f}")
            print(f"  Índice de morosidad   : {m['indice_morosidad_pct']:>13.2f} %")
            _pausar()

        elif op == "5":
            _sep("ANÁLISIS AVANZADO")
            try:
                import analisis_cartera
                analisis_cartera.analizar_cartera(RUTA_JSON)
            except Exception as e:
                print(f"\n  ❌ {e}")
            _pausar()

        elif op == "0":
            break

# ── Demo con datos de ejemplo ─────────────────────────────────────────

def cargar_datos_demo() -> None:
    if _clientes.listar_clientes():
        print("  ℹ  Ya existen datos. Omitiendo carga demo.")
        return
    _sep("CARGANDO DATOS DE DEMOSTRACIÓN")
    for args in [
        ("CLI001","Tech Solutions SAS","info@techsol.co","6012345678","Bogotá"),
        ("CLI002","Distribuidora Norte","ventas@norte.co","6076543210","Medellín"),
        ("CLI003","Consultores Andes","andes@consul.co","6013219876","Bogotá"),
    ]:
        try: _clientes.crear_cliente(*args)
        except ValueError: pass

    for args in [
        ("PRD001","Licencia ERP Anual","Software ERP",4_800_000,1_200_000,50),
        ("PRD002","Consultoría TI (hora)","Hora especializada",250_000,80_000,200),
        ("PRD003","Servidor Cloud (mes)","Instancia cloud",1_500_000,600_000,100),
    ]:
        try: _productos.crear_producto(*args)
        except ValueError: pass

    for id_f, id_c, vence, lineas in [
        ("FAC-2026-001","CLI001","2026-06-30",[("PRD001",2),("PRD002",10)]),
        ("FAC-2026-002","CLI002","2026-07-15",[("PRD003",3)]),
        ("FAC-2026-003","CLI003","2026-05-10",[("PRD002",5)]),
    ]:
        try:
            _facturas.crear_factura(id_f, id_c, vence)
            for id_p, cant in lineas:
                _facturas.agregar_linea_a_factura(id_f, id_p, cant)
        except ValueError: pass

    try:
        _facturas.pagar_factura("FAC-2026-001")
    except ValueError: pass

    print("\n  ✅ Datos cargados correctamente.")
    _pausar()

# ── Menú principal ────────────────────────────────────────────────────

def menu_principal() -> None:
    while True:
        _limpiar()
        _sep("SISTEMA DE GESTIÓN FINANCIERA DE CARTERA  v1.1")
        print("  1. 👤  Gestión de Clientes")
        print("  2. 📦  Gestión de Productos / Servicios")
        print("  3. 🧾  Gestión de Facturas")
        print("  4. 📊  Reportes Financieros de Cartera")
        print("  ─────────────────────────────────────────")
        print("  5. 🎲  Cargar datos de demostración")
        print("  0. 🚪  Salir")
        _sep()
        op = _input("Selecciona una opción")

        if   op == "1": menu_clientes()
        elif op == "2": menu_productos()
        elif op == "3": menu_facturas()
        elif op == "4": menu_reportes()
        elif op == "5": cargar_datos_demo()
        elif op == "0":
            print("\n  👋 ¡Hasta luego!\n")
            sys.exit(0)
        else:
            print("  ⚠  Opción inválida.")
            _pausar()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        cargar_datos_demo()
        r = _cartera.calcular_resumen_cartera()
        _sep("RESUMEN DE CARTERA")
        for k, v in r.items():
            print(f"  {k:<25}: {v}")
        _sep()
    else:
        menu_principal()