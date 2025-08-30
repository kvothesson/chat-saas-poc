# Chat SaaS PoC

Un proof of concept de un sistema de chat comercial SaaS con datos centralizados del negocio.

## 🏗️ Arquitectura

- **`data/business.json`**: Fuente única de verdad para la información del negocio
- **`site/`**: Frontend web con chat
- **`worker/`**: Worker de Cloudflare que maneja la lógica del chat
- **Datos centralizados**: No más duplicación de información entre archivos

## 🚀 Desarrollo

### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar variables de entorno
En `worker/wrangler.toml`, asegúrate de tener:
```toml
[vars]
BUSINESS_JSON_URL = "http://localhost:3001/business.json"
```

### 3. Ejecutar entorno de desarrollo
```bash
npm run dev
```

Esto iniciará:
- Servidor de datos en `http://localhost:3001`
- Frontend en `http://localhost:3000`

### 4. Configurar API Key de Groq
En el dashboard de Cloudflare Workers, agrega la variable secreta `GROQ_API_KEY`.

## 🚀 Producción

### 1. Actualizar URL del business.json
En `worker/wrangler.toml`, cambia:
```toml
BUSINESS_JSON_URL = "https://raw.githubusercontent.com/<user>/<repo>/main/data/business.json"
```

### 2. Deploy del worker
```bash
npm run deploy:worker
```

## 📁 Estructura del Proyecto

```
├── data/
│   └── business.json          # ✅ Fuente única de datos del negocio
├── site/
│   ├── app.js                 # ✅ Carga datos desde JSON
│   ├── index.html
│   └── serve-data.js          # ✅ Servidor local para desarrollo
├── worker/
│   ├── src/index.ts           # ✅ Lee datos desde URL configurada
│   └── wrangler.toml          # ✅ Configuración de variables
└── package.json               # ✅ Scripts de desarrollo
```

## 🔄 Flujo de Datos

1. **`data/business.json`** contiene toda la información del negocio
2. **`site/app.js`** carga los datos al inicializar
3. **`worker/src/index.ts`** lee los datos desde la URL configurada
4. **No hay duplicación** - un solo lugar para mantener la información

## 🎯 Beneficios

- ✅ **Mantenimiento simple**: Cambios en un solo archivo
- ✅ **Consistencia**: No más datos desincronizados
- ✅ **Escalabilidad**: Fácil agregar nuevos negocios
- ✅ **Desarrollo**: Entorno local funcional
- ✅ **Producción**: URL pública configurable
