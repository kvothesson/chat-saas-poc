# Chat SaaS PoC

Un proof of concept de un sistema de chat comercial SaaS con datos centralizados del negocio.

## 🏗️ Arquitectura

- **`data/business.json`**: Fuente única de verdad para la información del negocio
- **`site/`**: Frontend web con chat
- **Datos centralizados**: No más duplicación de información entre archivos

## 🚀 Desarrollo

### 1. Instalar dependencias
```bash
npm install
```

### 2. Configurar variables de entorno
No se requieren variables de entorno para ejecución local.

### 3. Ejecutar entorno de desarrollo
```bash
npm run dev
```

Esto iniciará:
- Servidor de datos en `http://localhost:3001`
- Frontend en `http://localhost:3000`

### 4. Configurar API Key de Groq
Para usar la funcionalidad de chat, configura tu API key de Groq en el archivo de configuración local.

## 🚀 Producción

### 1. Actualizar URL del business.json
Para producción, actualiza la URL del archivo business.json en tu configuración local.

### 2. Deploy del sitio
```bash
# Deploy del frontend a cualquier hosting estático
```

## 📁 Estructura del Proyecto

```
├── data/
│   └── business.json          # ✅ Fuente única de datos del negocio
├── site/
│   ├── app.js                 # ✅ Carga datos desde JSON
│   ├── index.html
│   └── serve-data.js          # ✅ Servidor local para desarrollo
└── package.json               # ✅ Scripts de desarrollo
```

## 🔄 Flujo de Datos

1. **`data/business.json`** contiene toda la información del negocio
2. **`site/app.js`** carga los datos al inicializar
3. **No hay duplicación** - un solo lugar para mantener la información

## 🎯 Beneficios

- ✅ **Mantenimiento simple**: Cambios en un solo archivo
- ✅ **Consistencia**: No más datos desincronizados
- ✅ **Escalabilidad**: Fácil agregar nuevos negocios
- ✅ **Desarrollo**: Entorno local funcional
- ✅ **Producción**: URL pública configurable
