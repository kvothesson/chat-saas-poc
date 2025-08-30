# 🔍 Debug Tracker para Groq API

Este módulo permite monitorear en tiempo real el uso de tokens, costos y estadísticas acumuladas de la API de Groq.

## 🚀 Características

- **Tracking automático** de tokens de entrada y salida
- **Cálculo de costos** basado en precios oficiales de Groq
- **Estadísticas diarias, mensuales y totales**
- **Persistencia de datos** en archivos JSON
- **Modo debug configurable** via variables de entorno
- **Endpoints REST** para consultar estadísticas

## ⚙️ Configuración

### Variables de Entorno

```bash
# Activar modo debug
export GROQ_DEBUG=true

# Guardar datos en archivos (opcional)
export GROQ_SAVE_DEBUG=true

# API Key de Groq
export GROQ_API_KEY=tu_api_key_aqui
```

### Archivo .env

```bash
GROQ_DEBUG=true
GROQ_SAVE_DEBUG=true
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama3-70b-8192
```

## 📊 Uso

### 1. Tracking Automático

El tracker se integra automáticamente en `app.py` y registra cada llamada a Groq:

```python
from debug_tracker import debug_tracker

# Se ejecuta automáticamente en call_groq()
# No necesitas hacer nada más
```

### 2. Consultar Estadísticas

#### Via Endpoints REST

```bash
# Estadísticas del día
curl http://localhost:5001/debug/stats?type=today

# Estadísticas del mes
curl http://localhost:5001/debug/stats?type=month

# Estadísticas totales
curl http://localhost:5001/debug/stats?type=total

# Imprimir resumen en consola
curl http://localhost:5001/debug/summary?type=today
```

#### Via Python

```python
from debug_tracker import debug_tracker

# Resumen del día
daily = debug_tracker.get_daily_summary()

# Resumen del mes
monthly = debug_tracker.get_monthly_summary()

# Resumen total
total = debug_tracker.get_total_summary()

# Imprimir en consola
debug_tracker.print_summary("today")
```

## 💰 Precios Soportados

El tracker incluye precios actualizados para los modelos más populares de Groq:

- **Llama 3.3 70B Versatile**: $0.59/M input, $0.79/M output
- **Llama 3.1 8B Instant**: $0.05/M input, $0.08/M output
- **Qwen3 32B**: $0.29/M input, $0.59/M output
- **Gemma 2 9B**: $0.20/M input, $0.20/M output
- **GPT OSS 20B**: $0.10/M input, $0.50/M output
- **Kimi K2 1T**: $1.00/M input, $3.00/M output

## 📁 Estructura de Datos

### Archivos Generados

```
debug_data/
├── daily_stats.json      # Estadísticas diarias
└── usage_log.json        # Log detallado de uso
```

### Formato de Datos

#### Daily Stats
```json
{
  "2025-01-15": {
    "date": "2025-01-15",
    "total_requests": 25,
    "total_input_tokens": 15000,
    "total_output_tokens": 8000,
    "total_cost_usd": 0.0125,
    "models_used": {
      "llama3-70b-8192": 20,
      "llama3-8b-8192": 5
    }
  }
}
```

#### Usage Log
```json
[
  {
    "input_tokens": 1500,
    "output_tokens": 800,
    "total_tokens": 2300,
    "cost_usd": 0.00125,
    "timestamp": "2025-01-15T10:30:00",
    "model": "llama3-70b-8192",
    "request_id": "chat_1705312200"
  }
]
```

## 🧪 Pruebas

### Script de Prueba

```bash
# Activar debug mode
export GROQ_DEBUG=true

# Ejecutar prueba
python3 test_debug_tracker.py
```

### Prueba Manual

```bash
# 1. Iniciar servidor con debug activado
export GROQ_DEBUG=true
python3 -m app.main

# 2. Hacer algunas llamadas al chat
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿cómo estás?"}'

# 3. Consultar estadísticas
curl http://localhost:5001/debug/stats?type=today
```

## 🔧 Personalización

### Agregar Nuevos Modelos

```python
# En debug_tracker.py, agregar al diccionario pricing
self.pricing["nuevo-modelo"] = {"input": 0.50, "output": 0.75}
```

### Modificar Lógica de Tracking

```python
# Sobrescribir métodos en una clase heredada
class CustomDebugTracker(GroqDebugTracker):
    def track_request(self, model, input_tokens, output_tokens, request_id=None):
        # Lógica personalizada aquí
        super().track_request(model, input_tokens, output_tokens, request_id)
```

## 📈 Monitoreo en Producción

### Logs Estructurados

```python
# Los datos se guardan automáticamente en debug_data/
# Puedes usar herramientas como ELK Stack o Grafana para visualización
```

### Alertas de Costos

```python
# Ejemplo de alerta cuando se supera un umbral
daily_cost = debug_tracker.get_daily_summary()["total_cost_usd"]
if daily_cost > 1.0:  # $1 USD por día
    print(f"⚠️ Costo diario alto: ${daily_cost:.2f}")
```

## 🚨 Troubleshooting

### Debug Mode No Funciona

1. Verificar variable de entorno: `echo $GROQ_DEBUG`
2. Crear archivo `.env` con `GROQ_DEBUG=true`
3. Reiniciar el servidor

### Datos No Se Guardan

1. Verificar permisos de escritura en directorio `debug_data/`
2. Verificar variable `GROQ_SAVE_DEBUG=true`
3. Revisar logs de error en consola

### Precios Incorrectos

1. Verificar que el modelo esté en el diccionario `pricing`
2. Actualizar precios según [Groq Pricing](https://console.groq.com/pricing)
3. El tracker usa precios por defecto si no encuentra el modelo

## 📚 Referencias

- [Groq API Documentation](https://console.groq.com/docs)
- [Groq Pricing](https://console.groq.com/pricing)
- [Flask Documentation](https://flask.palletsprojects.com/)
