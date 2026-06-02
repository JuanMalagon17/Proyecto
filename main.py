import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Importaciones para el Dashboard Gráfico
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.insert(0, os.path.dirname(__file__))

# ── 1. IMPORTACIONES DE TU BACKEND ─────────────────────────────────────────
from src.controllers.cartera_controller import CarteraController
from src.controllers.cliente_controller import ClienteController
from src.controllers.factura_controller import FacturaController
from src.controllers.producto_controller import ProductoController
from src.dao.cliente_dao import ClienteDao
from src.dao.factura_dao import FacturaDao
from src.dao.producto_dao import ProductoDao


# ── 1B. PATRÓN CHAIN OF RESPONSIBILITY: EMAIL NOTIFICATION SERVICE ─────────
class ManejadorNotificacionBase:
    """Manejador base para la cadena de responsabilidades."""
    def __init__(self):
        self._siguiente_manejador = None

    def establecer_siguiente(self, manejador): # type: ignore
        self._siguiente_manejador = manejador # type: ignore
        return manejador # type: ignore

    def procesar_notificacion(self, evento: str, datos: dict): # type: ignore
        if self._siguiente_manejador: # type: ignore
            return self._siguiente_manejador.procesar_notificacion(evento, datos) # type: ignore
        return False


class ManejadorEmailFacturacion(ManejadorNotificacionBase):
    """Eslabón encargado de correos sobre facturas nuevas o anuladas."""
    def procesar_notificacion(self, evento: str, datos: dict): # type: ignore
        if evento in ["factura_creada", "factura_anulada"]:
            num = datos.get("numero", "N/A") # type: ignore
            cliente = datos.get("cliente_id", "Cliente") # type: ignore
            total = datos.get("total", 0) # type: ignore
            
            print(f"\n[EMAIL SERVICE] 📧 Enviando correo al Cliente {cliente}...")
            print(f"👉 Asunto: Actualización de Estado - Factura {num}")
            print(f"👉 Cuerpo: El documento {num} por valor de ${total:,.0f} COP ha cambiado su estado a [{evento.upper()}].")
            return True
        return super().procesar_notificacion(evento, datos) # type: ignore


class ManejadorEmailCartera(ManejadorNotificacionBase):
    """Eslabón encargado de cobranza y confirmación de pagos (Dirigido a Salle)."""
    def procesar_notificacion(self, evento: str, datos: dict): # type: ignore
        if evento in ["factura_pagada", "factura_vencida"]:
            num = datos.get("numero", "N/A") # type: ignore
            cliente = datos.get("cliente_id", "Cliente") # type: ignore
            
            print(f"\n[EMAIL SERVICE] 💵 Alerta de Cartera / Tesorería...")
            
            if evento == "factura_pagada":
                destinatario = "raranda@unisalle.edu.co"
                print(f"👉 Enviando correo a: {destinatario}")
                print(f"👉 Asunto: [PAGO REGISTRADO] Confirmación de Transacción - Factura {num}")
                print(f"👉 Cuerpo: Estimado equipo, se notifica que se ha registrado exitosamente el pago "
                      f"del documento {num} asociado al cliente {cliente} en el sistema.")
            elif evento == "factura_vencida":
                print(f"👉 Asunto: ⚠️ RECORDATORIO DE PAGO - Factura Vencida {num}")
                print(f"👉 Cuerpo: El documento {num} presenta saldo en mora. Por favor comunicarse con cartera.")
                
            return True
        return super().procesar_notificacion(evento, datos) # type: ignore


class ManejadorEmailAuditoria(ManejadorNotificacionBase):
    """Eslabón de seguridad que audita eliminaciones críticas."""
    def procesar_notificacion(self, evento: str, datos: dict): # type: ignore
        if evento in ["cliente_eliminado", "factura_eliminada"]: 
            id_ref = datos.get("id", "N/A") # type: ignore
            
            print(f"\n[EMAIL SERVICE] 🚨 ALERTA DE SEGURIDAD INTERNA...")
            print(f"👉 Asunto: Registro Eliminado del Sistema - {evento.upper()}")
            print(f"👉 Cuerpo: Se ha eliminado permanentemente el registro {id_ref} del archivo JSON.")
            return True
        return super().procesar_notificacion(evento, datos) # type: ignore


# ── 2. ENSAMBLAJE DE DEPENDENCIAS (DIP) ──────────────────────────────────
RUTA_JSON = os.path.join(os.path.dirname(__file__), "data", "facturas.json")

_factura_dao  = FacturaDao(RUTA_JSON)
_cliente_dao  = ClienteDao(RUTA_JSON)
_producto_dao = ProductoDao(RUTA_JSON)

_clientes  = ClienteController(_cliente_dao, _factura_dao)
_productos = ProductoController(_producto_dao)
_facturas  = FacturaController(_factura_dao, _cliente_dao, _producto_dao)
_cartera   = CarteraController(_factura_dao)

# Construcción de la cadena del Servicio de Correos
manejador_facturas = ManejadorEmailFacturacion()
manejador_cartera = ManejadorEmailCartera()
manejador_auditoria = ManejadorEmailAuditoria()

manejador_facturas.establecer_siguiente(manejador_cartera).establecer_siguiente(manejador_auditoria) # type: ignore
_email_service = manejador_facturas


