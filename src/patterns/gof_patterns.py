"""
Patrones GoF aplicados al proyecto de Gestión de Cartera.
Actividad 8 — Lenguajes de Programación II

Patrones implementados:
  1. Builder        — FacturaBuilder
  2. Factory Method — DaoFactory / JsonDaoFactory / InMemoryDaoFactory
  3. Singleton      — ConfiguracionApp
  4. Decorator      — ValidarLimiteCreditoDecorator / LogAuditoriaDecorator
  5. Strategy       — EstrategiaReporte / ReporteTextoPlano / ReporteCSV / ReporteJSON
  6. Facade         — GestionCarteraFacade
  7. Command        — ComandoPagarFactura / ComandoAnularFactura / HistorialComandos
"""

import csv
import io
import json
import threading
from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List, Optional, TypeVar, Generic

from src.models.factura import Factura, LineaFactura, EstadoFactura
from src.models.producto import Producto
from src.models.cliente import Cliente
from src.dao.interface_dao import IDao
from src.dao.cliente_dao import ClienteDao
from src.dao.factura_dao import FacturaDao
from src.dao.producto_dao import ProductoDao
from src.controllers.cartera_controller import CarteraController
from src.controllers.cliente_controller import ClienteController
from src.controllers.factura_controller import FacturaController
from src.controllers.producto_controller import ProductoController

# ======================================================================
# 1. BUILDER
# ======================================================================
class FacturaBuilder:
    """Builder para construir Facturas complejas paso a paso."""

    def __init__(self) -> None:
        self._id_factura: str = ""
        self._id_cliente: str = ""
        self._nombre_cliente: str = ""
        self._fecha_emision: str = ""
        self._fecha_vencimiento: str = ""
        self._lineas: List[LineaFactura] = []
        self._notas: str = ""
        self._reset()

    def _reset(self) -> None:
        self._id_factura = ""
        self._id_cliente = ""
        self._nombre_cliente = ""
        self._fecha_emision = date.today().isoformat()
        self._fecha_vencimiento = ""
        self._lineas = []
        self._notas = ""

    def set_identificador(self, id_factura: str) -> "FacturaBuilder":
        self._id_factura = id_factura
        return self

    def set_cliente(self, id_cliente: str, nombre_cliente: str) -> "FacturaBuilder":
        self._id_cliente = id_cliente
        self._nombre_cliente = nombre_cliente
        return self

    def set_vencimiento(self, fecha: str) -> "FacturaBuilder":
        self._fecha_vencimiento = fecha
        return self

    def agregar_linea(self, producto: Producto, cantidad: int) -> "FacturaBuilder":
        if not producto.hay_stock_suficiente(cantidad):
            raise ValueError(f"Stock insuficiente para '{producto.nombre}'.")
        
        linea = LineaFactura(
            id_producto=producto.id_producto,
            nombre_producto=producto.nombre,
            cantidad=cantidad,
            precio_unitario=producto.precio_unitario,
            costo_unitario=producto.costo_unitario,
        )
        self._lineas.append(linea)
        return self

    def set_notas(self, notas: str) -> "FacturaBuilder":
        self._notas = notas
        return self

    def build(self) -> Factura:
        if not self._id_factura:
            raise ValueError("El id de factura es obligatorio.")
        if not self._fecha_vencimiento:
            raise ValueError("La fecha de vencimiento es obligatoria.")
        
        # Satisface exactamente los argumentos requeridos por tu modelo original
        factura = Factura(
            id_factura=self._id_factura,
            id_cliente=self._id_cliente,
            nombre_cliente=self._nombre_cliente,
            fecha_emision=self._fecha_emision,
            fecha_vencimiento=self._fecha_vencimiento,
            lineas=[],
            estado=EstadoFactura.PENDIENTE,
            notas=self._notas
        )
        
        for linea in self._lineas:
            factura.agregar_linea(linea)
            
        self._reset()
        return factura


# ======================================================================
# 2. FACTORY METHOD
# ======================================================================
class DaoFactory(ABC):
    """Fábrica abstracta de DAOs — Factory Method con tipado estricto."""

    @abstractmethod
    def crear_cliente_dao(self) -> IDao[Cliente]: ...

    @abstractmethod
    def crear_factura_dao(self) -> IDao[Factura]: ...

    @abstractmethod
    def crear_producto_dao(self) -> IDao[Producto]: ...


class JsonDaoFactory(DaoFactory):
    """Fábrica concreta: DAOs JSON para producción."""

    def __init__(self, ruta_json: str) -> None:
        self._ruta = ruta_json

    def crear_cliente_dao(self) -> IDao[Cliente]:
        return ClienteDao(self._ruta)

    def crear_factura_dao(self) -> IDao[Factura]:
        return FacturaDao(self._ruta)

    def crear_producto_dao(self) -> IDao[Producto]:
        return ProductoDao(self._ruta)


T = TypeVar("T")

