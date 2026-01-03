# 🔍 Revolico Deals Finder

Una herramienta profesional de web scraping y análisis para encontrar las mejores ofertas en Revolico.com, detectando automáticamente gangas y posibles estafas.

## ✨ Características

### Scraping & Analysis
- **Web Scraping Avanzado**: Utiliza Playwright para scraping confiable con manejo de errores robusto
- **Análisis Inteligente de Precios**: 
  - Limpieza automática de precios (detecta USD, CUP, MLC)
  - Conversión de monedas con tasas configurables
  - Análisis estadístico para detectar anomalías
- **Clasificación de Listados**:
  - 🔥 **GANGA**: Ofertas excepcionales (por debajo de media - 1.5σ)
  - ⚠️ **POSIBLE ESTAFA**: Precios anormalmente bajos (< 40% de la media)
  - ✅ **MERCADO**: Precios normales

### Interfaz Mejorada 🎨
- **Sidebar Avanzado**: Secciones organizadas para búsqueda, filtros, configuración
- **Filtrado Multi-nivel**:
  - Filtro por etiqueta (Ganga, Estafa, Mercado)
  - Filtro por moneda (USD, CUP, MLC)
  - Rango de precio dinámico
  - 4 opciones de ordenamiento (precio, título, etiqueta)
- **Dashboard de Métricas**: 5 KPIs con información en tiempo real
- **Tabla de Resultados**: Color-codificada con detalles expandibles
- **Gráficos Analíticos**: 3 tabs (Distribución, Tendencias, Categorías)
- **Botones de Acción**: Scrape, Exportar, Refrescar, Limpiar

### General
- **Logging Completo**: Rastreo detallado de todas las operaciones
- **Configuración Centralizada**: Variables globales fáciles de ajustar
- **Exportación de Datos**: Descarga resultados en CSV
- **Modo Mock**: Prueba la interfaz sin scraping

## 🚀 Inicio Rápido

### Requisitos
- Python 3.12+
- Windows/Linux/macOS

### Instalación

```bash
# Clonar o descargar el repositorio
cd Revo_Scrapper

# Crear entorno virtual
python -m venv venv

# Activar entorno
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegadores para Playwright
playwright install chromium
```

### Uso Básico

#### 1. Scraping por línea de comandos (sin interfaz gráfica)

```bash
# Scraping real de Revolico
python main.py "cars" 1

# Scraping de múltiples páginas
python main.py "motorcycle" 2

# Usar datos simulados para pruebas
python main.py "house" 1 --mock
```

#### 2. Interfaz Web (Recomendado)

```bash
streamlit run app.py
```

Luego abre tu navegador en `http://localhost:8501`

## 📁 Estructura del Proyecto

```
Revo_Scrapper/
├── config.py              # Configuración centralizada
├── logger.py              # Utilidades de logging
├── main.py                # Script principal de orquestación
├── app.py                 # Interfaz Streamlit
├── requirements.txt       # Dependencias Python
├── README.md              # Este archivo
│
├── src/
│   ├── __init__.py
│   ├── scraper.py         # Scraper con Playwright (clase RevolicoScraper)
│   └── processor.py       # Procesador de datos (clase DataProcessor)
│
├── data/                  # Directorio de resultados
│   └── results.json       # Último archivo de resultados
│
├── logs/
│   └── scraper.log        # Archivo de log
│
└── .cache/                # Cache de datos
```

## ⚙️ Configuración

Todas las configuraciones están centralizadas en `config.py`:

```python
# Tasas de cambio
EXCHANGE_RATES = {
    "CUP": 350,  # 1 USD = 350 CUP
    "USD": 1,
    "MLC": 1,
}

# Thresholds de clasificación
DEAL_THRESHOLD = 1.5      # σ por debajo de la media = ganga
SCAM_THRESHOLD = 0.4      # 40% de la media = estafa

# Limites de precio (USD)
MIN_PRICE = 0.1
MAX_PRICE = 1000000

# Scraper
SCRAPER_TIMEOUT = 30000   # ms
REQUEST_DELAY_MIN = 2     # segundos
REQUEST_DELAY_MAX = 5
USER_AGENT_ROTATION = True
```

### Configurar variables de entorno

