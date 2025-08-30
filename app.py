#!/usr/bin/env python3
"""
Chat SaaS PoC Backend
Reemplaza la funcionalidad del Cloudflare Worker con un servidor Flask local
"""

import os
import json
import requests
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from debug_tracker import debug_tracker

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama3-70b-8192')
BUSINESS_JSON_PATH = 'data/business.json'

class BusinessProfile:
    """Clase para manejar el perfil del negocio"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.name = data.get('name')
        self.defaultLocale = data.get('defaultLocale', 'es-AR')
        self.currency = data.get('currency', 'ARS')
        self.tone = data.get('tone', {})
        self.policies = data.get('policies', {})
        self.payments = data.get('payments', {})
        self.catalog = data.get('catalog', [])

def load_business_data() -> BusinessProfile:
    """Carga los datos del negocio desde el archivo JSON"""
    try:
        with open(BUSINESS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return BusinessProfile(data)
    except Exception as e:
        print(f"Error cargando business.json: {e}")
        raise

def format_money(amount: int, locale: str, currency: str) -> str:
    """Formatea el dinero según la localización"""
    try:
        # Simulación simple de formateo de moneda
        if currency == 'ARS':
            return f"${amount:,}"
        elif currency == 'USD':
            return f"${amount:,}"
        else:
            return f"{amount:,} {currency}"
    except:
        return str(amount)

def compute_offers(business: BusinessProfile, locale: str) -> Dict[str, Any]:
    """Calcula las ofertas y descuentos"""
    offers = {}
    
    for product in business.catalog:
        base_price = product.get('price', 0)
        
        # Calcular descuentos
        discounts = []
        for discount in business.payments.get('discounts', []):
            discount_value = int(base_price * (1 - discount['percent'] / 100))
            discounts.append({
                'key': discount['key'],
                'label': discount['label'],
                'value': discount_value,
                'formatted': format_money(discount_value, locale, business.currency)
            })
        
        # Calcular cuotas
        installments = None
        if business.payments.get('installments'):
            inst_data = business.payments['installments']
            count = inst_data.get('count')
            if count and count > 0:
                per_installment = int(base_price / count)
                installments = {
                    'label': inst_data.get('label', ''),
                    'perInstallment': per_installment,
                    'count': count,
                    'formattedEach': format_money(per_installment, locale, business.currency)
                }
        
        offers[product['sku']] = {
            'sku': product['sku'],
            'title': product['title'],
            'base_price': base_price,
            'formatted': {
                'base': format_money(base_price, locale, business.currency),
                'discounts': discounts,
                'installments': installments
            }
        }
    
    return offers

def build_system_prompt(business: BusinessProfile, locale: str, offers: Dict[str, Any]) -> str:
    """Construye el prompt del sistema para Groq"""
    policies = ' '.join(filter(None, [
        business.policies.get('stock'),
        business.policies.get('disclaimer')
    ]))
    
    prompt = f"""Eres un agente comercial del negocio "{business.name}". Habla en {locale}. Tono: {business.tone.get('style', 'amigable')}.

Reglas:
- Usa EXCLUSIVAMENTE la información de catálogo y de ofertas calculadas que te paso. No inventes stock, precios ni tiempos.
- Si falta información clave, pide SOLO un dato adicional de manera breve.
- Formatea como chat amigable estilo WhatsApp, con bullets y emojis moderados. Evita párrafos largos.
- Cuando menciones precios, utiliza los números ya FORMATEADOS provistos y NO recalcules.
- Cierra con: "{business.tone.get('signoff', '¡Gracias!')}". Si hablaste de precios, añade: "{policies}".

