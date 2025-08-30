# 🚀 Quick Start - Commercial Agent PoC

Get your AI commercial agent running in 5 minutes!

## Prerequisites

- [Groq API Key](https://console.groq.com/) (free tier available)
- [Cloudflare Account](https://dash.cloudflare.com/) (free)
- Node.js 18+ installed

## ⚡ 5-Minute Setup

### 1. Clone & Setup
```bash
git clone <your-repo>
cd chat-saas-poc
```

### 2. Deploy Worker (Auto)
```bash
./deploy.sh
```

**Or manually:**
```bash
cd worker
npm install
npm run deploy
```

### 3. Configure API Key
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Workers & Pages → Find your worker
3. Settings → Variables → Add Variable
4. **Name:** `GROQ_API_KEY` | **Value:** Your Groq API key | **Type:** Secret

### 4. Update Frontend
In `site/app.js`, change:
```js
const API_BASE = "https://YOUR_WORKER_NAME.workers.dev";
```

### 5. Deploy Frontend
Upload `site/` folder to:
- GitHub Pages (recommended)
- Netlify
- Vercel
- Any static hosting

## 🧪 Test It!

Open your deployed site and try:

**Spanish:**
```
"Me mostrás anillos solitarios en oro amarillo?"
```

**English:**
```
"Can you show me men's rings under 700k?"
```

**Policies:**
```
"¿Cuánto tardan las entregas?"
```

## 🔧 Customize Business

Edit `data/business.json` or create new ones for:
- Different industries
- Multiple locations
- Various payment methods

## 📊 What You Get

- ✅ AI agent that talks like a human salesperson
- ✅ Automatic price calculations (discounts, installments)
- ✅ Multi-language support (Spanish/English)
- ✅ WhatsApp-style chat interface
- ✅ 100% free infrastructure
- ✅ Only pay for Groq API calls (~$0.05 per 1M tokens)

## 🆘 Need Help?

- Check [README.md](README.md) for detailed docs
- Open an issue for bugs
- The agent only uses catalog data (no hallucinations!)

---

**Ready to sell?** Your AI agent is live! 🎉