Crea un archivo `.env` en la raíz:

```env
LOG_LEVEL=INFO
SCRAPER_HEADLESS=true
USER_AGENT_ROTATION=true
```

## 📊 Uso de la Interfaz Web

### Panel Lateral (Settings)
- Ajusta la tasa de cambio en tiempo real
- Configura thresholds para detección de gangas/estafas
- Define rango de precios válidos

### Búsqueda
1. Ingresa tu consulta (ej: "car", "motorcycle")
2. Selecciona número de páginas a scrapear
3. Haz clic en "🚀 Scrape & Analyze"

### Resultados
- **Summary Cards**: Estadísticas rápidas (promedio, mediana, totales)
- **Tabla Detallada**: Con resaltado por categoría
- **Gráficos**: Distribución y análisis de tendencias
- **Exportación**: Descarga en CSV

## 🔧 Desarrollo

### Extensiones Posibles

1. **Caché persistente** para evitar re-scraping
2. **Notificaciones** para gangas nuevas
3. **Base de datos** para histórico de precios
4. **API REST** para integraciones
5. **Detección de duplicados** entre listados
6. **Análisis de tendencias** temporales

### Mejoras Implementadas vs Versión Anterior

- ✅ Clase `RevolicoScraper` con métodos organizados
- ✅ Clase `DataProcessor` mejorada con mejor manejo de errores
- ✅ Logging a archivos y consola
- ✅ Configuración centralizada en `config.py`
- ✅ Interfaz Streamlit profesional con múltiples secciones
- ✅ Soporte para múltiples páginas en scraping
- ✅ Manejo robusto de excepciones
- ✅ Exportación de datos (CSV, JSON)
- ✅ Estadísticas completas (media, mediana, std dev)
- ✅ Argumentos CLI para main.py

## 📈 Ejemplos de Salida

### CLI
```
============================================================
📊 REVOLICO DEALS FINDER - SUMMARY
============================================================

💰 PRICE STATISTICS (USD)
   Average:             150.00
   Median:              140.00
   Min:                  50.00
   Max:                 500.00
   Std Dev:              95.32

📈 LISTINGS BREAKDOWN
   Total:                   25
   🔥 Deals:                 3 (12.0%)
   ⚠️  Scams:               2 (8.0%)
   ✅ Normal:              20 (80.0%)

🏆 TOP 5 DEALS
   1. Toyota Camry 2015                            $45.00
   2. Honda Civic 2014                             $55.00
   3. Nissan Altima 2013                           $60.00
```

### Web UI
- Dashboard interactivo con métrica visuales
- Tabla con color-coding por categoría
- Gráficos de distribución
- Filtros ajustables en tiempo real

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'config'"
```bash
# Asegúrate de ejecutar desde la raíz del proyecto
cd /path/to/Revo_Scrapper
python main.py
```

### "No listings found"
- El sitio podría haber cambiado su estructura HTML
- Revisa los logs en `logs/scraper.log`
- Intenta con `--mock` para pruebas

### Playwright no se instala
```bash
# Reinstalar Playwright
pip install --force-reinstall playwright>=1.40.0
playwright install chromium
```

## 📝 Logs

Los logs se guardan en `logs/scraper.log` con el siguiente formato:

```
2025-01-02 15:30:45,123 - src.scraper - INFO - Starting scrape for query: car (max 1 pages)
2025-01-02 15:30:46,456 - src.processor - INFO - Processing 15 listings
2025-01-02 15:30:46,789 - src.processor - INFO - Removed 2 listings with invalid prices
```

Cambia el nivel de log en `config.py`:
```python
LOG_LEVEL = "DEBUG"  # Para más detalle
```

## 📄 Licencia

Este proyecto es de código abierto y puede ser usado libremente.

## 💡 Tips

- Usa `max_pages=1` para búsquedas rápidas
- Ajusta `REQUEST_DELAY_MIN/MAX` si obtienes errores de timeout
- Revisa los logs si algo sale mal
- La tasa de cambio CUP/USD fluctúa; actualízala regularmente
- Las gangas se detectan estadísticamente; el threshold es configurable

---

**Última actualización**: Enero 2, 2025  
**Versión**: 1.0.0