# ── 3. VISTA MODULAR: GESTIÓN DE CLIENTES ─────────────────────────────────
class VistaClientes(ttk.Frame):
    def __init__(self, parent): # type: ignore
        super().__init__(parent) # type: ignore
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Formulario (Izquierda)
        frame_izq = ttk.LabelFrame(self, text=" Formulario de Cliente ", padding=10)
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        campos = ["ID / NIT", "Nombre", "Email", "Teléfono", "Dirección"]
        self.inputs = {}
        for i, campo in enumerate(campos):
            ttk.Label(frame_izq, text=f"{campo}:").grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(frame_izq, width=28)
            entry.grid(row=i, column=1, pady=3, padx=5)
            self.inputs[campo] = entry # type: ignore
            
        self.btn_crear = ttk.Button(frame_izq, text="➕ Crear Cliente", command=self.crear)
        self.btn_crear.grid(row=5, column=0, columnspan=2, pady=8, sticky="ewe")
        
        self.btn_actualizar = ttk.Button(frame_izq, text="💾 Guardar Cambios", command=self.actualizar, state="disabled")
        self.btn_actualizar.grid(row=6, column=0, columnspan=2, pady=4, sticky="ewe")
        
        self.btn_limpiar = ttk.Button(frame_izq, text="🧹 Limpiar Campos", command=self.limpiar_formulario)
        self.btn_limpiar.grid(row=7, column=0, columnspan=2, pady=4, sticky="ewe")

        # Tabla y Acciones (Derecha)
        frame_der = ttk.Frame(self)
        frame_der.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        frame_der.grid_rowconfigure(0, weight=1)
        frame_der.grid_columnconfigure(0, weight=1)
        
        self.tabla = ttk.Treeview(frame_der, columns=("id", "nombre", "email", "estado"), show="headings")
        self.tabla.heading("id", text="ID / NIT")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("email", text="Email")
        self.tabla.heading("estado", text="Estado")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_seleccion) # type: ignore
        
        frame_botones = ttk.Frame(frame_der)
        frame_botones.grid(row=1, column=0, sticky="ew", pady=5)
        
        ttk.Button(frame_botones, text="🔄 Activar / Desactivar", command=self.alternar_estado).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="❌ Eliminar Cliente", command=self.eliminar).pack(side="right", padx=5)
        
        self.refrescar_tabla()

    def refrescar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for c in _clientes.listar_clientes():
            attrs = vars(c)
            id_real = attrs.get('id_cliente') or attrs.get('id') or attrs.get('nit') or list(attrs.values())[0]
            est = "Activo" if attrs.get('activo', True) else "Inactivo"
            self.tabla.insert("", "end", values=(id_real, c.nombre, c.email, est))

    def cargar_seleccion(self, event): # type: ignore
        sel = self.tabla.selection()
        if not sel: return
        c = _clientes.obtener_cliente(str(self.tabla.item(sel[0])['values'][0]))
        if c:
            self.limpiar_formulario()
            attrs = vars(c)
            id_real = attrs.get('id_cliente') or attrs.get('id') or attrs.get('nit') or list(attrs.values())[0]
            tel_real = attrs.get('telefono') or attrs.get('tel') or ""
            dir_real = attrs.get('direccion') or attrs.get('dir') or ""
            
            self.inputs["ID / NIT"].insert(0, id_real) # type: ignore
            self.inputs["ID / NIT"].config(state="disabled") # type: ignore
            self.inputs["Nombre"].insert(0, c.nombre) # type: ignore
            self.inputs["Email"].insert(0, c.email) # type: ignore
            self.inputs["Teléfono"].insert(0, tel_real) # type: ignore
            self.inputs["Dirección"].insert(0, dir_real) # type: ignore
            self.btn_crear.config(state="disabled")
            self.btn_actualizar.config(state="normal")

    def limpiar_formulario(self):
        self.inputs["ID / NIT"].config(state="normal") # type: ignore
        for entry in self.inputs.values(): entry.delete(0, tk.END) # type: ignore
        self.btn_crear.config(state="normal")
        self.btn_actualizar.config(state="disabled")

    def crear(self):
        try:
            _clientes.crear_cliente(
                self.inputs["ID / NIT"].get(), self.inputs["Nombre"].get(), # type: ignore
                self.inputs["Email"].get(), self.inputs["Teléfono"].get(), self.inputs["Dirección"].get() # type: ignore
            )
            messagebox.showinfo("✅ Éxito", "Cliente registrado correctamente.")
            self.refrescar_tabla(); self.limpiar_formulario()
        except ValueError as e: messagebox.showerror("❌ Error", str(e))

    def actualizar(self):
        try:
            c = _clientes.obtener_cliente(self.inputs["ID / NIT"].get()) # type: ignore
            attrs = vars(c)
            
            for k in attrs.keys():
                if 'nombre' in k: setattr(c, k, self.inputs["Nombre"].get()) # type: ignore
                elif 'email' in k: setattr(c, k, self.inputs["Email"].get()) # type: ignore
                elif 'telefono' in k: setattr(c, k, self.inputs["Teléfono"].get()) # type: ignore
                elif 'direccion' in k: setattr(c, k, self.inputs["Dirección"].get()) # type: ignore
                
            _clientes.actualizar_cliente(c) # type: ignore
            messagebox.showinfo("✅ Éxito", "Cliente actualizado con éxito.")
            self.refrescar_tabla(); self.limpiar_formulario()
        except ValueError as e: messagebox.showerror("❌ Error", str(e))

    def alternar_estado(self):
        sel = self.tabla.selection()
        if not sel: return messagebox.showwarning("⚠ Atención", "Selecciona un cliente.")
        id_c = self.tabla.item(sel[0])['values'][0]
        est = self.tabla.item(sel[0])['values'][3]
        try:
            _clientes.desactivar_cliente(id_c) if est == "Activo" else _clientes.activar_cliente(id_c)
            self.refrescar_tabla()
            messagebox.showinfo("✅ Éxito", "Estado del cliente modificado.")
        except ValueError as e: messagebox.showerror("❌ Error", str(e))

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel: return messagebox.showwarning("⚠ Atención", "Selecciona un cliente.")
        id_c = self.tabla.item(sel[0])['values'][0]
        if messagebox.askyesno("❓ Confirmar", f"¿Seguro que deseas eliminar al cliente {id_c}?"):
            try:
                _clientes.eliminar_cliente(id_c)
                _email_service.procesar_notificacion("cliente_eliminado", {"id": id_c}) # type: ignore
                messagebox.showinfo("✅ Éxito", "Cliente eliminado.")
                self.refrescar_tabla(); self.limpiar_formulario()
            except ValueError as e: messagebox.showerror("❌ Error", str(e))


