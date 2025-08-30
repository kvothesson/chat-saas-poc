# Agente Comercial SaaS - PoC

**Estado:** Draft (PoC)  
**Autores:** Equipo (Ezequiel + IA)  
**Fecha:** 29-08-2025

## 🎯 Resumen

Construimos un **AI Agent comercial** que responde como un vendedor humano por WhatsApp/Chat (estilo natural, emojis, precios y planes de pago), reutilizable para **cualquier rubro y país**. 

La PoC usa **Groq** como LLM (único costo variable) y **infra gratuita** para el resto:
- **Frontend estático** en GitHub Pages
- **API edge** en Cloudflare Workers (free tier) como proxy seguro al LLM
- **Catálogo & perfil del negocio** como JSON público

## 🏗️ Arquitectura

```
Cliente (GH Pages)
  └─ Chat Web (HTML/JS)  
      └─ POST /chat → Cloudflare Worker (TypeScript)
             ├─ Carga Business/Profile + Catálogo (JSON del repo)
             ├─ Calcula ofertas (descuentos/cuotas) + formatea moneda
             └─ Llama a Groq (Chat Completions) con:
                   - system prompt (políticas, tono, estilo WhatsApp)
                   - context (catálogo y ofertas ya calculadas)
                   - user message
```

## 🚀 Setup Rápido

### 1. Preparar Cloudflare Worker

```bash
cd worker
npm install
```

### 2. Configurar Variables de Entorno

En el dashboard de Cloudflare → Workers & Pages → tu-worker → Settings → Variables:

- **GROQ_API_KEY** (secreto): Tu API key de Groq
- **GROQ_MODEL** (opcional): Modelo a usar (default: `llama3-70b-8192`)
- **BUSINESS_JSON_URL** (opcional): URL al JSON del negocio

### 3. Deploy del Worker

```bash
cd worker
npm run deploy
```

### 4. Configurar Frontend

En `site/app.js`, cambiar:
```js
const API_BASE = "https://<tu-worker>.workers.dev";
```

### 5. Deploy Frontend

Subir la carpeta `site/` a GitHub Pages o cualquier hosting estático.

## 📁 Estructura del Proyecto

```
├── worker/                 # Cloudflare Worker (TypeScript)
│   ├── src/index.ts       # Lógica principal del agente
│   ├── wrangler.toml      # Configuración de Wrangler
│   ├── package.json       # Dependencias
│   └── tsconfig.json      # Configuración TypeScript
├── site/                  # Frontend estático
│   ├── index.html         # Página principal
│   └── app.js            # Lógica del chat
├── data/                  # Perfiles de negocio
│   └── business.json      # Ejemplo Ring Jewelers
└── README.md              # Este archivo
```

## 🧪 Testing

### Casos de Prueba Sugeridos

1. **Consulta en español:**
   ```
   "Me mostrás anillos solitarios en oro amarillo?"
   ```
   → Debe responder en español con productos y ofertas pre-calculadas

2. **Cambio de idioma:**
   ```
   "Can you show me men's rings under 700k?"
   ```
   → Debe responder en inglés y formato de moneda del negocio

3. **Consulta de políticas:**
   ```
   "¿Cuánto tardan las entregas?"
   ```
   → Debe citar la política del perfil del negocio

## 🔧 Personalización

### Crear Nuevo Negocio

1. Crear archivo JSON en `data/` siguiendo el esquema de `business.json`
2. Configurar `BUSINESS_JSON_URL` en el Worker o pasar el JSON directamente en el frontend
3. Personalizar:
   - `tone.style`: Estilo de comunicación
   - `payments.discounts`: Descuentos disponibles
   - `payments.installments`: Opciones de cuotas
   - `catalog`: Productos/servicios

### Ejemplo de Otros Rubros

- **Pastelería:** Cupcakes, tortas, postres
- **Mecánica:** Servicios, repuestos, mantenimiento
- **Cursos:** Programación, idiomas, cocina
- **Consultoría:** IT, marketing, legal

## 🛡️ Seguridad

- **API Key protegida:** Solo vive en el Worker (env var)
- **CORS configurable:** En PoC abierto (`*`), restringible por dominio
- **Validación:** El LLM solo usa datos del catálogo (no inventa)
- **Guardrails:** Si consulta fuera de catálogo → "consultaré al equipo"

## 📊 Métricas

- Latencia total (objetivo < 2.5s)
- Tokens por respuesta
- Tasa de "pedidos de aclaración"

## 🚧 Roadmap

- **PoC (semana 1):** ✅ Front + Worker + un JSON de negocio
- **MVP:** Multinegocio, editor de catálogo (CSV → JSON), logs persistentes
- **Futuro:** Integración WhatsApp Business, pasarela de pago

## 💰 Costos

- **Groq API:** Único costo variable (~$0.05 por 1M tokens)
- **Infraestructura:** 100% gratuita (Cloudflare Workers free tier + GitHub Pages)
- **Escalabilidad:** Worker free tier: 100k requests/día

## 🔍 Troubleshooting

### Error "Groq API error 401"
- Verificar que `GROQ_API_KEY` esté configurada correctamente
- Confirmar que la API key tenga permisos para el modelo especificado

### Error "Worker not found"
- Verificar que el Worker esté deployado correctamente
- Confirmar la URL en `API_BASE` del frontend

### Respuestas lentas
- Verificar latencia de Groq API
- Considerar usar modelo más rápido (ej: `llama3-8b-8192`)

## 📝 Licencia

MIT para el código de la PoC.

## 🤝 Contribuir

1. Fork del repo
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request

---

**¿Preguntas?** Abrir un issue o contactar al equipo.