class _InMemoryDao(IDao[T], Generic[T]):
    """DAO genérico en memoria para pruebas unitarias."""

    def __init__(self) -> None:
        self._store: Dict[str, T] = {}

    def _get_id(self, entidad: Any) -> str:
        return str(list(vars(entidad).values())[0]) # type: ignore

    def guardar(self, e: T) -> T: # type: ignore
        key = self._get_id(e)
        self._store[key] = e
        return e

    def buscar_por_id(self, id_: str) -> Optional[T]: # type: ignore
        return self._store.get(id_)

    def listar_todos(self) -> List[T]:
        return list(self._store.values())

    def actualizar(self, e: T) -> T: # type: ignore
        key = self._get_id(e)
        self._store[key] = e
        return e

    def eliminar(self, id_: str) -> bool: # type: ignore
        return self._store.pop(id_, None) is not None


class InMemoryDaoFactory(DaoFactory):
    """Fábrica concreta: DAOs en memoria para pruebas unitarias."""

    def crear_cliente_dao(self) -> IDao[Cliente]:
        return _InMemoryDao[Cliente]()

    def crear_factura_dao(self) -> IDao[Factura]:
        return _InMemoryDao[Factura]()

    def crear_producto_dao(self) -> IDao[Producto]:
        return _InMemoryDao[Producto]()


# ======================================================================
# 3. SINGLETON
# ======================================================================
class ConfiguracionApp:
    """Singleton thread-safe para configuración global de la aplicación."""

    _instancia: Optional["ConfiguracionApp"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "ConfiguracionApp":
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
                    cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self) -> None:
        self._config: Dict[str, Any] = {
            "ruta_json": "data/facturas.json",
            "moneda": "COP",
            "umbral_roa_alerta": 15.0,
            "dias_vencimiento_alerta": 7,
            "max_lineas_factura": 50,
            "version_app": "1.0.0",
        }

    def obtener(self, clave: str, por_defecto: Any = None) -> Any:
        return self._config.get(clave, por_defecto)

    def establecer(self, clave: str, valor: Any) -> None:
        self._config[clave] = valor


# ======================================================================
# 4. DECORATOR
# ======================================================================
class FacturaDaoDecorator(IDao[Factura]):
    """Decorador base que delega al DAO real sin perder los tipos."""

    def __init__(self, dao_real: IDao[Factura]) -> None:
        self._dao = dao_real

    def guardar(self, f: Factura) -> Factura: # type: ignore
        return self._dao.guardar(f)

    def buscar_por_id(self, id_: str) -> Optional[Factura]: # type: ignore
        return self._dao.buscar_por_id(id_)

    def listar_todos(self) -> List[Factura]:
        return self._dao.listar_todos()

    def actualizar(self, f: Factura) -> Factura: # type: ignore
        return self._dao.actualizar(f)

    def eliminar(self, id_: str) -> bool: # type: ignore
        return self._dao.eliminar(id_)


class ValidarLimiteCreditoDecorator(FacturaDaoDecorator):
    """Decorador: valida límite de crédito antes de persistir la factura."""

    def __init__(self, dao_real: IDao[Factura], limite_credito: float) -> None:
        super().__init__(dao_real)
        self._limite = limite_credito

    def guardar(self, factura: Factura) -> Factura: # type: ignore
        if factura.total > self._limite:
            raise ValueError(
                f"Factura supera el límite de crédito de ${self._limite:,.2f}. "
                f"Total: ${factura.total:,.2f}"
            )
        return super().guardar(factura)


class LogAuditoriaDecorator(FacturaDaoDecorator):
    """Decorador: registra auditoría por terminal de cada operación de escritura."""

    def guardar(self, factura: Factura) -> Factura: # type: ignore
        print(f"[AUDIT] CREAR Factura {factura.id_factura} | Total: ${factura.total:,.0f}")
        resultado = super().guardar(factura)
        print(f"[AUDIT] OK — Factura {factura.id_factura} guardada.")
        return resultado

    def eliminar(self, id_: str) -> bool:
        print(f"[AUDIT] ELIMINAR Factura {id_}")
        return super().eliminar(id_)


# ======================================================================
# 5. STRATEGY
# ======================================================================
class EstrategiaReporte(ABC):
    """Interfaz Strategy para generación de reportes financieros."""

    @abstractmethod
    def generar(self, datos: List[Dict[str, Any]], titulo: str) -> str: ...


class ReporteTextoPlano(EstrategiaReporte):
    def generar(self, datos: List[Dict[str, Any]], titulo: str) -> str:
        lineas = [f"\n{'='*60}", f"  {titulo}", f"{'='*60}"]
        for fila in datos:
            lineas.append("  " + " | ".join(f"{k}: {v}" for k, v in fila.items()))
        lineas.append(f"{'='*60}\n")
        return "\n".join(lineas)


class ReporteCSV(EstrategiaReporte):
    def generar(self, datos: List[Dict[str, Any]], titulo: str) -> str:
        if not datos:
            return ""
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(datos[0].keys()))
        writer.writeheader()
        writer.writerows(datos)
        return buffer.getvalue()