# ── 4. VISTA MODULAR: GESTIÓN DE PRODUCTOS ────────────────────────────────
class VistaProductos(ttk.Frame):
    def __init__(self, parent): # type: ignore
        super().__init__(parent) # type: ignore
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Formulario
        frame_izq = ttk.LabelFrame(self, text=" Formulario de Producto ", padding=10)
        frame_izq.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        campos = ["ID / SKU", "Nombre", "Descripción", "Precio (COP)", "Costo (COP)", "Stock Inicial"]
        self.inputs = {}
        for i, campo in enumerate(campos):
            ttk.Label(frame_izq, text=f"{campo}:").grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(frame_izq, width=25)
            entry.grid(row=i, column=1, pady=3, padx=5)
            self.inputs[campo] = entry # type: ignore
            
        ttk.Button(frame_izq, text="➕ Crear Producto", command=self.crear).grid(row=6, column=0, columnspan=2, pady=4, sticky="ewe")
        self.btn_edit = ttk.Button(frame_izq, text="💾 Actualizar Info Básica", command=self.actualizar, state="disabled")
        self.btn_edit.grid(row=7, column=0, columnspan=2, pady=4, sticky="ewe")
        
        # Ajustes rápidos financieros/inventario
        frame_ajustes = ttk.LabelFrame(frame_izq, text=" Ajustes Rápidos ", padding=5)
        frame_ajustes.grid(row=8, column=0, columnspan=2, pady=10, sticky="ew")
        
        ttk.Label(frame_ajustes, text="Cantidad Stock (+/-):").grid(row=0, column=0, sticky="w")
        self.txt_stock_ajuste = ttk.Entry(frame_ajustes, width=10)
        self.txt_stock_ajuste.grid(row=0, column=1, pady=2)
        ttk.Button(frame_ajustes, text="Aplicar Stock", command=self.ajustar_stock).grid(row=0, column=2, padx=2)
        
        # Tabla
        frame_der = ttk.Frame(self)
        frame_der.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        frame_der.grid_rowconfigure(0, weight=1)
        frame_der.grid_columnconfigure(0, weight=1)
        
        self.tabla = ttk.Treeview(frame_der, columns=("sku", "nombre", "precio", "stock", "margen"), show="headings")
        self.tabla.heading("sku", text="ID / SKU")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("precio", text="Precio")
        self.tabla.heading("stock", text="Stock")
        self.tabla.heading("margen", text="Margen %")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        
        self.tabla.bind("<<TreeviewSelect>>", self.cargar_seleccion) # type: ignore
        ttk.Button(frame_der, text="❌ Eliminar Producto", command=self.eliminar).grid(row=1, column=0, pady=5, sticky="e")
        
        self.refrescar_tabla()

    def refrescar_tabla(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        for p in _productos.listar_productos():
            attrs = vars(p)
            id_real = attrs.get('id_producto') or attrs.get('id_sku') or attrs.get('id') or list(attrs.values())[0]
            stock_real = attrs.get('stock_actual') or attrs.get('stock') or attrs.get('cantidad') or 0
            precio_real = attrs.get('precio_unitario') or attrs.get('precio') or attrs.get('valor') or 0
            
            margen_real = attrs.get('margen_porcentual') or attrs.get('margen')
            if margen_real is None:
                costo_real = attrs.get('costo_unitario') or attrs.get('costo') or 0
                margen_real = (((precio_real - costo_real) / precio_real) * 100) if precio_real > 0 else 0
                
            self.tabla.insert("", "end", values=(id_real, p.nombre, f"${precio_real:,.0f}", stock_real, f"{margen_real:.1f}%"))

    def cargar_seleccion(self, event): # type: ignore
        sel = self.tabla.selection()
        if not sel: return
        p = _productos.obtener_producto(str(self.tabla.item(sel[0])['values'][0]))
        if p:
            self.limpiar_formulario()
            attrs = vars(p)
            id_real = attrs.get('id_producto') or attrs.get('id_sku') or attrs.get('id') or list(attrs.values())[0]
            stock_real = attrs.get('stock_actual') or attrs.get('stock') or attrs.get('cantidad') or 0
            precio_real = attrs.get('precio_unitario') or attrs.get('precio') or attrs.get('valor') or 0
            costo_real = attrs.get('costo_unitario') or attrs.get('costo') or 0
            desc_real = attrs.get('descripcion') or attrs.get('detalle') or ""
            
            self.inputs["ID / SKU"].insert(0, id_real) # type: ignore
            self.inputs["ID / SKU"].config(state="disabled") # type: ignore
            self.inputs["Nombre"].insert(0, p.nombre) # type: ignore
            self.inputs["Descripción"].insert(0, desc_real) # type: ignore
            self.inputs["Precio (COP)"].insert(0, precio_real) # type: ignore
            self.inputs["Costo (COP)"].insert(0, costo_real) # type: ignore
            self.inputs["Stock Inicial"].insert(0, stock_real) # type: ignore
            self.inputs["Stock Inicial"].config(state="disabled") # type: ignore 
            self.btn_edit.config(state="normal")  

    def limpiar_formulario(self):
        self.inputs["ID / SKU"].config(state="normal") # type: ignore
        self.inputs["Stock Inicial"].config(state="normal") # type: ignore
        for entry in self.inputs.values(): entry.delete(0, tk.END) # type: ignore
        self.txt_stock_ajuste.delete(0, tk.END)
        self.btn_edit.config(state="disabled")

    def crear(self):
        try:
            _productos.crear_producto(
                self.inputs["ID / SKU"].get(), self.inputs["Nombre"].get(), self.inputs["Descripción"].get(), # type: ignore
                float(self.inputs["Precio (COP)"].get() or 0), float(self.inputs["Costo (COP)"].get() or 0), # type: ignore
                int(self.inputs["Stock Inicial"].get() or 0) # type: ignore
            )
            messagebox.showinfo("✅ Éxito", "Producto añadido al catálogo.")
            self.refrescar_tabla(); self.limpiar_formulario()
        except ValueError as e: messagebox.showerror("❌ Error", f"Dato inválido: {e}")

    def actualizar(self):
        try:
            p = _productos.obtener_producto(self.inputs["ID / SKU"].get()) # type: ignore
            p.nombre = self.inputs["Nombre"].get() # type: ignore
            attrs = vars(p)
            desc_key = [k for k in attrs.keys() if 'desc' in k]
            if desc_key: setattr(p, desc_key[0], self.inputs["Descripción"].get()) # type: ignore
             
            _productos.actualizar_producto(p) # type: ignore
            messagebox.showinfo("✅ Éxito", "Información base actualizada.")
            self.refrescar_tabla(); self.limpiar_formulario()
        except ValueError as e: messagebox.showerror("❌ Error", str(e))

    def ajustar_stock(self):
        sel = self.tabla.selection()
        if not sel: return messagebox.showwarning("⚠ Atención", "Selecciona un producto.")
        sku = self.tabla.item(sel[0])['values'][0]
        try:
            cant = int(self.txt_stock_ajuste.get() or 0)
            _productos.ajustar_stock(sku, cant)
            messagebox.showinfo("✅ Éxito", "Inventario actualizado.")
            self.refrescar_tabla(); self.limpiar_formulario()
        except ValueError: messagebox.showerror("❌ Error", "Introduce una cantidad entera válida.")

    def eliminar(self):
        sel = self.tabla.selection()
        if not sel: return
        sku = self.tabla.item(sel[0])['values'][0]
        if messagebox.askyesno("❓ Confirmar", f"¿Eliminar producto {sku}?"):
            _productos.eliminar_producto(sku)
            self.refrescar_tabla(); self.limpiar_formulario()
            messagebox.showinfo("✅ Éxito", "Producto removido.")


# ── 5. VISTA MODULAR: GESTIÓN DE FACTURAS ─────────────────────────────────
class VistaFacturas(ttk.Frame):
    def __init__(self, parent): # type: ignore
        super().__init__(parent) # type: ignore
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # PANEL IZQUIERDO: Historial
        frame_lista = ttk.LabelFrame(self, text=" Historial de Facturas ", padding=10)
        frame_lista.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        frame_lista.grid_rowconfigure(1, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        frame_filtros = ttk.Frame(frame_lista)
        frame_filtros.grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Button(frame_filtros, text="Ver Todas", command=self.refrescar_todas).pack(side="left", padx=2)
        ttk.Button(frame_filtros, text="Ver Pendientes", command=self.refrescar_pendientes).pack(side="left", padx=2)
        
        self.tabla_fac = ttk.Treeview(frame_lista, columns=("num", "cliente", "total", "estado"), show="headings")
        self.tabla_fac.heading("num", text="Número Factura")
        self.tabla_fac.heading("cliente", text="Cliente ID")
        self.tabla_fac.heading("total", text="Total")
        self.tabla_fac.heading("estado", text="Estado")
        self.tabla_fac.grid(row=1, column=0, sticky="nsew")
        self.tabla_fac.bind("<<TreeviewSelect>>", self.cargar_detalle_factura) # type: ignore
        
        frame_ops = ttk.Frame(frame_lista)
        frame_ops.grid(row=2, column=0, sticky="ew", pady=5)
        ttk.Button(frame_ops, text="💵 Registrar Pago", command=self.pagar).pack(side="left", padx=2)
        ttk.Button(frame_ops, text="🚫 Anular", command=self.anular).pack(side="left", padx=2)
        ttk.Button(frame_ops, text="❌ Eliminar", command=self.eliminar).pack(side="right", padx=2)

        # PANEL DERECHO: Detalle
        self.frame_der = ttk.LabelFrame(self, text=" Visor y Nueva Facturación ", padding=10)
        self.frame_der.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.configurar_modo_espera()
        self.refrescar_todas()

    def configurar_modo_espera(self):
        for widget in self.frame_der.winfo_children(): widget.destroy()
        ttk.Label(self.frame_der, text="Selecciona una factura del historial o pulsa el botón inferior.", font=("Arial", 10, "italic")).pack(pady=40)
        ttk.Button(self.frame_der, text="✨ Crear Nueva Factura", command=self.configurar_modo_creacion).pack(pady=10)

    def refrescar_todas(self):
        for item in self.tabla_fac.get_children(): self.tabla_fac.delete(item)
        lista = _facturas.listar_facturas()
        if lista:
            for f in lista:
                attrs = vars(f)
                num = attrs.get('numero_factura') or attrs.get('id_factura') or list(attrs.values())[0]
                cli = attrs.get('id_cliente') or attrs.get('cliente_id') or ""
                est_obj = attrs.get('estado')
                est_name = est_obj.name if hasattr(est_obj, 'name') else str(est_obj) # type: ignore
                alerta = " ⚠ VENCIDA" if attrs.get('esta_vencida', False) else ""
                self.tabla_fac.insert("", "end", values=(num, cli, f"${f.total:,.0f}", f"{est_name}{alerta}"))

    def refrescar_pendientes(self):
        for item in self.tabla_fac.get_children(): self.tabla_fac.delete(item)
        lista = _facturas.listar_pendientes()
        if lista:
            for f in lista:
                attrs = vars(f)
                num = attrs.get('numero_factura') or attrs.get('id_factura') or list(attrs.values())[0]
                cli = attrs.get('id_cliente') or attrs.get('cliente_id') or ""
                est_obj = attrs.get('estado')
                est_name = est_obj.name if hasattr(est_obj, 'name') else str(est_obj) # type: ignore
                alerta = " ⚠ VENCIDA" if attrs.get('esta_vencida', False) else ""
                self.tabla_fac.insert("", "end", values=(num, cli, f"${f.total:,.0f}", f"{est_name}{alerta}"))

    def cargar_detalle_factura(self, event): # type: ignore
        sel = self.tabla_fac.selection()
        if not sel: return
        num_fac = self.tabla_fac.item(sel[0])['values'][0]
        f = _facturas.obtener_factura(num_fac)
        if not f: return
        
        for widget in self.frame_der.winfo_children(): widget.destroy()
        attrs = vars(f)
        cli = attrs.get('id_cliente') or attrs.get('cliente_id') or ""
        vence = attrs.get('fecha_vencimiento') or attrs.get('vencimiento') or ""
        est_obj = attrs.get('estado')
        est_name = est_obj.name if hasattr(est_obj, 'name') else str(est_obj) # type: ignore
        
        ttk.Label(self.frame_der, text=f"Detalle Factura: {num_fac}", font=("Arial", 12, "bold")).pack(anchor="w")
        ttk.Label(self.frame_der, text=f"Cliente ID: {cli} | Vence: {vence}").pack(anchor="w", pady=2)
        ttk.Label(self.frame_der, text=f"Estado del Documento: {est_name}", font=("Arial", 9, "bold")).pack(anchor="w")
        
        tabla_items = ttk.Treeview(self.frame_der, columns=("p", "cant", "sub"), show="headings", height=8)
        tabla_items.heading("p", text="Producto/Servicio")
        tabla_items.heading("cant", text="Cant")
        tabla_items.heading("sub", text="Subtotal")
        tabla_items.pack(fill="both", expand=True, pady=10)
        
        lineas = attrs.get('lineas') or [] # type: ignore
        for l in lineas: # type: ignore
            l_attrs = vars(l) # type: ignore
            p_name = l_attrs.get('nombre_producto') or l_attrs.get('producto_id') or "Item" # type: ignore
            cant = l_attrs.get('amount') or l_attrs.get('cantidad') or 0 # type: ignore
            sub = l_attrs.get('subtotal') or 0 # type: ignore
            tabla_items.insert("", "end", values=(p_name, cant, f"${sub:,.0f}")) # type: ignore
             
        ttk.Label(self.frame_der, text=f"TOTAL DOCUMENTO: ${f.total:,.0f}", font=("Arial", 11, "bold")).pack(anchor="e")
        ttk.Button(self.frame_der, text="⬅ Volver", command=self.configurar_modo_espera).pack(anchor="w", pady=5)

    def configurar_modo_creacion(self):
        for widget in self.frame_der.winfo_children(): widget.destroy()
        ttk.Label(self.frame_der, text="📝 Emitir Nueva Factura", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
        
        f_campos = ttk.Frame(self.frame_der)
        f_campos.pack(fill="x", pady=5)
        
        ttk.Label(f_campos, text="Número Factura:").grid(row=0, column=0, sticky="w")
        txt_num = ttk.Entry(f_campos, width=20); txt_num.grid(row=0, column=1, pady=2)
        txt_num.insert(0, f"FAC-{datetime.now().year}-00")
        
        ttk.Label(f_campos, text="ID Cliente:").grid(row=1, column=0, sticky="w")
        txt_cli = ttk.Entry(f_campos, width=20); txt_cli.grid(row=1, column=1, pady=2)
        
        ttk.Label(f_campos, text="Vence (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        txt_vence = ttk.Entry(f_campos, width=20); txt_vence.grid(row=2, column=1, pady=2)
        txt_vence.insert(0, f"{datetime.now().year}-12-31")

        lbl_lineas = ttk.LabelFrame(self.frame_der, text=" Agregar Ítems / Líneas de Venta ", padding=5)
        lbl_lineas.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(lbl_lineas, text="ID Producto:").grid(row=0, column=0, sticky="w")
        txt_prod_id = ttk.Entry(lbl_lineas, width=12); txt_prod_id.grid(row=0, column=1)
        
        ttk.Label(lbl_lineas, text="Cant:").grid(row=0, column=2, sticky="w")
        txt_prod_cant = ttk.Entry(lbl_lineas, width=6); txt_prod_cant.grid(row=0, column=3)
        
        lista_lineas_temp = []
        lbl_resumen_items = ttk.Label(lbl_lineas, text="Items agregados: 0", font=("Arial", 9, "italic"))
        lbl_resumen_items.grid(row=1, column=0, columnspan=4, pady=5)
        
        def push_linea():
            p_id = txt_prod_id.get().strip()
            c_str = txt_prod_cant.get().strip()
            if p_id and c_str.isdigit():
                lista_lineas_temp.append((p_id, int(c_str))) # type: ignore
                lbl_resumen_items.config(text=f"Items agregados: {len(lista_lineas_temp)} (Listos para procesar)") # type: ignore
                txt_prod_id.delete(0, tk.END); txt_prod_cant.delete(0, tk.END)
            else: messagebox.showwarning("⚠ Cuidado", "Campos de ítems inválidos.")
            
        ttk.Button(lbl_lineas, text="➕ Añadir Línea", command=push_linea).grid(row=0, column=4, padx=5)

        def procesar_factura_completa():
            num = txt_num.get().strip()
            cli = txt_cli.get().strip()
            vence = txt_vence.get().strip()
            if not num or not cli or not lista_lineas_temp:
                return messagebox.showerror("❌ Error", "Faltan datos de cabecera o ítems.")
            try:
                _facturas.crear_factura(num, cli, vence, "Generada vía GUI")
                for p_id, cant in lista_lineas_temp: # type: ignore
                    _facturas.agregar_linea_a_factura(num, p_id, cant) # type: ignore
                
                f_creada = _facturas.obtener_factura(num)
                total_real = f_creada.total if f_creada else 0
                
                _email_service.procesar_notificacion("factura_creada", {"numero": num, "cliente_id": cli, "total": total_real}) # type: ignore
                messagebox.showinfo("✅ Éxito", f"Factura {num} emitida de forma completa.")
                self.refrescar_todas(); self.configurar_modo_espera()
            except ValueError as e: messagebox.showerror("❌ Error Comercial", str(e))

        f_control = ttk.Frame(self.frame_der)
        f_control.pack(fill="x", pady=5)
        ttk.Button(f_control, text="💾 Emitir Factura Total", command=procesar_factura_completa).pack(side="right")
        ttk.Button(f_control, text="❌ Cancelar", command=self.configurar_modo_espera).pack(side="left")

    def pagar(self):
        sel = self.tabla_fac.selection()
        if not sel: return messagebox.showwarning("⚠", "Selecciona una factura.")
        num = self.tabla_fac.item(sel[0])['values'][0]
        try:
            _facturas.pagar_factura(num)
            f = _facturas.obtener_factura(num)
            cli = vars(f).get('id_cliente') or vars(f).get('cliente_id') if f else "Cliente"
            
            _email_service.procesar_notificacion("factura_pagada", {"numero": num, "cliente_id": cli}) # type: ignore
            messagebox.showinfo("✅ Éxito", f"Pago cargado a la factura {num}")
            self.refrescar_todas(); self.configurar_modo_espera()
        except ValueError as e: messagebox.showerror("❌ Error", str(e))

    def anular(self):
        sel = self.tabla_fac.selection()
        if not sel: return
        num = self.tabla_fac.item(sel[0])['values'][0]
        if messagebox.askyesno("❓ Confirmar", f"¿Deseas anular la factura {num}?"):
            try:
                _facturas.anular_factura(num)
                messagebox.showinfo("✅ Éxito", "Factura anulada.")
                self.refrescar_todas(); self.configurar_modo_espera()
            except ValueError as e: messagebox.showerror("❌ Error", str(e))

    def eliminar(self):
        sel = self.tabla_fac.selection()
        if not sel: return
        num = self.tabla_fac.item(sel[0])['values'][0]
        if messagebox.askyesno("❓ Confirmar", f"¿Eliminar permanentemente la factura {num}?"):
            _facturas.eliminar_factura(num)
            self.refrescar_todas(); self.configurar_modo_espera()
            messagebox.showinfo("✅ Éxito", "Registro borrado.")


# ── 6. VISTA MODULAR: REPORTES FINANCIEROS (Dashboard Gráfico y Exportación) ──
class VistaReportes(ttk.Frame):
    def __init__(self, parent): # type: ignore
        super().__init__(parent) # type: ignore
        
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)
        
        # PANEL IZQUIERDO: KPIs
        frame_izq_contenedor = ttk.Frame(self)
        frame_izq_contenedor.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.frame_kpis = ttk.LabelFrame(frame_izq_contenedor, text=" 📊 Indicadores Clave (KPI) ", padding=10)
        self.frame_kpis.pack(fill="both", expand=True)
        
        self.lbl_total_facturado = self.crear_tarjeta(self.frame_kpis, "TOTAL FACTURADO", "$0", "#1E3A8A") # type: ignore
        self.lbl_total_cobrado   = self.crear_tarjeta(self.frame_kpis, "FLUJO COBRADO", "$0", "#065F46") # type: ignore
        self.lbl_total_pendiente = self.crear_tarjeta(self.frame_kpis, "CARTERA PENDIENTE", "$0", "#9A3412") # type: ignore
        self.lbl_morosidad       = self.crear_tarjeta(self.frame_kpis, "ÍNDICE DE MOROSIDAD", "0%", "#991B1B") # type: ignore
        
        # Herramientas Pandas
        self.frame_acciones = ttk.LabelFrame(frame_izq_contenedor, text=" 🛠️ Herramientas de Datos ", padding=10)
        self.frame_acciones.pack(fill="x", pady=(10, 0))
        
        ttk.Button(self.frame_acciones, text="🔄 Recalcular Tablero", command=self.ejecutar_calculos).pack(fill="x", pady=3)
        ttk.Button(self.frame_acciones, text="🐼 Ejecutar Script Pandas (Exportar CSV)", command=self.ejecutar_pandas_avanzado).pack(fill="x", pady=3)
        
        # PANEL DERECHO: Pestañas
        self.notebook_rep = ttk.Notebook(self)
        self.notebook_rep.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.frame_graficos = ttk.Frame(self.notebook_rep, padding=5)
        self.notebook_rep.add(self.frame_graficos, text=" 📈 Vista Gráfica ")
        
        self.txt_resumen = tk.Text(self.notebook_rep, font=("Courier", 10), bg="#F9F9F9", wrap="none")
        self.notebook_rep.add(self.txt_resumen, text=" Resumen Ejecutivo ")
        
        self.txt_rentabilidad = tk.Text(self.notebook_rep, font=("Courier", 10), bg="#F9F9F9", wrap="none")
        self.notebook_rep.add(self.txt_rentabilidad, text=" Rentabilidad por Producto ")
        
        self.txt_morosidad = tk.Text(self.notebook_rep, font=("Courier", 10), bg="#F9F9F9", wrap="none")
        self.notebook_rep.add(self.txt_morosidad, text=" Índices de Morosidad ")
        
        self.canvas_widget = None
        self.ejecutar_calculos()

    def crear_tarjeta(self, parent, titulo, valor_defecto, color_hex): # type: ignore
        frame = tk.Frame(parent, bg="#FFFFFF", bd=1, relief="solid", highlightbackground=color_hex, highlightthickness=2) # type: ignore
        frame.pack(fill="x", pady=5, ipady=4) # type: ignore
        
        lbl_tit = tk.Label(frame, text=titulo, font=("Arial", 8, "bold"), fg="#6B7280", bg="#FFFFFF") # type: ignore
        lbl_tit.pack(anchor="w", padx=8, pady=(2,0))
        
        lbl_val = tk.Label(frame, text=valor_defecto, font=("Consolas", 13, "bold"), fg=color_hex, bg="#FFFFFF") # type: ignore
        lbl_val.pack(anchor="w", padx=8, pady=(1,3))
        return lbl_val

    def ejecutar_calculos(self):
        r = _cartera.calcular_resumen_cartera() or {}
        m = _cartera.calcular_indice_morosidad() or {}
        datos_p = _cartera.rentabilidad_por_producto() or []
        
        self.lbl_total_facturado.config(text=f"${r.get('total_facturado', 0):,.0f} COP")
        self.lbl_total_cobrado.config(text=f"${r.get('total_cobrado', 0):,.0f} COP")
        self.lbl_total_pendiente.config(text=f"${r.get('total_pendiente', 0):,.0f} COP")
        
        idx_mora = m.get('indice_morosidad_pct') or m.get('porcentaje_morosidad', 0)
        self.lbl_morosidad.config(text=f"{idx_mora:.2f} %")
        
        # Reportes en Texto
        txt_res = (
            f"===========================================================\n"
            f"                    RESUMEN CORPORATIVO                    \n"
            f"===========================================================\n"
            f" Facturas Procesadas Totales : {r.get('total_facturas', 0)}\n"
            f" Volumen Total Facturado    : ${r.get('total_facturado', 0):,.2f}\n"
            f" Flujo Neto Cobrado          : ${r.get('total_cobrado', 0):,.2f}\n"
            f" Saldo Neto Pendiente       : ${r.get('total_pendiente', 0):,.2f}\n"
            f"-----------------------------------------------------------\n"
            f" Utilidad Bruta General     : ${r.get('utilidad_bruta', 0):,.2f}\n"
            f" Margen de Operación (%)    : {r.get('margen_bruto_pct', 0):.2f} %\n"
            f" Tasa Real de Cobranza (%)  : {r.get('tasa_cobranza_pct', 0):.2f} %\n"
            f"===========================================================\n"
        )
        self.txt_resumen.config(state="normal")
        self.txt_resumen.delete("1.0", tk.END); self.txt_resumen.insert("1.0", txt_res)
        self.txt_resumen.config(state="disabled")

        txt_rent = f"{'Producto/SKU':<25} {'Unidades':<10} {'Ingresos':<15} {'Margen %':<10}\n" + "─"*65 + "\n"
        if datos_p:
            for d in datos_p:
                sku_txt = d.get('nombre') or d.get('id_sku') or "Item"
                uni = d.get('unidades_vendidas') or d.get('cantidad') or 0
                ing = d.get('total_vendido') or d.get('ingresos') or 0
                mar = d.get('margen_pct') or d.get('margen') or 0
                txt_rent += f"{sku_txt:<25} {uni:<10} ${ing:<14,.0f} {mar:.1f}%\n"
        else: 
            txt_rent += "(Sin registros de venta en facturas activas)"
        
        self.txt_rentabilidad.config(state="normal")
        self.txt_rentabilidad.delete("1.0", tk.END); self.txt_rentabilidad.insert("1.0", txt_rent)
        self.txt_rentabilidad.config(state="disabled")

        txt_mor = (
            f"===========================================================\n"
            f"                  ANÁLISIS DE RIESGO Y MORA                \n"
            f"===========================================================\n"
            f" Índice de Morosidad Real   : {idx_mora:.2f} %\n"
            f" Facturas Vencidas Detectadas: {m.get('facturas_vencidas_cuenta', 0)}\n"
            f" Capital en Riesgo Crítico  : ${m.get('total_vencido_monto', 0):,.2f} COP\n"
            f"===========================================================\n"
        )
        self.txt_morosidad.config(state="normal")
        self.txt_morosidad.delete("1.0", tk.END); self.txt_morosidad.insert("1.0", txt_mor)
        self.txt_morosidad.config(state="disabled")

        self.dibujar_grafico(datos_p) # type: ignore

    def dibujar_grafico(self, datos_p): # type: ignore
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            plt.close('all')
            
        if not datos_p:
            lbl_vacio = tk.Label(self.frame_graficos, text="Sin transacciones para procesar gráficos.", font=("Arial", 11, "italic"))
            lbl_vacio.pack(expand=True)
            return

        nombres = [d.get('nombre', 'Item')[:15] + '..' if len(d.get('nombre', '')) > 15 else d.get('nombre', 'Item') for d in datos_p] # type: ignore
        ingresos = [d.get('total_vendido', 0) or d.get('ingresos', 0) for d in datos_p] # type: ignore
        margenes = [d.get('margen_pct', 0) or d.get('margen', 0) for d in datos_p] # type: ignore

        fig, ax1 = plt.subplots(figsize=(6, 4.0), dpi=100) # type: ignore
        fig.patch.set_facecolor('#F3F4F6')
        ax1.set_facecolor('#FFFFFF')

        color_barras = '#3B82F6'
        ax1.bar(nombres, ingresos, color=color_barras, alpha=0.8, width=0.45, label="Ingresos ($)") # type: ignore
        ax1.set_ylabel("Ingresos de Caja ($)", color=color_barras, fontweight='bold') # type: ignore
        ax1.tick_params(axis='y', labelcolor=color_barras) # type: ignore
        ax1.set_xticklabels(nombres, rotation=20, ha='right', fontsize=8) # type: ignore
        ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x)))) # type: ignore

        ax2 = ax1.twinx()
        color_linea = '#10B981'
        ax2.plot(nombres, margenes, color=color_linea, marker='o', linewidth=2.2, label="Margen %") # type: ignore
        ax2.set_ylabel("Margen Neto de Ganancia (%)", color=color_linea, fontweight='bold') # type: ignore
        ax2.tick_params(axis='y', labelcolor=color_linea) # type: ignore
        ax2.set_ylim(0, 100)

        plt.title("Rendimiento Comercial: Ingresos vs Margen por Línea", fontsize=10, fontweight='bold', pad=12) # type: ignore
        fig.tight_layout()

        self.canvas_widget = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)

    def ejecutar_pandas_avanzado(self):
        try:
            metodo = getattr(_cartera, 'ejecutar_analisis_pandas', None) or getattr(_cartera, 'exportar_reportes_csv', None)
            if metodo:
                metodo()
                messagebox.showinfo("✅ Script Pandas Ejecutado", "El análisis avanzado finalizó con éxito.\nArchivos CSV exportados.")
            else:
                messagebox.showwarning("⚠️ Verificación", "Recuerda verificar que tu 'CarteraController' tenga el método de escritura de archivos CSV.")
        except Exception as e:
            messagebox.showerror("❌ Error en Script Pandas", f"No se pudo procesar el dataframe: {str(e)}")



