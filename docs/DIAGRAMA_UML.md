```mermaid
classDiagram
  class IDao {
    <<interface>>
    +guardar(entidad: T) T
    +buscar_por_id(id: str) T
    +listar_todos() list
    +actualizar(entidad: T) T
    +eliminar(id: str) bool
  }

  class ClienteDao {
    -_ruta: str
    +guardar(cliente: Cliente) Cliente
    +buscar_por_id(id: str) Cliente
    +listar_todos() list
    +actualizar(cliente: Cliente) Cliente
    +eliminar(id: str) bool
    +buscar_por_nombre(nombre: str) Cliente
    +listar_activos() list
    +listar_con_saldo_pendiente() list
  }

  class ProductoDao {
    -_ruta: str
    +guardar(producto: Producto) Producto
    +buscar_por_id(id: str) Producto
    +listar_todos() list
    +actualizar(producto: Producto) Producto
    +eliminar(id: str) bool
    +listar_con_stock_disponible() list
  }

  class FacturaDao {
    -_ruta: str
    +guardar(factura: Factura) Factura
    +buscar_por_id(id: str) Factura
    +listar_todos() list
    +actualizar(factura: Factura) Factura
    +eliminar(id: str) bool
    +listar_por_cliente(id_cliente: str) list
    +listar_pendientes() list
  }

  IDao <|.. ClienteDao : implementa
  IDao <|.. ProductoDao : implementa
  IDao <|.. FacturaDao : implementa


  class Cliente {
    +id_cliente: str
    +nombre: str
    +email: str
    +telefono: str
    +direccion: str
    +activo: bool
    +saldo_pendiente: float
    +agregar_saldo(monto: float) void
    +reducir_saldo(monto: float) void
    +to_dict() dict
    +from_dict(data: dict) Cliente
  }

  class Producto {
    +id_producto: str
    +nombre: str
    +descripcion: str
    +precio_unitario: float
    +costo_unitario: float
    +stock: int
    +activo: bool
    +margen_bruto() float
    +margen_porcentual() float
    +hay_stock_suficiente(cantidad: int) bool
    +reducir_stock(cantidad: int) void
    +to_dict() dict
    +from_dict(data: dict) Producto
  }

  class EstadoFactura {
    <<enumeration>>
    PENDIENTE
    PAGADA
    VENCIDA
    ANULADA
  }

  class LineaFactura {
    +id_producto: str
    +nombre_producto: str
    +cantidad: int
    +precio_unitario: float
    +costo_unitario: float
    +subtotal() float
    +costo_total() float
    +utilidad_bruta() float
    +to_dict() dict
    +from_dict(data: dict) LineaFactura
  }

  class Factura {
    +id_factura: str
    +id_cliente: str
    +nombre_cliente: str
    +fecha_emision: str
    +fecha_vencimiento: str
    +lineas: list
    +estado: EstadoFactura
    +notas: str
    +total() float
    +utilidad_bruta() float
    +margen_bruto_porcentual() float
    +esta_vencida() bool
    +agregar_linea(linea: LineaFactura) void
    +marcar_pagada() void
    +anular() void
    +to_dict() dict
    +from_dict(data: dict) Factura
  }

  Factura "1" *-- "*" LineaFactura : contiene
  Factura --> EstadoFactura : usa


  class ClienteController {
    -_cliente_dao: IDao
    -_factura_dao: IDao
    +crear_cliente(id, nombre, email, tel, dir) Cliente
    +obtener_cliente(id: str) Cliente
    +listar_clientes() list
    +listar_clientes_activos() list
    +listar_con_saldo_pendiente() list
    +actualizar_cliente(cliente: Cliente) Cliente
    +activar_cliente(id: str) Cliente
    +desactivar_cliente(id: str) Cliente
    +eliminar_cliente(id: str) bool
  }

  class ProductoController {
    -_dao: IDao
    +crear_producto(id, nombre, desc, precio, costo, stock) Producto
    +obtener_producto(id: str) Producto
    +listar_productos() list
    +listar_disponibles() list
    +listar_sin_stock() list
    +actualizar_producto(producto: Producto) Producto
    +ajustar_stock(id: str, cantidad: int) Producto
    +actualizar_precio(id, precio, costo) Producto
    +activar_producto(id: str) Producto
    +desactivar_producto(id: str) Producto
    +eliminar_producto(id: str) bool
  }

  class FacturaController {
    -_factura_dao: IDao
    -_cliente_dao: IDao
    -_producto_dao: IDao
    +crear_factura(id, id_cliente, vencimiento, notas) Factura
    +agregar_linea_a_factura(id_fac, id_prod, cant) Factura
    +obtener_factura(id: str) Factura
    +listar_facturas() list
    +listar_facturas_por_cliente(id: str) list
    +listar_pendientes() list
    +pagar_factura(id: str) Factura
    +anular_factura(id: str) Factura
    +eliminar_factura(id: str) bool
  }

  class CarteraController {
    -_factura_dao: IDao
    +calcular_resumen_cartera() dict
    +top_clientes_por_ventas(n: int) void
    +rentabilidad_por_producto() dict
    +calcular_indice_morosidad() dict
  }

  %% Relaciones de dependencia correctas (DIP)
  ClienteController  --> IDao : usa
  ProductoController --> IDao : usa
  FacturaController  --> IDao : usa
  CarteraController  --> IDao : usa

  %% Operación sobre modelos
  ClienteController  ..> Cliente : gestiona
  ProductoController ..> Producto : gestiona
  FacturaController  ..> Factura : transacciona
  CarteraController  ..> Factura : analiza

  %% Persistencia de datos
  ClienteDao  ..> Cliente : mapea
  ProductoDao ..> Producto : mapea
  FacturaDao  ..> Factura : mapea
  ```