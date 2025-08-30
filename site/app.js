const API_BASE = "http://localhost:8001"; // ← Servidor local para desarrollo

const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');

let business = null; // Se cargará desde business.json

const history = [];

function addMsg(text, who) {
  const div = document.createElement('div');
  div.className = 'msg ' + (who === 'user' ? 'user' : 'bot');
  div.textContent = text;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function loadBusinessProfile() {
  try {
    const response = await fetch('./data/business.json');
    business = await response.json();
    console.log('Perfil de negocio cargado:', business);
  } catch (error) {
    console.error('Error cargando perfil de negocio:', error);
    // Fallback mínimo en caso de error
    business = {
      id: 'ring-jewelers',
      name: 'Ring Jewelers',
      defaultLocale: 'es-AR',
      currency: 'ARS'
    };
  }
}

async function send() {
  const text = inputEl.value.trim();
  if (!text) return;
  
  if (!business) {
    addMsg('Cargando perfil de negocio...', 'bot');
    await loadBusinessProfile();
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

// Cargar perfil al iniciar
loadBusinessProfile().then(() => {
  addMsg('¡Hola! Soy tu asesor virtual. ¿Qué estás buscando hoy? 😊', 'bot');
});