# ── 7. VENTANA PRINCIPAL (CONTENEDOR DE PESTAÑAS RAÍZ) ──────────────────────
class AppEmpresarial(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema ERP Corporativo v3.0 - Módulo de Cartera Financiera")
        self.geometry("1080x640")
        
        # Configuración de estilos globales
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Panel superior decorativo corporativo
        self.banner = tk.Frame(self, bg="#1E3A8A", height=50)
        self.banner.pack(fill="x", side="top")
        self.lbl_titulo = tk.Label(self.banner, text="SISTEMA CENTRAL DE OPERACIONES COMERCIALES", font=("Arial", 12, "bold"), fg="#FFFFFF", bg="#1E3A8A")
        self.lbl_titulo.pack(side="left", padx=15, pady=12)
        
        # Notebook de Módulos Principales
        self.notebook_principal = ttk.Notebook(self)
        self.notebook_principal.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Inicialización de Vistas Modulares
        self.vista_clientes = VistaClientes(self.notebook_principal)
        self.vista_productos = VistaProductos(self.notebook_principal)
        self.vista_facturas = VistaFacturas(self.notebook_principal)
        self.vista_reportes = VistaReportes(self.notebook_principal)
        
        # Registro de pestañas en el panel raíz
        self.notebook_principal.add(self.vista_clientes, text=" 👥 Módulo Clientes ")
        self.notebook_principal.add(self.vista_productos, text=" 📦 Catálogo Productos ")
        self.notebook_principal.add(self.vista_facturas, text=" 📝 Facturación & Ventas ")
        self.notebook_principal.add(self.vista_reportes, text=" 📈 Business Intelligence ")
        
        # Barra de estado inferior (Corregido a ttk para evitar errores de padding)
        self.status = ttk.Label(self, text=f"Base de Datos Conectada: {RUTA_JSON} | Modo: Producción", relief="sunken", anchor="w", padding=4)
        self.status.pack(side="bottom", fill="x")


# ── 8. ARRANQUE DE LA APLICACIÓN ───────────────────────────────────────────
if __name__ == "__main__":
    app = AppEmpresarial()
    app.mainloop()