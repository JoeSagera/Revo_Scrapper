"""
Quick Start Guide - REVÓLICO DEALS FINDER

Para ejecutar el proyecto en modo real vs. prueba:

================================
1. OPCIÓN A: LÍNEA DE COMANDOS
================================

# Scraping con datos simulados (prueba rápida)
python main.py "car" 1 --mock

# Scraping real de Revolico (puede tomar 1-2 minutos)
python main.py "car" 1

# Múltiples páginas
python main.py "motorcycle" 2

# Ver ayuda
python main.py --help


================================
2. OPCIÓN B: INTERFAZ WEB (RECOMENDADO)
================================

# Inicia la interfaz Streamlit
streamlit run app.py

# Se abrirá automáticamente en http://localhost:8501
# Si no abre, copia la URL en tu navegador


================================
3. PRUEBAS
================================

# Ejecutar test suite
python test.py


================================
REQUISITOS PREVIOS
================================

✅ Python 3.12+ instalado
✅ Dependencias instaladas: pip install -r requirements.txt
✅ Playwright instalado: playwright install chromium


================================
PRIMEROS PASOS RECOMENDADOS
================================

1. Ejecuta las pruebas:
   python test.py

2. Prueba con datos simulados:
   python main.py "car" 1 --mock

3. Abre la interfaz web:
   streamlit run app.py

4. Cuando funcione, cambia a scraping real en app.py
   (o configura use_mock=False en main.py)


================================
TROUBLESHOOTING
================================

❌ ModuleNotFoundError: 
   → Asegúrate de estar en la carpeta raíz del proyecto

❌ "Found 0 listings":
   → El sitio cambió su estructura
   → Revisa los logs: logs/scraper.log
   → Prueba con --mock mientras investigas

❌ Timeout error:
   → Aumenta REQUEST_DELAY_MIN/MAX en config.py
   → Verifica tu conexión a internet

❌ Playwright error:
   → playwright install chromium
   → pip install --force-reinstall playwright


================================
CONFIGURACIÓN RECOMENDADA
================================

Para desarrollo rápido:
config.SCRAPER_TIMEOUT = 20000  # 20 segundos

Para scraping profundo:
config.REQUEST_DELAY_MIN = 3
config.REQUEST_DELAY_MAX = 7

Para máxima precisión:
config.DEAL_THRESHOLD = 2.0  # más estricto
config.SCAM_THRESHOLD = 0.3  # más estricto


================================
CASOS DE USO
================================

Buscar autos baratos:
  python main.py "auto" 2
  python main.py "carro" 2
  python main.py "máquina" 1

Buscar motos:
  python main.py "moto" 1
  python main.py "motorcycle" 1

Buscar casas:
  python main.py "casa" 1
  python main.py "apartment" 2


¡Listo! Tu proyecto está completo y funcional. 🚀
"""

print(__doc__)
