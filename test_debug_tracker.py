#!/usr/bin/env python3
"""
Script de prueba para el Debug Tracker de Groq
"""

import os
from dotenv import load_dotenv
from debug_tracker import debug_tracker

# Cargar variables de entorno
load_dotenv()

def test_debug_tracker():
    """Prueba las funcionalidades del debug tracker"""
    
    print("🧪 Probando Debug Tracker de Groq")
    print("=" * 50)
    
    # Verificar configuración
    print(f"🔍 Debug Mode: {debug_tracker.debug_mode}")
    print(f"💾 Save to File: {debug_tracker.save_to_file}")
    print()
    
    if not debug_tracker.debug_mode:
        print("⚠️ Debug mode no está activado. Para activarlo:")
        print("   export GROQ_DEBUG=true")
        print("   o crear archivo .env con GROQ_DEBUG=true")
        print()
        return
    
    # Simular algunas solicitudes
    print("📊 Simulando solicitudes a Groq...")
    
    # Solicitud 1
    usage1 = debug_tracker.track_request(
        model="llama3-70b-8192",
        input_tokens=1500,
        output_tokens=800,
        request_id="test_001"
    )
    
    # Solicitud 2
    usage2 = debug_tracker.track_request(
        model="llama3-8b-8192",
        input_tokens=800,
        output_tokens=400,
        request_id="test_002"
    )
    
    # Solicitud 3
    usage3 = debug_tracker.track_request(
        model="llama3-70b-8192",
        input_tokens=2000,
        output_tokens=1200,
        request_id="test_003"
    )
    
    print("\n✅ Solicitudes simuladas registradas")
    print()
    
    # Mostrar resúmenes
    print("📈 RESUMEN DEL DÍA:")
    debug_tracker.print_summary("today")
    
    print("📈 RESUMEN TOTAL:")
    debug_tracker.print_summary("total")
    
    # Mostrar datos en formato JSON
    print("📊 DATOS DEL DÍA (JSON):")
    daily_data = debug_tracker.get_daily_summary()
    import json
    print(json.dumps(daily_data, indent=2, ensure_ascii=False))
    
    print("\n🎯 Prueba completada!")
    print("💡 Puedes ver los datos guardados en el directorio 'debug_data/'")

if __name__ == "__main__":
    test_debug_tracker()
