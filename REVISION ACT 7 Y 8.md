# 🚀 Guía de Revisión: Actividades 7 y 8

Estimado Profesor, 

Para facilitar el proceso de revisión y asegurar la verificación de los criterios de evaluación, hemos consolidado este mapa de navegación directo hacia los componentes desarrollados para la **Actividad 7 (CRUD de una Entidad)** y la **Actividad 8 (Estructura Teórica y Práctica de Patrones GoF)**.

El proyecto fue desarrollado de manera modular por componentes de negocio utilizando ramas independientes integradas en la rama principal.

---

## 📂 Actividad 7: Desarrollo de CRUD (Módulo de Facturación)
* **Entidad Evaluada:** `Factura` / `LineaFactura` (Módulo de Gestión de Cartera Financiera).
* **Descripción:** Se implementó el flujo completo de persistencia y lógica para la creación, lectura, actualización y eliminación de comprobantes de cartera.

### Enlaces Directos al Código (Rama Principal):
* [**Modelo de la Entidad (`factura.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/models/factura.py) — Propiedades, encapsulamiento y métodos de negocio (ej. `pagar()`, `calcular_total()`).
* [**Interfaz del DAO (`interface_dao.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/dao/interface_dao.py) — Definición del contrato CRUD (`guardar`, `buscar_por_id`, `actualizar`, `eliminar`).
* [**Implementación Física del CRUD (`factura_dao.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/dao/factura_dao.py) — Lógica de persistencia encargada de interactuar con el almacenamiento del sistema.

---

## 🛠️ Actividad 8: Aplicación de Patrones de Diseño GoF
El sistema integra **7 patrones de diseño del catálogo GoF** distribuidos estratégicamente entre los módulos de los tres integrantes del equipo:

### 1. Evidencia Teórica (Sustentación Visual)
* [**Documentación Interactiva (`index.html`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/index.html) — Archivo HTML que contiene la matriz comparativa de los 23 patrones GoF con sus casos de uso específicos en nuestro software de cartera, ventajas, desventajas y patrones relacionados.

### 2. Evidencia Práctica en Código:
* **Creacional (Factory Method):** [Ver `DaoFactory` en `dao_factory.py`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/factory/dao_factory.py) — Aisla el entorno de pruebas (`InMemory`) del entorno real (`JSON`). *(Desarrollado por Caren Peña)*.
* **Creacional (Builder):** [Ver `FacturaBuilder` en `factura_builder.py`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/builders/factura_builder.py) — Construcción fluida y segura de facturas validando stock en tiempo real. *(Desarrollado por Sebastian Gutierrez)*.
* **Creacional (Singleton):** [Ver `ConfiguracionApp` en `config.py`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/config/config.py) — Instancia única y thread-safe para variables globales de riesgo crediticio. *(Desarrollado por Juan Pablo Malagón)*.
* **Estructural (Decorator):** [Ver `ValidarLimiteCreditoDecorator` en `credit_decorator.py`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/decorators/credit_decorator.py) — Intercepta el CRUD para bloquear facturas que superen el cupo del cliente. *(Desarrollado por Juan Pablo Malagón)*.
* **Estructural & Comportamiento (Facade & Command):** [Ver `GestionCarteraFacade` en `facade.py`](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/src/facade/facade.py) — Fachada unificada que orquesta el ecosistema cruzado disparando un `ComandoPagarFactura`. *(Integración Grupal)*.

---

## 🧪 Actividad 7 y 8: Ejecución de Pruebas Unitarias (`unittest`)
Para garantizar la cohesión y verificar que tanto el CRUD como los patrones de diseño funcionan perfectamente de manera integrada, diseñamos **14 pruebas automatizadas**.

* [**Suite de Pruebas Completa (`test_patterns.py`)**](https://github.com/TU_USUARIO/TU_REPOSITORIO/blob/main/tests/test_patterns.py) — Archivo donde podrá auditar las asserciones lógicas de cada componente.

### Comando de ejecución utilizado:
```bash
python -m unittest tests.test_patterns -v

Integrantes del Equipo:

Sebastian Gutierrez Guayacundo (Módulo Facturación — Rama dev_sgutierrez78)

Juan Pablo Malagón Sáenz (Módulo Clientes — Rama dev_jmalagon72)

Caren Rossana Peña Castañeda (Módulo Productos — Rama dev_cpena86)

