# 🎨 Actividad 8 — Patrones de Diseño GoF
## Sistema de Gestión Financiera de Cartera

> **Asignatura:** Lenguajes de Programación II  
> **Estudiante:** Sebastian Gutierrez Guayacundo  
> **Universidad:** Universidad de La Salle (UNISALLE)  
> **Fecha:** Mayo 2026

---

# 📚 Tabla de los 23 Patrones GoF

| # | Nombre Patrón | Tipo/Categoría | Problema que Resuelve | Diagrama de Clases (descripción) | Casos de Uso | Ventajas | Desventajas | Patrones Relacionados |
|---|---|---|---|---|---|---|---|---|
| 1 | **Abstract Factory** | Creacional | Crear familias de objetos relacionados sin especificar sus clases concretas | `AbstractFactory` → `ConcreteFactory1/2` → `ProductA/B` | UI multiplataforma, drivers de BD | Consistencia entre productos; aislamiento de código concreto | Difícil agregar nuevos tipos de producto | Factory Method, Prototype, Singleton |
| 2 | **Builder** | Creacional | Construir objetos complejos paso a paso separando construcción de representación | `Director` → `Builder` ← `ConcreteBuilder` → `Product` | Construcción de documentos, queries SQL, facturas | Reutilización del proceso de construcción | Requiere Builder separado | Factory Method, Abstract Factory |
| 3 | **Factory Method** | Creacional | Delegar a subclases la decisión de qué clase instanciar | `Creator.factoryMethod()` ← `ConcreteCreator` → `ConcreteProduct` | Frameworks de logging, generación de DAOs | Desacoplamiento entre creador y producto | Más subclases | Abstract Factory, Template Method |
| 4 | **Prototype** | Creacional | Clonar objetos existentes sin depender de clases concretas | `Prototype.clone()` ← `ConcretePrototype` | Plantillas y configuraciones | Reduce costo de creación | Complejidad con referencias circulares | Abstract Factory, Composite |
| 5 | **Singleton** | Creacional | Garantizar una única instancia global | `Singleton` con `_instance` y `getInstance()` | Configuración global, loggers | Control centralizado | Dificulta testing | Facade, Builder |
| 6 | **Adapter** | Estructural | Compatibilizar interfaces incompatibles | `Target` ← `Adapter` → `Adaptee` | Integración de librerías externas | Reutilización | Mayor complejidad | Proxy, Bridge |
| 7 | **Bridge** | Estructural | Separar abstracción e implementación | `Abstraction` → `Implementor` | Sistemas multicanal | Flexibilidad | Más clases | Adapter |
| 8 | **Composite** | Estructural | Tratar objetos individuales y grupos uniformemente | `Component` ← `Composite` | Árboles de menús | Simplifica clientes | Restricciones difíciles | Visitor |
| 9 | **Decorator** | Estructural | Agregar comportamiento dinámicamente | `Decorator` → `Component` | Validaciones, middlewares | Flexible | Muchos objetos | Strategy |
| 10 | **Facade** | Estructural | Simplificar acceso a subsistemas complejos | `Facade` → múltiples clases | APIs simplificadas | Reduce acoplamiento | Riesgo de “objeto dios” | Mediator |
| 11 | **Flyweight** | Estructural | Compartir estado para ahorrar memoria | `FlyweightFactory` → `Flyweight` | Renderizado masivo | Menor consumo RAM | Separación compleja | Singleton |
| 12 | **Proxy** | Estructural | Controlar acceso a objetos | `Proxy` → `RealSubject` | Caché, seguridad | Control y seguridad | Latencia adicional | Decorator |
| 13 | **Chain of Responsibility** | Comportamiento | Procesar solicitudes en cadena | `Handler` → `ConcreteHandler` | Pipelines y validaciones | Bajo acoplamiento | No garantiza manejo | Observer |
| 14 | **Command** | Comportamiento | Encapsular solicitudes como objetos | `Invoker` → `Command.execute()` | Undo/redo, transacciones | Historial y reversión | Muchas clases | Memento |
| 15 | **Interpreter** | Comportamiento | Interpretar gramáticas | `Expression` ← `TerminalExpression` | Lenguajes simples | Flexible | Ineficiente en gramáticas complejas | Composite |
| 16 | **Iterator** | Comportamiento | Recorrer colecciones sin exponer estructura | `Iterator` ← `ConcreteIterator` | Reportes, listas | Interfaz uniforme | Overhead innecesario | Visitor |
| 17 | **Mediator** | Comportamiento | Centralizar comunicación | `Mediator` ↔ `Colleague` | Chats, formularios | Reduce dependencias | Mediador complejo | Facade |
| 18 | **Memento** | Comportamiento | Capturar/restaurar estados | `Originator` → `Memento` | Undo en editores | Encapsulación segura | Alto uso de memoria | Command |
| 19 | **Observer** | Comportamiento | Notificar cambios automáticamente | `Subject.subscribe()` → `Observer` | Eventos UI | Extensible | Orden impredecible | Mediator |
| 20 | **State** | Comportamiento | Cambiar comportamiento según estado | `Context` → `State` | Facturas PENDIENTE/PAGADA | Elimina condicionales | Muchas clases | Strategy |
| 21 | **Strategy** | Comportamiento | Intercambiar algoritmos dinámicamente | `Context` → `Strategy.execute()` | Reportes y cálculos | Extensible | Cliente debe conocer estrategias | Template Method |
| 22 | **Template Method** | Comportamiento | Definir esqueleto de algoritmo | `AbstractClass.templateMethod()` | Frameworks ETL | Reutilización | Herencia rígida | Strategy |
| 23 | **Visitor** | Comportamiento | Separar algoritmos de estructuras | `Visitor.visit()` ← `Element.accept()` | ASTs y auditorías | Nuevas operaciones fáciles | Difícil agregar elementos | Composite |

