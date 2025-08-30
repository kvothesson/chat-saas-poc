const API_BASE = "https://agent-poc.kvothesson.workers.dev"; // ← URL del Worker deployado

const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');

const business = { // opcional: sobreescribir el perfil por request
  id: 'ring-jewelers',
  name: 'Ring Jewelers',
  defaultLocale: 'es-AR',
  currency: 'ARS',
  tone: { style: 'cálido, cercano, vendedor experto, emojis moderados', signoff: '¡Quedo atento a cualquier consulta!' },
  policies: { delivery: 'Entregas en 3 a 7 días hábiles.', returns: 'Cambios dentro de 10 días con ticket.', disclaimer: 'Precios sujetos a actualización.', stock: 'Stock sujeto a confirmación.' },
  payments: {
    discounts: [
      { label: '15% descuento en efectivo', percent: 15, key: 'cash' },
      { label: '10% descuento por transferencia', percent: 10, key: 'bank' }
    ],
    installments: { count: 3, noInterest: true, label: '3 pagos sin interés con tarjeta bancaria' }
  },
  catalog: [
    { sku: 'A', title: 'Cintillo Oro Blanco 18k con zafiros y circones', price: 633800, weight_g: 1.7 },
    { sku: 'B', title: 'Cintillo Oro Blanco 18k, 5 circones', price: 720000, weight_g: 2.7 },
    { sku: 'C', title: 'Cintillo Oro Blanco 18k con circones pequeños', price: 520000, weight_g: 1.9 }
  ]
};

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

addMsg('¡Hola! Soy tu asesor virtual. ¿Qué estás buscando hoy? 😊', 'bot');
