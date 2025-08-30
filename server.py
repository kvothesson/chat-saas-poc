#!/usr/bin/env python3
"""
Servidor local simple para desarrollo - reemplaza al Cloudflare Worker
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

# Configuración
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama3-70b-8192')
PORT = 8001

class ChatHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(b'Local Chat Server OK')
        else:
            self.send_error(404)
    
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Content-Type', 'application/json')
    
    def handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            business = data.get('business', {})
            
            # Generar respuesta usando Groq
            reply = self.call_groq(message, business)
            
            response = {
                'reply': reply,
                'locale': 'es-AR',
                'business': business.get('id', 'local')
            }
            
            self.send_response(200)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {'error': str(e)}
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def call_groq(self, message, business):
        """Llamar a la API de Groq"""
        if GROQ_API_KEY == 'your-groq-api-key-here':
            return f"⚠️ Configura GROQ_API_KEY en las variables de entorno para usar IA real. Mensaje: {message}"
        
        try:
            system_prompt = self.build_system_prompt(business)
            
            payload = {
                'model': GROQ_MODEL,
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ],
                'temperature': 0.6,
                'max_tokens': 700
            }
            
            headers = {
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                return f"Error en Groq API: {response.status_code}"
                
        except Exception as e:
            return f"Error llamando a Groq: {str(e)}"
    
    def build_system_prompt(self, business):
        """Construir el prompt del sistema"""
        return f"""Eres un agente comercial del negocio "{business.get('name', 'Local Business')}". 
Habla en español argentino. Tono: cálido, cercano, vendedor experto, emojis moderados.

Reglas:
- Usa EXCLUSIVAMENTE la información del negocio que te paso
- Formatea como chat amigable estilo WhatsApp
- Cierra con: "¡Quedo atento a cualquier consulta!"
- Si no tienes información específica, pide más detalles

Información del negocio: {json.dumps(business, indent=2)}"""

if __name__ == '__main__':
    print(f"🚀 Servidor local iniciando en puerto {PORT}")
    print(f"📱 Frontend: http://localhost:8000/site/")
    print(f"🔧 API: http://localhost:{PORT}")
    print(f"⚠️  Configura GROQ_API_KEY para usar IA real")
    
    server = HTTPServer(('localhost', PORT), ChatHandler)
    print(f"✅ Servidor corriendo en http://localhost:{PORT}")
    print("Presiona Ctrl+C para detener")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
        server.server_close()
