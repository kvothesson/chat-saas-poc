# Ejemplo de Uso del Asistente

## Iniciar el servidor

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
python3 app.py
```

## Endpoints disponibles

### 1. Chat principal
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hola, ¿qué productos tienen disponibles?",
    "locale": "es-AR"
  }'
```

**Respuesta incluye información de uso:**
```json
{
  "reply": "Respuesta del asistente...",
  "locale": "es-AR",
  "business": "hervor",
  "usage": {
    "tokens": {
      "input": 1012,
      "output": 57,
      "total": 1069
    },
    "cost": {
      "usd": 0.000642,
      "formatted": "$0.000642"
    },
    "model": "llama3-70b-8192"
  }
}
```

### 2. Obtener datos del negocio
```bash
curl http://localhost:5001/business
```

### 3. Estadísticas de debug
```bash
# Estadísticas del día
curl "http://localhost:5001/debug/stats?type=today"

# Estadísticas del mes
curl "http://localhost:5001/debug/stats?type=month"

# Estadísticas totales
curl "http://localhost:5001/debug/stats?type=total"
```

### 4. Imprimir resumen en consola
```bash
curl "http://localhost:5001/debug/summary?type=today"
```

### 5. Log de uso
```bash
curl http://localhost:5001/debug/usage_log
```

## Configuración

Asegúrate de tener un archivo `.env` con:
```
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama3-70b-8192
GROQ_DEBUG=true
```

## Estructura del proyecto

```
chat-saas-poc/
├── app.py              # Servidor principal del asistente
├── debug_tracker.py    # Tracking de tokens y costos
├── data/               # Datos del negocio
│   ├── business.json   # Perfil del negocio
│   └── bakery.json     # Ejemplo de negocio
├── debug_data/         # Datos de debug
├── venv/               # Entorno virtual Python
└── .env                # Variables de entorno
```

El asistente está listo para ser integrado en cualquier frontend o aplicación que necesite funcionalidad de chat comercial.
