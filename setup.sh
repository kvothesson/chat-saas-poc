#!/bin/bash

echo "🚀 Configurando Chat SaaS PoC..."

# Verificar que Node.js esté instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instálalo desde https://nodejs.org/"
    exit 1
fi

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instálalo desde https://python.org/"
    exit 1
fi

echo "✅ Dependencias del sistema verificadas"

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm install

echo "✅ Dependencias instaladas"

# Crear archivo .env.example si no existe
if [ ! -f "worker/.env.example" ]; then
    echo "📝 Creando archivo de ejemplo de variables de entorno..."
    cat > worker/.env.example << EOF
# Copia este archivo a .env y configura tus variables
GROQ_API_KEY=tu_api_key_aqui
GROQ_MODEL=llama3-70b-8192
BUSINESS_JSON_URL=http://localhost:3001/business.json
EOF
fi

echo ""
echo "🎯 Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura tu GROQ_API_KEY en el dashboard de Cloudflare Workers"
echo "2. Ejecuta: npm run dev"
echo "3. Abre http://localhost:3000 en tu navegador"
echo ""
echo "🔧 Para desarrollo:"
echo "  - Servidor de datos: http://localhost:3001"
echo "  - Frontend: http://localhost:3000"
echo "  - Worker: https://agent-poc.kvothesson.workers.dev"
echo ""
echo "📚 Más información en README.md"