CATÁLOGO RELEVANTE (con ofertas):"""
    
    for offer in offers.values():
        prompt += f"\n- {offer['sku']} · {offer['title']}"
        prompt += f"\n  Precio base: {offer['formatted']['base']}"
        
        for discount in offer['formatted']['discounts']:
            prompt += f"\n  • {discount['label']}: {discount['formatted']}"
        
        if offer['formatted']['installments']:
            inst = offer['formatted']['installments']
            prompt += f"\n  • {inst['label']}: {inst['count']} pagos de {inst['formattedEach']}"
    
    return prompt

def detect_locale(message: str, fallback: str = 'es-AR') -> str:
    """Detecta el idioma del mensaje"""
    if not message:
        return fallback
    
    message_lower = message.lower()
    
    # Detectar español
    if any(char in message_lower for char in 'áéíóúñ¡¿'):
        return 'es-AR'
    
    # Palabras clave en español
    spanish_keywords = ['hola', 'gracias', 'buenos', 'buenas', 'consulta', 'precio', 'envío']
    if any(keyword in message_lower for keyword in spanish_keywords):
        return 'es-AR'
    
    # Palabras clave en inglés
    english_keywords = ['hello', 'hi', 'thanks', 'price', 'shipping', 'delivery']
    if any(keyword in message_lower for keyword in english_keywords):
        return 'en-US'
    
    return fallback

def call_groq(system_prompt: str, user_message: str) -> tuple[str, dict]:
    """Llama a la API de Groq y retorna respuesta + info de debug"""
    print(f"🔍 DEBUG: GROQ_API_KEY = {GROQ_API_KEY}")
    print(f"🔍 DEBUG: GROQ_API_KEY type = {type(GROQ_API_KEY)}")
    print(f"🔍 DEBUG: GROQ_API_KEY length = {len(GROQ_API_KEY) if GROQ_API_KEY else 0}")
    
    if not GROQ_API_KEY:
        return "Lo siento, no tengo acceso a la API de Groq en este momento. Por favor, configura tu GROQ_API_KEY.", {}
    
    try:
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.6,
            "max_tokens": 700
        }
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print(f"🔍 DEBUG: Headers enviados = {headers}")
        print(f"🔍 DEBUG: Authorization header = Bearer {GROQ_API_KEY[:10]}..." if GROQ_API_KEY else "None")
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"🔍 DEBUG: Status code = {response.status_code}")
        print(f"🔍 DEBUG: Response headers = {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Tracking de tokens y costos
            usage = data.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            
            # Registrar en el tracker de debug
            debug_tracker.track_request(
                model=GROQ_MODEL,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                request_id=f"chat_{int(time.time())}"
            )
            
            # Preparar info de debug para el frontend
            debug_info = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": debug_tracker._get_model_pricing(GROQ_MODEL)["input"] * (input_tokens / 1_000_000) + 
                           debug_tracker._get_model_pricing(GROQ_MODEL)["output"] * (output_tokens / 1_000_000),
                "model": GROQ_MODEL
            }
            
            return data['choices'][0]['message']['content'], debug_info
        else:
            print(f"🔍 DEBUG: Error response = {response.text}")
            return f"Error en la API de Groq: {response.status_code}", {}
            
    except Exception as e:
        print(f"🔍 DEBUG: Exception = {e}")
        return f"Error comunicándose con Groq: {str(e)}", {}

@app.route('/')
def health_check():
    """Endpoint de salud del servidor"""
    return jsonify({
        "status": "ok",
        "message": "Chat SaaS PoC Backend funcionando",
        "groq_configured": bool(GROQ_API_KEY)
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        locale = data.get('locale')
        business_data = data.get('business')
        
        if not message:
            return jsonify({"error": "Mensaje requerido"}), 400
        
        # Cargar datos del negocio
        if business_data:
            business = BusinessProfile(business_data)
        else:
            business = load_business_data()
        
        # Detectar idioma si no se especifica
        if not locale:
            locale = detect_locale(message, business.defaultLocale)
        
        # Calcular ofertas
        offers = compute_offers(business, locale)
        
        # Construir prompt del sistema
        system_prompt = build_system_prompt(business, locale, offers)
        
        # Llamar a Groq
        reply, debug_info = call_groq(system_prompt, message)
        
        return jsonify({
            "reply": reply,
            "locale": locale,
            "business": business.id,
            "debug_info": debug_info
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/business', methods=['GET'])
def get_business():
    """Endpoint para obtener los datos del negocio"""
    try:
        business = load_business_data()
        return jsonify({
            "id": business.id,
            "name": business.name,
            "defaultLocale": business.defaultLocale,
            "currency": business.currency,
            "tone": business.tone,
            "policies": business.policies,
            "payments": business.payments,
            "catalog": business.catalog
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug/stats', methods=['GET'])
def get_debug_stats():
    """Endpoint para obtener estadísticas de debug"""
    try:
        summary_type = request.args.get('type', 'today')
        
        if summary_type == 'today':
            data = debug_tracker.get_daily_summary()
        elif summary_type == 'month':
            data = debug_tracker.get_monthly_summary()
        elif summary_type == 'total':
            data = debug_tracker.get_total_summary()
        else:
            return jsonify({"error": "Tipo de resumen inválido. Use: today, month, total"}), 400
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug/summary', methods=['GET'])
def print_debug_summary():
    """Endpoint para imprimir resumen de debug en consola"""
    try:
        summary_type = request.args.get('type', 'today')
        debug_tracker.print_summary(summary_type)
        return jsonify({"message": f"Resumen de {summary_type} impreso en consola"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug/usage_log', methods=['GET'])
def get_usage_log():
    """Endpoint para obtener el log detallado de uso"""
    try:
        # Obtener los últimos 100 registros
        recent_logs = debug_tracker.usage_log[-100:] if debug_tracker.usage_log else []
        return jsonify(recent_logs)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug')
def debug_dashboard():
    """Servir el dashboard de debug"""
    try:
        with open('site/debug.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return "Dashboard de debug no encontrado", 404
    except Exception as e:
        return f"Error cargando dashboard: {str(e)}", 500

if __name__ == '__main__':
    print("🚀 Iniciando Chat SaaS PoC Backend...")
    print(f"📊 Modelo Groq: {GROQ_MODEL}")
    print(f"🔑 Groq API Key: {'✅ Configurada' if GROQ_API_KEY else '❌ No configurada'}")
    print(f"📁 Datos del negocio: {BUSINESS_JSON_PATH}")
    print("🌐 Servidor iniciando en http://localhost:5001")
    
    # Mostrar estado del debug tracker
    if debug_tracker.debug_mode:
        print("🔍 DEBUG MODE: Activado - Tracking de tokens y costos habilitado")
        print("📊 Endpoints de debug disponibles:")
        print("   • GET /debug/stats?type=today|month|total")
        print("   • GET /debug/summary?type=today|month|total")
    else:
        print("🔍 DEBUG MODE: Desactivado - Para activar, set GROQ_DEBUG=true")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
