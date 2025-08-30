#!/bin/bash

echo "🚀 Deploying Commercial Agent PoC..."
echo "====================================="

# Check if we're in the right directory
if [ ! -f "worker/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Deploy Cloudflare Worker
echo "📦 Deploying Cloudflare Worker..."
cd worker

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
fi

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📥 Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Deploy the worker
echo "🚀 Deploying to Cloudflare..."
npm run deploy

if [ $? -eq 0 ]; then
    echo "✅ Worker deployed successfully!"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Go to Cloudflare Dashboard → Workers & Pages"
    echo "2. Find your worker and go to Settings → Variables"
    echo "3. Add GROQ_API_KEY (secret) with your Groq API key"
    echo "4. Optionally add GROQ_MODEL and BUSINESS_JSON_URL"
    echo ""
    echo "🌐 Your worker URL: https://$(grep 'name =' wrangler.toml | cut -d'"' -f2).workers.dev"
else
    echo "❌ Worker deployment failed!"
    exit 1
fi

cd ..

# Frontend deployment instructions
echo ""
echo "🌐 Frontend Deployment:"
echo "1. Update site/app.js with your worker URL:"
echo "   const API_BASE = \"https://$(grep 'name =' worker/wrangler.toml | cut -d'"' -f2).workers.dev\";"
echo ""
echo "2. Deploy the site/ folder to GitHub Pages or any static hosting"
echo "   - Option 1: Push to GitHub and enable Pages in repo settings"
echo "   - Option 2: Upload to Netlify, Vercel, or similar"
echo ""
echo "🎯 Test your agent with:"
echo "   \"Me mostrás anillos solitarios en oro amarillo?\""
echo "   \"Can you show me men's rings under 700k?\""
echo "   \"¿Cuánto tardan las entregas?\""

echo ""
echo "✨ Commercial Agent PoC is ready to use!"
