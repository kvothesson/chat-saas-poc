#!/usr/bin/env python3
"""
Test script para probar la API de Groq directamente
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_groq_api():
    """Prueba la API de Groq directamente"""
    
    # Obtener la API key
    api_key = os.getenv('GROQ_API_KEY')
    model = os.getenv('GROQ_MODEL', 'llama3-70b-8192')
    
    print(f"🔑 API Key: {api_key[:10]}..." if api_key else "❌ No API key")
    print(f"📊 Modelo: {model}")
    print()
    
    if not api_key:
        print("❌ No hay API key configurada")
        return
    
    # Payload de prueba simple
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ],
        "temperature": 0.6,
        "max_tokens": 100
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Probando llamada a Groq...")
    print(f"📡 URL: https://api.groq.com/openai/v1/chat/completions")
    print(f"🔑 Headers: {headers}")
    print(f"📦 Payload: {payload}")
    print()
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(f"📝 Respuesta: {data['choices'][0]['message']['content']}")
        else:
            print(f"❌ Error {response.status_code}:")
            print(f"📝 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en la llamada: {e}")

if __name__ == "__main__":
    test_groq_api()
