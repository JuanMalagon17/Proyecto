# 🚀 Guía de Revisión General: Actividades 7 y 8

Estimado Profesor,

Para facilitar el proceso de revisión y asegurar la verificación de los criterios de evaluación, hemos consolidado este mapa de navegación directo hacia los componentes de nuestro **Sistema de Gestión de Clientes, Ventas y Control de Cartera Financiera**.

El proyecto representa la integración total de los componentes de negocio desarrollados por el equipo mediante ramas Git independientes sincronizadas en `main`.

---

## 📂 Actividad 7: Arquitectura y Desarrollo de los CRUDs de las Entidades
El núcleo del sistema está compuesto por **3 entidades principales**, cada una con su respectiva lógica de encapsulamiento, contratos de interfaz y persistencia física de datos.

### 1. Componente: Módulo de Productos (Gestión de Catálogos)
* **Entidad:** `Producto` (Manejo de inventario, costos y dimensiones de carpintería).
* **Desarrollador:** Caren Rossana Peña Castañeda (Rama `dev_cpena86`)
* **Enlaces directos:**
  * [**Modelo de la Entidad (`producto.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/models/producto.py) — Lógica de stock y costeo base.
  * [**Implementación CRUD / DAO (`producto_dao.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/dao/producto_dao.py) — Persistencia y consultas del catálogo.

### 2. Componente: Módulo de Clientes (Riesgo y Control Comercial)
* **Entidad:** `Cliente` (Registro de compradores, estados de cuenta y asignación de cupos).
* **Desarrollador:** Juan Pablo Malagón Sáenz (Rama `dev_jmalagon72`)
* **Enlaces directos:**
  * [**Modelo de la Entidad (`cliente.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/models/cliente.py) — Atributos privados y control de perfil crediticio.
  * [**Implementación CRUD / DAO (`cliente_dao.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/dao/cliente_dao.py) — Persistencia del maestro de clientes.

### 3. Componente: Módulo de Facturación (Control de Cuentas por Cobrar)
* **Entidad:** `Factura` / `LineaFactura` (Orquestación de la venta, plazos de vencimiento y saldos).
* **Desarrollador:** Sebastian Gutierrez Guayacundo (Rama `dev_sgutierrez78`)
* **Enlaces directos:**
  * [**Modelo de la Entidad (`factura.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/models/factura.py) — Métodos de amortización, cálculo de IVA y estados transaccionales.
  * [**Implementación CRUD / DAO (`factura_dao.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/dao/factura_dao.py) — Gestión del histórico transaccional de cartera.

* *Nota: La abstracción y contratos unificados de las operaciones CRUD de todo el sistema se rigen bajo la interfaz base:* [**Contrato Universal (`interface_dao.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/dao/interface_dao.py).

---

## 🛠️ Actividad 8: Aplicación de Patrones de Diseño GoF (Ecosistema Conectado)
El sistema integra **7 patrones de diseño del catálogo GoF** distribuidos de manera complementaria en la arquitectura del proyecto para resolver acoplamientos y añadir extensibilidad.

### 1. Evidencia Teórica (Sustentación General)
* [**Matriz de los 23 Patrones GoF (`index.html`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/index.html) — Interfaz interactiva diseñada con la clasificación completa, ventajas, desventajas y casos de uso contextualizados en la gestión financiera de cartera.

### 2. Mapeo de Patrones Aplicados en el Código:
* **Creacional (Factory Method):** [Ver `DaoFactory` e `InMemoryDaoFactory`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/factory/dao_factory.py) — Aísla la inicialización de los DAOs para conmutar dinámicamente entre persistencia real o de pruebas en memoria. *(Caren Peña)*.
* **Creacional (Builder):** [Ver `FacturaBuilder`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/builders/factura_builder.py) — Construye de forma fluida el agregado complejo `Factura` inyectando líneas de productos y verificando existencias de stock antes de instanciar. *(Sebastian Gutierrez)*.
* **Creacional (Singleton):** [Ver `ConfiguracionApp`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/config/config.py) — Acceso único y centralizado de lectura thread-safe para parámetros de riesgo de la aplicación. *(Juan Pablo Malagón)*.
* **Estructural (Decorator):** [Ver `ValidarLimiteCreditoDecorator`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/decorators/credit_decorator.py) — Envuelve el CRUD de facturas para interceptar el guardado y validar las reglas de negocio sobre el límite de crédito del cliente sin modificar el DAO original. *(Juan Pablo Malagón)*.
* **Estructural & Comportamiento (Facade & Command):** [Ver `GestionCarteraFacade` y `ComandoPagarFactura`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/facade/facade.py) — Punto de entrada único que unifica la interacción cruzada entre los 3 módulos, encapsulando las acciones transaccionales en comandos independientes con soporte operacional. *(Integración del Equipo)*.

---

## 🧪 Validación Automatizada: Pruebas Unitarias (`unittest`)
Para asegurar la estabilidad técnica de las tres entidades CRUD y el correcto funcionamiento de los patrones de diseño, implementamos una suite robusta con **14 pruebas unitarias**.

* [**Suite de Pruebas Automatizadas (`test_patterns.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/tests/test_patterns.py)

### Instrucciones de Ejecución:
Para ejecutar el banco de pruebas completo y validar las aserciones, corra el siguiente comando en la consola:
```bash
python -m unittest tests.test_patterns -v

Integrantes del Equipo:

Sebastian Gutierrez Guayacundo (Módulo Facturación — Rama dev_sgutierrez78)

Juan Pablo Malagón Sáenz (Módulo Clientes — Rama dev_jmalagon72)

Caren Rossana Peña Castañeda (Módulo Productos — Rama dev_cpena86)

