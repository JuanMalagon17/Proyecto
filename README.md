# 📊 Gestión Financiera de Cartera

> **Proyecto de Asignatura — Lenguajes de Programación II**  
> Universidad de La Salle · 2026  
> Correo docente: raranda@unisalle.edu.co

Sistema de gestión de clientes, productos y facturas con **análisis financiero de cartera** (ROA, márgenes, tasa de cobranza). Construido en Python puro con persistencia en JSON.

---

## 🏗️ Arquitectura

El proyecto aplica estrictamente los patrones **MVC + DAO** y los principios **SOLID**:

```
gestion_cartera/
├── data/
│   └── facturas.json           ← Persistencia (única fuente de verdad)
├── src/
│   ├── models/                 ← M (Model): entidades de dominio
│   │   ├── cliente.py
│   │   ├── producto.py
│   │   └── factura.py
│   ├── dao/                    ← Data Access Object (abstracción + implementación JSON)
│   │   ├── interface_dao.py    ← IDao[T]: contrato genérico (DIP)
│   │   ├── cliente_dao.py
│   │   ├── producto_dao.py
│   │   └── factura_dao.py
│   ├── controllers/            ← C (Controller): lógica de negocio y métricas
│   │   └── factura_controller.py
│   └── patterns/               ← Actividad 8: patrones GoF implementados
│       └── gof_patterns.py
├── tests/
│   ├── test_factura.py         ← 20 pruebas unitarias (Actividad 7)
│   └── test_patterns.py        ← 14 pruebas unitarias (Actividad 8)
├── main.py                     ← V (View): entrada y demo del sistema
├── PATRONES_GOF.md             ← Documento Actividad 8
├── PATRONES_GOF.html           ← HTML generado de la Actividad 8
├── requirements.txt
└── README.md
```

### Principios SOLID aplicados

| Principio | Dónde se aplica |
|-----------|-----------------|
| **SRP** — Responsabilidad única | Cada clase tiene un solo motivo de cambio: modelos solo modelan, DAOs solo persisten, Controller solo coordina |
| **OCP** — Abierto/cerrado | Nuevas estrategias de reporte o nuevos DAOs se agregan sin modificar código existente |
| **LSP** — Sustitución de Liskov | `ClienteDao`, `ProductoDao`, `FacturaDao` sustituyen a `IDao[T]` sin romper contratos |
| **ISP** — Segregación de interfaces | `IDao[T]` define solo 5 métodos CRUD esenciales |
| **DIP** — Inversión de dependencias | `FacturaController` recibe `IDao[T]` por constructor; nunca instancia DAOs concretos |

---

## 🚀 Instalación y ejecución

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd gestion_cartera

# (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar demo completo
python main.py

# Ejecutar pruebas unitarias (Actividad 7)
python -m unittest tests/test_factura.py -v

# Ejecutar pruebas de patrones GoF (Actividad 8)
python -m unittest tests/test_patterns.py -v

