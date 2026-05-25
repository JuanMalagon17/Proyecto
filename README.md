# 📊 Gestión Financiera de Cartera

> **Proyecto de Asignatura — Lenguajes de Programación II**  
> Universidad de La Salle · 2026  
> Correo docente: raranda@unisalle.edu.co

Sistema integral de gestión de clientes, productos y facturación con análisis financiero avanzado.  
Permite el seguimiento de métricas clave (**ROA, márgenes, morosidad**) y prepara el terreno para modelos de **Machine Learning** mediante la exportación de datasets estructurados.

---

# 🔍 GUÍA RÁPIDA DE REVISIÓN (Actividades 7 y 8)

Estimado Profesor, para agilizar el proceso de calificación, hemos unificado la navegación de los componentes evaluados.  
Toda la documentación académica y diagramas se han centralizado en la carpeta `docs/`.

---

## 📂 Actividad 7: Arquitectura y CRUDs por Componente

El sistema implementa el patrón de persistencia mediante **3 entidades CRUD** independientes conectadas bajo una interfaz base unificada:

`src/dao/interface_dao.py`

### 🧾 Módulo de Productos
**Responsable:** Caren Peña · `dev_cpena86`

- Modelo: `src/models/producto.py`
- CRUD/Persistencia: `src/dao/producto_dao.py`

### 👤 Módulo de Clientes
**Responsable:** Juan Pablo Malagón · `dev_jmalagon72`

- Modelo: `src/models/cliente.py`
- CRUD/Persistencia: `src/dao/cliente_dao.py`

### 🧾 Módulo de Facturación
**Responsable:** Sebastian Gutierrez · `dev_sgutierrez78`

- Modelo: `src/models/factura.py`
- CRUD/Persistencia: `src/dao/factura_dao.py`

---

## 🛠️ Actividad 8: Sustentación y Código de Patrones GoF

### 📑 Evidencia Teórica e Interactiva

Documentación completa disponible en la carpeta `docs/`:

- `docs/PATRONES_GOF.html`
- `docs/PATRONES_GOF.md`

### 📐 Modelado UML

- `docs/DIAGRAMA_UML.md`
- `docs/Diagrama UML.pdf`

### 💻 Código Fuente de Patrones

Implementaciones disponibles en:

- `src/patterns/`
- `src/builders/`

---

# 🏗️ Arquitectura y Stack Tecnológico

El proyecto sigue los patrones **MVC + DAO**, aplica principios **SOLID** e incorpora **Pandas** para el procesamiento y análisis de datos financieros.

```plaintext
gestion_cartera/
├── data/
│   ├── facturas.json         ← Fuente de verdad (Persistencia de Cartera)
│   └── *.csv                 ← Exportaciones para ML (generadas por analisis_cartera.py)
│
├── docs/                     ← Centralización de documentación académica y diseños
│   ├── DIAGRAMA_UML.md
│   ├── Diagrama UML.pdf
│   ├── PATRONES_GOF.html
│   └── PATRONES_GOF.md
│
├── src/
│   ├── controllers/          ← Lógica de negocio y control de transacciones
│   ├── dao/                  ← Persistencia y CRUDs de entidades
│   ├── models/               ← Entidades y modelos de dominio
│   └── patterns/             ← Implementaciones de patrones GoF
│
├── tests/
│   ├── test_cliente.py
│   ├── test_factura.py
│   ├── test_producto.py
│   └── test_patterns.py
│
├── analisis_cartera.py       ← Procesamiento financiero y exportaciones ML
├── main.py                   ← Vista principal de ejecución
├── requirements.txt
└── README.md
```

---

# ✅ Principios SOLID Aplicados

| Principio | Aplicación |
|-----------|-------------|
| **SRP — Responsabilidad única** | Modelos, controladores, DAOs y análisis trabajan desacoplados |
| **OCP — Abierto/Cerrado** | Nuevos reportes y motores de persistencia se agregan sin modificar el sistema |
| **LSP — Sustitución de Liskov** | Los DAOs concretos sustituyen correctamente las abstracciones |
| **ISP — Segregación de interfaces** | Interfaces pequeñas y enfocadas exclusivamente en persistencia |
| **DIP — Inversión de dependencias** | Los controladores dependen de abstracciones (`IDao`) y no de implementaciones concretas |

---

# 🚀 Instalación y Ejecución