class ReporteJSON(EstrategiaReporte):
    def generar(self, datos: List[Dict[str, Any]], titulo: str) -> str:
        return json.dumps({"titulo": titulo, "datos": datos}, ensure_ascii=False, indent=2)


class GeneradorReporteCartera:
    """Contexto Strategy: genera reportes usando la estrategia inyectada."""

    def __init__(self, estrategia: EstrategiaReporte) -> None:
        self._estrategia = estrategia

    def cambiar_estrategia(self, estrategia: EstrategiaReporte) -> None:
        self._estrategia = estrategia

    def generar_reporte_rentabilidad(self, datos_productos: List[Dict[str, Any]]) -> str:
        return self._estrategia.generar(datos_productos, "Rentabilidad por Producto")


# ======================================================================
# 6. FACADE
# ======================================================================
class GestionCarteraFacade:
    """Facade unificada para el sistema de gestión de cartera."""

    def __init__(self, factory_dao: Optional[DaoFactory] = None) -> None:
        cfg = ConfiguracionApp()
        ruta = str(cfg.obtener("ruta_json"))
        
        self._factory = factory_dao or JsonDaoFactory(ruta)
        
        self._fd = self._factory.crear_factura_dao()
        self._cd = self._factory.crear_cliente_dao()
        self._pd = self._factory.crear_producto_dao()
        
        # Inyección respetando exactamente los constructores de la Actividad 7
        self._facturas = FacturaController(self._fd, self._cd, self._pd)
        self._clientes = ClienteController(self._cd, self._fd)
        self._productos = ProductoController(self._pd)
        self._cartera = CarteraController(self._fd)
        self._reportes = GeneradorReporteCartera(ReporteTextoPlano())

    def registrar_venta(self, id_factura: str, id_cliente: str, id_producto: str, cantidad: int, fecha_vencimiento: str) -> Factura:
        self._facturas.crear_factura(id_factura, id_cliente, fecha_vencimiento)
        return self._facturas.agregar_linea_a_factura(id_factura, id_producto, cantidad)

    def cobrar_factura(self, id_factura: str) -> Factura:
        return self._facturas.pagar_factura(id_factura)

    def dashboard_financiero(self, formato: str = "texto") -> str:
        estrategia = {"json": ReporteJSON(), "csv": ReporteCSV()}.get(formato, ReporteTextoPlano()) # type: ignore
        self._reportes.cambiar_estrategia(estrategia) # type: ignore
        return self._reportes.generar_reporte_rentabilidad(self._cartera.rentabilidad_por_producto())


# ======================================================================
# 7. COMMAND
# ======================================================================
class ComandoFactura(ABC):
    """Interfaz Command para operaciones reversibles sobre facturas."""

    @abstractmethod
    def ejecutar(self) -> Factura: ...

    @abstractmethod
    def deshacer(self) -> None: ...

    @property
    @abstractmethod
    def descripcion(self) -> str: ...


class ComandoPagarFactura(ComandoFactura):
    """Command: Registra el pago de una factura de forma reversible."""

    def __init__(self, controller: FacturaController, id_factura: str) -> None:
        self._ctrl = controller
        self._id = id_factura
        self._factura_modificada: Optional[Factura] = None

    def ejecutar(self) -> Factura:
        self._factura_modificada = self._ctrl.pagar_factura(self._id)
        return self._factura_modificada

    def deshacer(self) -> None:
        if self._factura_modificada:
            self._factura_modificada.estado = EstadoFactura.PENDIENTE
            self._ctrl._factura_dao.actualizar(self._factura_modificada) # type: ignore

    @property
    def descripcion(self) -> str:
        return f"Pagar factura {self._id}"


class ComandoAnularFactura(ComandoFactura):
    """Command: Anula una factura."""

    def __init__(self, controller: FacturaController, id_factura: str) -> None:
        self._ctrl = controller
        self._id = id_factura
        self._factura_modificada: Optional[Factura] = None

    def ejecutar(self) -> Factura:
        self._factura_modificada = self._ctrl.anular_factura(self._id)
        return self._factura_modificada

    def deshacer(self) -> None:
        if self._factura_modificada:
            self._factura_modificada.estado = EstadoFactura.PENDIENTE
            self._ctrl._factura_dao.actualizar(self._factura_modificada) # type: ignore

    @property
    def descripcion(self) -> str:
        return f"Anular factura {self._id}"


class HistorialComandos:
    """Invoker: Registra comandos para ejecuciones transaccionales."""

    def __init__(self) -> None:
        self._historial: List[ComandoFactura] = []

    def ejecutar(self, comando: ComandoFactura) -> Factura:
        resultado = comando.ejecutar()
        self._historial.append(comando)
        return resultado

    def deshacer_ultimo(self) -> None:
        if not self._historial:
            return
        ultimo = self._historial.pop()
        ultimo.deshacer()

    def ver_historial(self) -> List[str]:
        return [c.descripcion for c in self._historial]