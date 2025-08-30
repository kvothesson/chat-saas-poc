const API_BASE = "http://localhost:5001"; // Backend Python local

const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');

let business = null; // se cargará desde el archivo JSON

// Función para cargar la información del negocio
async function loadBusiness() {
  try {
    // En desarrollo, usar el servidor local; en producción, usar la URL configurada
    const isDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const businessUrl = isDev ? 'http://localhost:3001/business.json' : '../data/business.json';
    
    const response = await fetch(businessUrl);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    business = await response.json();
    console.log('✅ Datos del negocio cargados exitosamente:', business.name);
  } catch (error) {
    console.error('❌ Error cargando business.json:', error);
    // No usar datos hardcodeados - mostrar error al usuario
    business = null;
    addMsg('⚠️ Error: No se pudieron cargar los datos del negocio. Por favor, recarga la página o contacta al administrador.', 'bot');
  }
}

const history = [];

function addMsg(text, who, debugInfo = null) {
  const div = document.createElement('div');
  div.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
  
  // Si es un mensaje del bot y hay info de debug, mostrarla
  if (who === 'bot' && debugInfo) {
    div.innerHTML = `
      <div class="message-content">${text}</div>
      <div class="debug-info">
        <span class="debug-label">🔍 Debug:</span>
        <span class="debug-tokens">Input: ${debugInfo.input_tokens?.toLocaleString() || '0'}</span>
        <span class="debug-tokens">Output: ${debugInfo.output_tokens?.toLocaleString() || '0'}</span>
        <span class="debug-cost">Costo: $${debugInfo.cost_usd?.toFixed(6) || '0.000000'}</span>
        <span class="debug-model">Modelo: ${debugInfo.model || 'N/A'}</span>
      </div>
    `;
  } else {
    div.textContent = text;
  }
  
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function send() {
  const text = inputEl.value.trim();
  if (!text) return;
  
  // Verificar que business esté cargado antes de enviar
  if (!business) {
    addMsg('⏳ Cargando datos del negocio...', 'bot');
    await loadBusiness();
    
    // Si después de intentar cargar sigue siendo null, no continuar
    if (!business) {
      addMsg('❌ No se pueden enviar mensajes sin los datos del negocio. Por favor, recarga la página.', 'bot');
      return;
    }
  }
  
  addMsg(text, 'user');
  inputEl.value = '';
  
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text, business })
    });
    const data = await res.json();
    
    if (data.reply) {
      // Obtener información de debug si está disponible
      let debugInfo = null;
      if (data.debug_info) {
        debugInfo = data.debug_info;
      } else {
        // Si no hay debug_info en la respuesta, intentar obtenerla del último request
        try {
          const debugRes = await fetch(`${API_BASE}/debug/stats?type=today`);
          if (debugRes.ok) {
            const debugData = await debugRes.json();
            if (debugData.total_requests > 0) {
              // Calcular info del último request
              const lastRequest = {
                input_tokens: debugData.total_input_tokens,
                output_tokens: debugData.total_output_tokens,
                cost_usd: debugData.total_cost_usd,
                model: data.model || 'N/A'
              };
              debugInfo = lastRequest;
            }
          }
        } catch (debugError) {
          console.log('Debug info no disponible:', debugError);
        }
      }
      
      addMsg(data.reply, 'bot', debugInfo);
      // Actualizar panel de estadísticas
      updateStatsPanel();
    } else {
      addMsg('Ups, no pude responder ahora 😅', 'bot');
    }
  } catch (e) {
    addMsg('Error de red: ' + e.message, 'bot');
  }
}

sendBtn.addEventListener('click', send);
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

// Función para actualizar el panel de estadísticas
async function updateStatsPanel() {
  try {
    const response = await fetch(`${API_BASE}/debug/stats?type=today`);
    if (response.ok) {
      const data = await response.json();
      if (data.total_requests > 0) {
        const statsPanel = document.getElementById('stats-panel');
        if (statsPanel) {
          statsPanel.innerHTML = `
            <div class="stats-item">
              <span class="stats-label">📊 Requests:</span>
              <span class="stats-value">${data.total_requests}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">🔤 Input:</span>
              <span class="stats-value">${data.total_input_tokens?.toLocaleString() || '0'}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">📝 Output:</span>
              <span class="stats-value">${data.total_output_tokens?.toLocaleString() || '0'}</span>
            </div>
            <div class="stats-item">
              <span class="stats-label">💰 Costo:</span>
              <span class="stats-value">$${data.total_cost_usd?.toFixed(6) || '0.000000'}</span>
            </div>
          `;
        }
      }
    }
  } catch (error) {
    console.log('Error actualizando estadísticas:', error);
  }
}

// Cargar business al inicializar
loadBusiness().then(() => {
  addMsg('¡Hola! Soy tu asesor virtual. ¿Qué estás buscando hoy? 😊', 'bot');
  // Actualizar panel de estadísticas
  updateStatsPanel();
});
