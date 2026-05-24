# 📊 Gestión Financiera de Cartera

> **Proyecto de Asignatura — Lenguajes de Programación II**  
> Universidad de La Salle · 2026  
> Correo docente: raranda@unisalle.edu.co

Sistema integral de gestión de clientes, productos y facturación con análisis financiero avanzado.  
Permite el seguimiento de métricas clave (**ROA, márgenes, morosidad**) y prepara el terreno para modelos de **Machine Learning** mediante la exportación de datasets estructurados.

---

# 🏗️ Arquitectura y Stack Tecnológico

El proyecto sigue los patrones **MVC + DAO**, aplica principios **SOLID** e incorpora **Pandas** para el procesamiento y análisis de datos financieros.

```plaintext
gestion_cartera/
├── data/
│   ├── facturas.json           ← Fuente de verdad (Persistencia)
│   └── *.csv                   ← Exportaciones para ML (generadas por analisis_cartera.py)
├── src/
│   ├── models/                 ← Modelos de dominio (Entidades)
│   ├── dao/                    ← Capa de acceso a datos (Patrón DAO)
│   ├── controllers/            ← Lógica de negocio y métricas
│   └── patterns/               ← Implementación GoF (Builder, Strategy, etc.)
├── tests/
│   ├── test (por entidad)      ← Creación de todos los test del modelo
├── analisis_cartera.py         ← Módulo de análisis avanzado con Pandas
└── main.py                     ← Vista principal (View)

```

---

## ✅ Principios SOLID aplicados

| Principio | Aplicación |
|-----------|-------------|
| **SRP** — Responsabilidad única | Cada módulo tiene una única responsabilidad: modelos, DAOs, controladores y análisis trabajan desacoplados |
| **OCP** — Abierto/cerrado | Nuevos reportes o motores de persistencia pueden añadirse sin modificar el código existente |
| **LSP** — Sustitución de Liskov | Los DAOs concretos reemplazan correctamente la abstracción `IDao[T]` |
| **ISP** — Segregación de interfaces | Interfaces DAO pequeñas y enfocadas únicamente en operaciones CRUD |
| **DIP** — Inversión de dependencias | `main.py` y los controladores dependen de abstracciones y no de implementaciones concretas |

---

# 🚀 Instalación y Ejecución

Para ejecutar el sistema completo y habilitar el procesamiento de datos financieros con Pandas:

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd Proyecto

# (Opcional) Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar sistema principal
python main.py

# Ejecutar análisis financiero independiente
python analisis_cartera.py

# Ejecutar pruebas unitarias
python -m unittest discover tests/ -v
```

---

# 📈 Módulo de Análisis Financiero (`analisis_cartera.py`)

Diseñado como base para futuras etapas de **Machine Learning** y analítica predictiva.

## Funcionalidades principales

- Conversión de datos relacionales JSON a `pandas.DataFrame`
- Cálculo de rentabilidad por producto y cliente
- Segmentación de morosidad utilizando `pd.cut`
- Generación automática de archivos CSV para entrenamiento de modelos
- Preparación de variables financieras para análisis predictivo

---

# 📊 Métricas Financieras Implementadas

| Métrica | Origen | Propósito |
|----------|---------|------------|
| **ROA de cartera** | `analisis_cartera.py` | Medir eficiencia de activos financieros |
| **Índice de morosidad** | `pd.cut` | Clasificación de riesgo por días vencidos |
| **Margen bruto** | Pandas `assign()` | Evaluar rentabilidad por producto y período |
| **Tasa de cobranza** | Lógica de negocio | Medir eficacia del flujo de caja |
| **Rentabilidad por producto** | Agrupaciones Pandas | Detectar productos más rentables |

---

# 🎨 Patrones GoF Implementados

El proyecto incorpora patrones clásicos de diseño para mejorar escalabilidad y mantenibilidad.

| Patrón | Implementación |
|---------|----------------|
| **Builder** | Construcción flexible de facturas |
| **Factory Method** | Creación desacoplada de DAOs |
| **Singleton** | Configuración global del sistema |
| **Decorator** | Validaciones y auditoría extensibles |
| **Strategy** | Diferentes formatos de reportes |
| **Facade** | Simplificación de operaciones complejas |
| **Command** | Gestión de acciones sobre facturas |

---

# 🔮 Visión: Hacia el Machine Learning

La arquitectura fue diseñada para facilitar una transición futura hacia modelos predictivos y analítica avanzada.

## Capacidades preparadas

- **Ingeniería de características**
  - Variables como `margen_pct`, `dias_vencimiento`, `n_facturas`

- **Datasets listos para ML**
  - Exportación automática de CSV para:
    - `scikit-learn`
    - `tensorflow`
    - `pandas`

- **Predicción de morosidad**
  - Clasificación de clientes según comportamiento de pago

- **Forecasting financiero**
  - Proyección de ventas y flujo de caja mediante series de tiempo

---

# 📋 Dependencias

```plaintext
pandas>=2.0.0      # Procesamiento y análisis de datos
pytest>=7.0        # Pruebas automatizadas (opcional)
markdown>=3.5      # Generación de documentación HTML
```

---

# 🧪 Pruebas Unitarias

El sistema incluye pruebas para lógica de negocio y patrones GoF.

```bash
# Ejecutar pruebas CRUD
python -m unittest tests/test_factura.py -v

# Ejecutar pruebas de patrones
python -m unittest tests/test_patterns.py -v

# Ejecutar todas las pruebas
python -m unittest discover tests/ -v
```

---

*Proyecto académico — Lenguajes de Programación II · Universidad de La Salle · 2026*