#!/usr/bin/env python3
"""
Debug Tracker para Groq API
Monitorea tokens, costos y uso acumulado
"""

import os
import json
import time
from datetime import datetime, date
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TokenUsage:
    """Estructura para tracking de tokens"""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    timestamp: str = ""
    model: str = ""
    request_id: str = ""

@dataclass
class DailyStats:
    """Estadísticas diarias"""
    date: str = ""
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_usd: float = 0.0
    models_used: Dict[str, int] = None

class GroqDebugTracker:
    """Tracker principal para debug de Groq API"""
    
    def __init__(self, debug_mode: bool = False, save_to_file: bool = True):
        self.debug_mode = debug_mode
        self.save_to_file = save_to_file
        self.daily_stats_file = "debug_data/daily_stats.json"
        self.usage_log_file = "debug_data/usage_log.json"
        
        # Precios por millón de tokens (USD) - basado en Groq pricing
        self.pricing = {
            "llama3-70b-8192": {"input": 0.59, "output": 0.79},
            "llama3-8b-8192": {"input": 0.05, "output": 0.08},
            "llama3.1-8b-instant": {"input": 0.05, "output": 0.08},
            "llama3.3-70b-versatile": {"input": 0.59, "output": 0.79},
            "qwen3-32b": {"input": 0.29, "output": 0.59},
            "gemma2-9b": {"input": 0.20, "output": 0.20},
            "gpt-oss-20b": {"input": 0.10, "output": 0.50},
            "gpt-oss-120b": {"input": 0.15, "output": 0.75},
            "kimi-k2-1t": {"input": 1.00, "output": 3.00},
            "llama4-scout": {"input": 0.11, "output": 0.34},
            "llama4-maverick": {"input": 0.20, "output": 0.60},
            "llama-guard-4": {"input": 0.20, "output": 0.20},
            "deepseek-r1": {"input": 0.75, "output": 0.99},
            "mistral-saba": {"input": 0.79, "output": 0.79},
            "llama-guard-3": {"input": 0.20, "output": 0.20}
        }
        
        # Crear directorio de debug si no existe
        Path("debug_data").mkdir(exist_ok=True)
        
        # Cargar estadísticas existentes
        self.daily_stats = self._load_daily_stats()
        self.usage_log = self._load_usage_log()
        
        if self.debug_mode:
            print("🔍 DEBUG MODE ACTIVADO - GroqDebugTracker iniciado")
    
    def _load_daily_stats(self) -> Dict[str, DailyStats]:
        """Carga estadísticas diarias desde archivo"""
        try:
            if os.path.exists(self.daily_stats_file):
                with open(self.daily_stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {date: DailyStats(**stats) for date, stats in data.items()}
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Error cargando daily stats: {e}")
        return {}
    
    def _load_usage_log(self) -> list:
        """Carga log de uso desde archivo"""
        try:
            if os.path.exists(self.usage_log_file):
                with open(self.usage_log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Error cargando usage log: {e}")
        return []
    
    def _save_daily_stats(self):
        """Guarda estadísticas diarias a archivo"""
        if not self.save_to_file:
            return
            
        try:
            with open(self.daily_stats_file, 'w', encoding='utf-8') as f:
                json.dump({date: asdict(stats) for date, stats in self.daily_stats.items()}, 
                         f, indent=2, ensure_ascii=False)
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Error guardando daily stats: {e}")
    
    def _save_usage_log(self):
        """Guarda log de uso a archivo"""
        if not self.save_to_file:
            return
            
        try:
            with open(self.usage_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️ Error guardando usage log: {e}")
    
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Obtiene precios para un modelo específico"""
        # Normalizar nombre del modelo
        model_lower = model.lower().replace('-', '').replace('_', '')
        
        for key, prices in self.pricing.items():
            if model_lower in key.lower().replace('-', '').replace('_', ''):
                return prices
        
        # Default pricing si no se encuentra
        return {"input": 0.50, "output": 0.50}
    
    def track_request(self, model: str, input_tokens: int, output_tokens: int, 
                     request_id: str = None) -> TokenUsage:
        """Registra una nueva solicitud a Groq"""
        if not self.debug_mode:
            return TokenUsage()
        
        # Calcular costo
        pricing = self._get_model_pricing(model)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Crear registro de uso
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=total_cost,
            timestamp=datetime.now().isoformat(),
            model=model,
            request_id=request_id or f"req_{int(time.time())}"
        )
        
        # Actualizar estadísticas diarias
        today = date.today().isoformat()
        if today not in self.daily_stats:
            self.daily_stats[today] = DailyStats(
                date=today,
                models_used={}
            )
        
        daily = self.daily_stats[today]
        daily.total_requests += 1
        daily.total_input_tokens += input_tokens
        daily.total_output_tokens += output_tokens
        daily.total_cost_usd += total_cost
        
        if model not in daily.models_used:
            daily.models_used[model] = 0
        daily.models_used[model] += 1
        
        # Agregar al log
        self.usage_log.append(asdict(usage))
        
        # Guardar datos
        self._save_daily_stats()
        self._save_usage_log()
        
        if self.debug_mode:
            print(f"🔍 TRACKED: {model} | Input: {input_tokens:,} | Output: {output_tokens:,} | Cost: ${total_cost:.6f}")
        
        return usage
    
    def get_daily_summary(self, target_date: str = None) -> Dict[str, Any]:
        """Obtiene resumen de un día específico"""
        if not target_date:
            target_date = date.today().isoformat()
        
        if target_date not in self.daily_stats:
            return {"error": "No hay datos para esa fecha"}
        
        daily = self.daily_stats[target_date]
        return {
            "date": daily.date,
            "total_requests": daily.total_requests,
            "total_input_tokens": daily.total_input_tokens,
            "total_output_tokens": daily.total_output_tokens,
            "total_cost_usd": daily.total_cost_usd,
            "models_used": daily.models_used,
            "formatted": {
                "input_tokens": f"{daily.total_input_tokens:,}",
                "output_tokens": f"{daily.total_output_tokens:,}",
                "total_tokens": f"{daily.total_input_tokens + daily.total_output_tokens:,}",
                "cost_usd": f"${daily.total_cost_usd:.6f}"
            }
        }
    
    def get_monthly_summary(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Obtiene resumen mensual"""
        if not year:
            year = date.today().year
        if not month:
            month = date.today().month
        
        month_str = f"{year:04d}-{month:02d}"
        
        monthly_data = {
            "year": year,
            "month": month,
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "models_used": {},
            "daily_breakdown": {}
        }
        
        for date_str, daily in self.daily_stats.items():
            if date_str.startswith(month_str):
                monthly_data["total_requests"] += daily.total_requests
                monthly_data["total_input_tokens"] += daily.total_input_tokens
                monthly_data["total_output_tokens"] += daily.total_output_tokens
                monthly_data["total_cost_usd"] += daily.total_cost_usd
                monthly_data["daily_breakdown"][date_str] = asdict(daily)
                
                for model, count in daily.models_used.items():
                    if model not in monthly_data["models_used"]:
                        monthly_data["models_used"][model] = 0
                    monthly_data["models_used"][model] += count
        
        # Agregar formato
        monthly_data["formatted"] = {
            "input_tokens": f"{monthly_data['total_input_tokens']:,}",
            "output_tokens": f"{monthly_data['total_output_tokens']:,}",
            "total_tokens": f"{monthly_data['total_input_tokens'] + monthly_data['total_output_tokens']:,}",
            "cost_usd": f"${monthly_data['total_cost_usd']:.6f}"
        }
        
        return monthly_data
    
    def get_total_summary(self) -> Dict[str, Any]:
        """Obtiene resumen total de todo el tiempo"""
        total_data = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "models_used": {},
            "days_active": len(self.daily_stats),
            "first_request": None,
            "last_request": None
        }
        
        dates = sorted(self.daily_stats.keys())
        if dates:
            total_data["first_request"] = dates[0]
            total_data["last_request"] = dates[-1]
        
        for daily in self.daily_stats.values():
            total_data["total_requests"] += daily.total_requests
            total_data["total_input_tokens"] += daily.total_input_tokens
            total_data["total_output_tokens"] += daily.total_output_tokens
            total_data["total_cost_usd"] += daily.total_cost_usd
            
            for model, count in daily.models_used.items():
                if model not in total_data["models_used"]:
                    total_data["models_used"][model] = 0
                total_data["models_used"][model] += count
        
        # Agregar formato
        total_data["formatted"] = {
            "input_tokens": f"{total_data['total_input_tokens']:,}",
            "output_tokens": f"{total_data['total_output_tokens']:,}",
            "total_tokens": f"{total_data['total_input_tokens'] + total_data['total_output_tokens']:,}",
            "cost_usd": f"${total_data['total_cost_usd']:.6f}"
        }
        
        return total_data
    
    def print_summary(self, summary_type: str = "today"):
        """Imprime un resumen en consola"""
        if not self.debug_mode:
            return
        
        print("\n" + "="*60)
        print("🔍 GROQ DEBUG TRACKER - RESUMEN")
        print("="*60)
        
        if summary_type == "today":
            data = self.get_daily_summary()
            print(f"📅 Fecha: {data.get('date', 'Hoy')}")
        elif summary_type == "month":
            data = self.get_monthly_summary()
            print(f"📅 Mes: {data.get('year')}-{data.get('month'):02d}")
        else:
            data = self.get_total_summary()
            print("📅 Período: Total")
        
        if "error" in data:
            print(f"❌ {data['error']}")
            return
        
        print(f"📊 Total Requests: {data['total_requests']:,}")
        print(f"🔤 Input Tokens: {data['formatted']['input_tokens']}")
        print(f"📝 Output Tokens: {data['formatted']['output_tokens']}")
        print(f"💎 Total Tokens: {data['formatted']['total_tokens']}")
        print(f"💰 Costo Total: {data['formatted']['cost_usd']}")
        
        if data.get('models_used'):
            print("\n🤖 Modelos utilizados:")
            for model, count in data['models_used'].items():
                print(f"   • {model}: {count} requests")
        
        print("="*60 + "\n")

# Instancia global del tracker
debug_tracker = GroqDebugTracker(
    debug_mode=os.getenv('GROQ_DEBUG', 'false').lower() == 'true',
    save_to_file=os.getenv('GROQ_SAVE_DEBUG', 'true').lower() == 'true'
)