---

# 🧩 Práctica: 7 Patrones GoF Aplicados al Proyecto

Los siguientes patrones están implementados en:

- `src/patterns/`
- `src/controllers/`

---

# 1️⃣ Builder — `FacturaBuilder`

## Problema

Construir una `Factura` con múltiples líneas, validaciones y notas requiere demasiados parámetros y lógica repetitiva.

## Solución

`FacturaBuilder` encapsula la construcción paso a paso de la factura.

```python
# src/patterns/gof_patterns.py

from src.models.factura import Factura, LineaFactura
from src.models.producto import Producto
from datetime import date


class FacturaBuilder:

    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._id_factura: str = ""
        self._id_cliente: str = ""
        self._nombre_cliente: str = ""
        self._fecha_emision: str = date.today().isoformat()
        self._fecha_vencimiento: str = ""
        self._lineas: list = []
        self._notas: str = ""

    def set_identificador(self, id_factura: str):
        self._id_factura = id_factura
        return self

    def set_cliente(self, id_cliente: str, nombre: str):
        self._id_cliente = id_cliente
        self._nombre_cliente = nombre
        return self

    def agregar_linea(self, producto: Producto, cantidad: int):
        if not producto.hay_stock_suficiente(cantidad):
            raise ValueError("Stock insuficiente")
```

---

# 2️⃣ Factory Method — `DaoFactory`

## Problema

El sistema necesita cambiar dinámicamente entre DAOs JSON o DAOs en memoria para pruebas.

## Solución

`DaoFactory` desacopla la creación de implementaciones concretas.

```python
from abc import ABC, abstractmethod

class DaoFactory(ABC):

    @abstractmethod
    def crear_cliente_dao(self):
        pass


class JsonDaoFactory(DaoFactory):

    def crear_cliente_dao(self):
        return ClienteDao(self._ruta)
```

---

# 3️⃣ Singleton — `ConfiguracionApp`

## Problema

La configuración global no debe duplicarse ni desincronizarse.

## Solución

Singleton thread-safe usando Double-Checked Locking.

```python
import threading

class ConfiguracionApp:

    _instancia = None
    _lock = threading.Lock()

    def __new__(cls):

        if cls._instancia is None:
            with cls._lock:

                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)

        return cls._instancia
```

---

# 4️⃣ Decorator — `ValidarLimiteCreditoDecorator`

## Problema

Agregar validaciones comerciales sin modificar directamente el DAO original.

## Solución

Usar un decorador estructural para interceptar operaciones.

```python
class FacturaDaoDecorator(IDao[Factura]):

    def __init__(self, dao_real):
        self._dao = dao_real

    def guardar(self, factura):
        return self._dao.guardar(factura)
```

---

# 5️⃣ Strategy — `EstrategiaReporte`

## Problema

Exportar reportes financieros en múltiples formatos sin romper OCP.

## Solución

Encapsular algoritmos de exportación bajo una interfaz común.

```python
from abc import ABC, abstractmethod

class EstrategiaReporte(ABC):

    @abstractmethod
    def generar(self, datos, titulo):
        pass


class ReporteCSV(EstrategiaReporte):

    def generar(self, datos, titulo):
        return "csv_generado"
```

---

# 6️⃣ Facade — `GestionCarteraFacade`

## Problema

`main.py` interactúa con demasiados controladores independientes.

## Solución

Crear una fachada unificada del sistema financiero.

```python
class GestionCarteraFacade:

    def __init__(self, factory_dao):

        self._facturas = FacturaController(...)
        self._clientes = ClienteController(...)
        self._productos = ProductoController(...)
```

---

# 7️⃣ Command — `ComandoPagarFactura`

## Problema

Registrar operaciones ejecutadas y permitir reversión de pagos.

## Solución

Convertir acciones de negocio en objetos ejecutables.

```python
from abc import ABC, abstractmethod

class ComandoFactura(ABC):

    @abstractmethod
    def ejecutar(self):
        pass


class ComandoPagarFactura(ComandoFactura):

    def ejecutar(self):
        return self._ctrl.pagar_factura(self._id)
```

---

# 🧪 Verificación de Pruebas Automatizadas

Se implementó una batería de 14 pruebas unitarias utilizando `unittest`.

## Ejecución

```bash
python -m unittest tests.test_patterns -v
```

---

# ✅ Resultado Exitoso

```plaintext
Ran 14 tests in 0.049s

OK
```

## Casos Verificados

| Código | Validación |
|---|---|
| B-1 | Builder genera facturas correctamente |
| B-2 | Builder valida campos obligatorios |
| CMD-1 | Command cambia estado de factura |
| CMD-2 | Historial registra operaciones |
| D-1 | Decorator bloquea límite excedido |
| D-2 | Decorator permite operaciones válidas |
| FA-1 | Facade registra ventas |
| FA-2 | Dashboard financiero funciona |
| FM-1 | Factory Method crea DAOs correctos |
| FM-2 | Factory in-memory persiste datos |
| S-1 | Singleton mantiene misma instancia |
| S-2 | Configuración persiste entre accesos |
| ST-1 | Strategy CSV genera encabezados |
| ST-2 | Strategy JSON genera salida válida |

---

# 🏁 Conclusión

La implementación de patrones GoF permitió:

- Mejorar el desacoplamiento del sistema
- Facilitar pruebas unitarias
- Incrementar extensibilidad y mantenibilidad
- Preparar la arquitectura para futuras integraciones con Machine Learning y analítica avanzada

---

*Documento estructurado y verificado para la Facultad de Ingeniería — Universidad de La Salle*