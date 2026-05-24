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
from datetime import date
from typing import List, Optional

from src.dao.interface_dao import IDao
from src.models.cliente import Cliente
from src.models.factura import EstadoFactura, Factura, LineaFactura
from src.models.producto import Producto


class FacturaController:
    """
    Controlador MVC para el ciclo de vida de la Factura.

    Necesita los tres DAOs porque una operación de factura
    tiene efectos secundarios sobre cliente (saldo) y producto (stock).
    """

    def __init__(
        self,
        factura_dao: IDao[Factura],
        cliente_dao: IDao[Cliente],
        producto_dao: IDao[Producto],
    ) -> None:
        self._factura_dao  = factura_dao
        self._cliente_dao  = cliente_dao
        self._producto_dao = producto_dao

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
    def crear_factura(
        self,
        id_factura: str,
        id_cliente: str,
        fecha_vencimiento: str,
        notas: str = "",
    ) -> Factura:
        """
        Crea una factura vacía vinculada a un cliente existente.
        Las líneas de detalle se agregan después con agregar_linea_a_factura().

        Raises:
            ValueError: Si el cliente no existe.
        """
        cliente = self._cliente_dao.buscar_por_id(id_cliente)
        if cliente is None:
            raise ValueError(f"No existe cliente con id '{id_cliente}'.")
        factura = Factura(
            id_factura=id_factura,
            id_cliente=id_cliente,
            nombre_cliente=cliente.nombre,
            fecha_emision=date.today().isoformat(),
            fecha_vencimiento=fecha_vencimiento,
            notas=notas,
        )
        return self._factura_dao.guardar(factura)

    def agregar_linea_a_factura(
        self,
        id_factura: str,
        id_producto: str,
        cantidad: int,
    ) -> Factura:
        """
        Agrega un producto a la factura, descuenta el stock
        y actualiza el saldo pendiente del cliente.

        Raises:
            ValueError: Si la factura o el producto no existen,
                        o si no hay stock suficiente.
        """
        factura = self._factura_dao.buscar_por_id(id_factura)
        if factura is None:
            raise ValueError(f"No existe factura '{id_factura}'.")

        producto = self._producto_dao.buscar_por_id(id_producto)
        if producto is None:
            raise ValueError(f"No existe producto '{id_producto}'.")

        linea = LineaFactura(
            id_producto=id_producto,
            nombre_producto=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio_unitario,
            costo_unitario=producto.costo_unitario,
        )
        factura.agregar_linea(linea)

        producto.reducir_stock(cantidad)
        self._producto_dao.actualizar(producto)

        cliente = self._cliente_dao.buscar_por_id(factura.id_cliente)
        if cliente:
            cliente.agregar_saldo(linea.subtotal)
            self._cliente_dao.actualizar(cliente)

        self._factura_dao.actualizar(factura)
        return factura

    # ------------------------------------------------------------------ #
    # READ
    # ------------------------------------------------------------------ #
    def obtener_factura(self, id_factura: str) -> Optional[Factura]:
        """Retorna la factura con ese id, o None si no existe."""
        return self._factura_dao.buscar_por_id(id_factura)

    def listar_facturas(self) -> List[Factura]:
        """Retorna todas las facturas del sistema."""
        return self._factura_dao.listar_todos()

    def listar_facturas_por_cliente(self, id_cliente: str) -> List[Factura]:
        """Retorna todas las facturas de un cliente específico."""
        return [
            f for f in self._factura_dao.listar_todos()
            if f.id_cliente == id_cliente
        ]

    def listar_pendientes(self) -> List[Factura]:
        """Retorna solo las facturas en estado PENDIENTE."""
        return [
            f for f in self._factura_dao.listar_todos()
            if f.estado == EstadoFactura.PENDIENTE
        ]

    # ------------------------------------------------------------------ #
    # UPDATE — transiciones de estado
    # ------------------------------------------------------------------ #
    def pagar_factura(self, id_factura: str) -> Factura:
        """
        Registra el pago de una factura: cambia estado a PAGADA
        y reduce el saldo pendiente del cliente.

        Raises:
            ValueError: Si la factura no existe o no está PENDIENTE.
        """
        factura = self._factura_dao.buscar_por_id(id_factura)
        if factura is None:
            raise ValueError(f"No existe factura '{id_factura}'.")
        factura.marcar_pagada()
        self._factura_dao.actualizar(factura)

        cliente = self._cliente_dao.buscar_por_id(factura.id_cliente)
        if cliente:
            cliente.reducir_saldo(factura.total)
            self._cliente_dao.actualizar(cliente)

        return factura

    def anular_factura(self, id_factura: str) -> Factura:
        """
        Anula una factura. Si estaba PENDIENTE, revierte el saldo del cliente.

        Raises:
            ValueError: Si la factura no existe o ya está ANULADA.
        """
        factura = self._factura_dao.buscar_por_id(id_factura)
        if factura is None:
            raise ValueError(f"No existe factura '{id_factura}'.")
        era_pendiente = factura.estado == EstadoFactura.PENDIENTE
        factura.anular()
        self._factura_dao.actualizar(factura)

        if era_pendiente:
            cliente = self._cliente_dao.buscar_por_id(factura.id_cliente)
            if cliente:
                cliente.reducir_saldo(factura.total)
                self._cliente_dao.actualizar(cliente)

        return factura

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #
    def eliminar_factura(self, id_factura: str) -> bool:
        """
        Elimina físicamente una factura del sistema.

        Returns:
            True si fue eliminada, False si no existía.
        """
        return self._factura_dao.eliminar(id_factura)