# Ejecutar TODAS las pruebas (34 en total)
python -m unittest discover tests/ -v
```

---

## ✅ Actividad 7 — CRUD con pruebas unitarias

**Entidad principal:** `Factura` (con `Cliente` y `Producto` como entidades de soporte)

### Operaciones CRUD implementadas

| Operación | Método Controller | Descripción |
|-----------|-------------------|-------------|
| **Create** | `crear_factura()` | Crea factura vinculada a cliente existente |
| **Create** | `agregar_linea_a_factura()` | Agrega producto, descuenta stock, actualiza saldo cliente |
| **Read** | `obtener_factura()` | Busca por id |
| **Read** | `listar_facturas()` | Lista todas las facturas |
| **Update** | `pagar_factura()` | Cambia estado → PAGADA, reduce saldo cliente |
| **Update** | `anular_factura()` | Cambia estado → ANULADA |
| **Delete** | `eliminar_factura()` | Elimina del JSON |

### Resultados de las pruebas (20/20 ✅)

```
TC-01  Crear cliente con datos válidos                     ✅ ok
TC-02  Email inválido lanza ValueError                     ✅ ok
TC-03  id_cliente vacío lanza ValueError                   ✅ ok
TC-04  Margen bruto calculado correctamente                ✅ ok
TC-05  Stock insuficiente lanza ValueError                 ✅ ok
TC-06  Total factura = suma de subtotales                  ✅ ok
TC-07  Pagar factura → estado PAGADA                       ✅ ok
TC-08  Pagar factura ya pagada → ValueError                ✅ ok
TC-09  Crear y recuperar cliente por id                    ✅ ok
TC-10  Actualizar email de cliente                         ✅ ok
TC-11  Eliminar cliente sin facturas pendientes            ✅ ok
TC-12  Crear factura para cliente válido                   ✅ ok
TC-13  Crear factura para cliente inexistente → Error      ✅ ok
TC-14  Agregar línea descuenta stock y actualiza saldo     ✅ ok
TC-15  Pagar factura reduce saldo del cliente              ✅ ok
TC-16  Resumen de cartera con cálculos correctos           ✅ ok
TC-17  Tasa de cobranza 0% sin pagos                       ✅ ok
TC-18  Rentabilidad por producto correcta                  ✅ ok
TC-19  Listar productos en BD vacía → lista vacía          ✅ ok
TC-20  Eliminar producto existente retorna True            ✅ ok
```

---

## 🎨 Actividad 8 — Patrones GoF

Ver documento completo: [`PATRONES_GOF.md`](PATRONES_GOF.md) · [`PATRONES_GOF.html`](PATRONES_GOF.html)

### Tabla resumen de los 23 patrones

| Categoría | Patrones |
|-----------|----------|
| **Creacionales** (5) | Abstract Factory, Builder, Factory Method, Prototype, Singleton |
| **Estructurales** (7) | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| **De Comportamiento** (11) | Chain of Responsibility, Command, Interpreter, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor |

### Patrones implementados en el proyecto

| # | Patrón | Clase(s) clave | Pruebas |
|---|--------|----------------|---------|
| 1 | **Builder** | `FacturaBuilder` | B-1, B-2 ✅ |
| 2 | **Factory Method** | `JsonDaoFactory`, `InMemoryDaoFactory` | FM-1, FM-2 ✅ |
| 3 | **Singleton** | `ConfiguracionApp` | S-1, S-2 ✅ |
| 4 | **Decorator** | `ValidarLimiteCreditoDecorator`, `LogAuditoriaDecorator` | D-1, D-2 ✅ |
| 5 | **Strategy** | `ReporteTextoPlano`, `ReporteCSV`, `ReporteJSON` | ST-1, ST-2 ✅ |
| 6 | **Facade** | `GestionCarteraFacade` | FA-1, FA-2 ✅ |
| 7 | **Command** | `ComandoPagarFactura`, `HistorialComandos` | CMD-1, CMD-2 ✅ |

---

## 📈 Métricas financieras implementadas

El `FacturaController` calcula las siguientes métricas de cartera:

| Métrica | Fórmula | Descripción |
|---------|---------|-------------|
| **Total facturado** | Σ subtotales de líneas | Volumen total de ventas |
| **Utilidad bruta** | Total facturado − Costo total | Ganancia antes de gastos operativos |
| **Margen bruto %** | (Utilidad / Total) × 100 | Eficiencia por venta |
| **ROA de cartera** | (Utilidad / Activos cartera) × 100 | Rentabilidad sobre activos gestionados |
| **Tasa de cobranza** | (Cobrado / Facturado) × 100 | Eficiencia del proceso de cobro |
| **Rentabilidad por producto** | Utilidad por SKU agrupada | Identifica productos más rentables |

---

## 🔮 Visión futura (Proyecto Asignatura)

El diseño actual prepara la base para análisis con **Machine Learning**:

- Los datos JSON se exportan fácilmente a `pandas.DataFrame`
- Las métricas de cartera alimentan modelos de **predicción de morosidad** (clasificación)
- El historial de facturas permite **forecasting de ventas** (series de tiempo)
- El `Strategy` de reportes puede extenderse con visualizaciones `matplotlib`/`plotly`

---

## 📋 Dependencias

```
# Sin dependencias externas de producción (solo stdlib de Python 3.11+)
# Para desarrollo y pruebas:
pytest>=7.0          # opcional, unittest viene incluido en Python
markdown>=3.5        # solo para regenerar el HTML de la Actividad 8
```

---

*Proyecto académico — Lenguajes de Programación II · Universidad de La Salle · 2026*