Para ejecutar el sistema completo y habilitar el análisis financiero:

```bash
# Clonar repositorio
git clone <url-del-repo>
cd Proyecto

# Crear entorno virtual (opcional)
python -m venv venv

# Activar entorno virtual
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar sistema principal
python main.py

# Ejecutar análisis financiero
python analisis_cartera.py

# Ejecutar pruebas globales
python -m unittest discover tests/ -v
```

---

# 📈 Módulo de Análisis Financiero (`analisis_cartera.py`)

Diseñado como base para futuras etapas de **Machine Learning** y analítica predictiva.

## Funcionalidades principales

- Conversión de datos JSON a `pandas.DataFrame`
- Cálculo de rentabilidad por producto y cliente
- Segmentación de morosidad utilizando `pd.cut`
- Generación automática de archivos CSV
- Preparación de variables financieras para modelos predictivos

---

# 📊 Métricas Financieras Implementadas

| Métrica | Origen | Propósito |
|----------|---------|------------|
| **ROA de cartera** | `analisis_cartera.py` | Medir eficiencia de activos financieros |
| **Índice de morosidad** | `pd.cut` | Clasificación de riesgo por días vencidos |
| **Margen bruto** | `Pandas assign()` | Evaluar rentabilidad por producto y período |
| **Tasa de cobranza** | Lógica de negocio | Medir eficacia del flujo de caja |
| **Rentabilidad por producto** | Agrupaciones Pandas | Detectar productos más estables y rentables |

---

# 🎨 Patrones GoF Implementados

El proyecto incorpora patrones clásicos del catálogo **Gang of Four (GoF)** para mejorar escalabilidad, desacoplamiento y mantenibilidad.

| Patrón | Tipo | Implementación |
|---------|------|----------------|
| **Builder** | Creacional | Construcción segura y fluida de facturas complejas |
| **Factory Method** | Creacional | Creación desacoplada de DAOs |
| **Singleton** | Creacional | Configuración global del sistema |
| **Decorator** | Estructural | Validaciones dinámicas de límites de crédito |
| **Strategy** | Comportamiento | Exportación flexible de reportes |
| **Facade** | Estructural | Punto unificado de interacción entre módulos |
| **Command** | Comportamiento | Encapsulamiento de operaciones transaccionales |

---

# 🔮 Visión: Hacia el Machine Learning

La arquitectura fue diseñada para facilitar la evolución hacia modelos predictivos y analítica avanzada.

## Capacidades preparadas

### 🧠 Ingeniería de características

Variables derivadas como:

- `margen_pct`
- `dias_vencimiento`
- `n_facturas`

### 📂 Datasets listos para ML

Exportación automática a CSV compatibles con:

- `scikit-learn`
- `tensorflow`
- `pandas`

### 📉 Predicción de morosidad

Preparación de perfiles transaccionales para clasificación predictiva del riesgo financiero.

### 📈 Forecasting financiero

Generación de históricos indexados para análisis de series temporales y proyección de flujo de caja.

---

# 📋 Dependencias

```plaintext
pandas>=2.0.0      # Procesamiento y análisis financiero
pytest>=7.0        # Framework de pruebas automatizadas (opcional)
markdown>=3.5      # Conversión de documentación a HTML
```

---

# 🧪 Pruebas Unitarias

El sistema incluye una suite automatizada para validar:

- CRUDs de las entidades
- Persistencia de datos
- Reglas de negocio
- Implementación de patrones GoF

## Ejecutar pruebas por módulo

```bash
# CRUD Productos
python -m unittest tests/test_producto.py -v

# CRUD Clientes
python -m unittest tests/test_cliente.py -v

# CRUD Facturas
python -m unittest tests/test_factura.py -v
```

## Ejecutar pruebas de Patrones GoF

```bash
python -m unittest tests.test_patterns -v
```

## Ejecutar suite completa

```bash
python -m unittest discover tests/ -v
```

---

# 🏁 Conclusión

El proyecto consolida una arquitectura robusta basada en principios de ingeniería de software moderna:

- Persistencia desacoplada mediante DAO
- Diseño extensible con patrones GoF
- Métricas financieras avanzadas
- Integración analítica con Pandas
- Preparación estructural para Machine Learning

---

*Proyecto académico — Lenguajes de Programación II · Universidad de La Salle · 2026*