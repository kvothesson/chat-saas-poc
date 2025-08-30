const API_BASE = "https://agent-poc.kvothesson.workers.dev"; // ← URL del Worker deployado

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
    business = await response.json();
  } catch (error) {
    console.error('Error cargando business.json:', error);
    // Fallback con datos mínimos si falla la carga
    business = {
      id: 'ring-jewelers',
      name: 'Ring Jewelers',
      defaultLocale: 'es-AR',
      currency: 'ARS'
    };
  }
}

const history = [];

function addMsg(text, who) {
  const div = document.createElement('div');
  div.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function send() {
  const text = inputEl.value.trim();
  if (!text) return;
  
  // Asegurar que business esté cargado antes de enviar
  if (!business) {
    await loadBusiness();
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
    if (data.reply) addMsg(data.reply, 'bot');
    else addMsg('Ups, no pude responder ahora 😅', 'bot');
  } catch (e) {
    addMsg('Error de red: ' + e.message, 'bot');
  }
}

sendBtn.addEventListener('click', send);
inputEl.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

// Cargar business al inicializar
loadBusiness().then(() => {
  addMsg('¡Hola! Soy tu asesor virtual. ¿Qué estás buscando hoy? 😊', 'bot');
});
