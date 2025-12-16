# Orakulum Onboarding - Quick Start Guide

**Rychlý start pro lokální testování onboardingu za méně než 5 minut.**

## 🚀 1-Krok Start (Automatický)

```bash
./start_onboarding.sh
```

Otevřete prohlížeč: http://localhost:8000/onboarding_demo.html

**To je vše!** 🎉

---

## 📋 Manuální Start (pokud preferujete)

### Krok 1: Konfigurace

```bash
# Zkopírujte .env.example na .env
cp .env.example .env

# Vyplňte vaše Supabase credentials
nano .env
```

Minimální konfigurace:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here
```

### Krok 2: Instalace závislostí

```bash
pip install -r requirements.txt
```

### Krok 3: Spuštění API serveru

V prvním terminálu:
```bash
python3 api_onboarding.py
```

### Krok 4: Spuštění frontend serveru

V druhém terminálu:
```bash
python3 -m http.server 8000
```

### Krok 5: Otevřít v prohlížeči

```
http://localhost:8000/onboarding_demo.html
```

---

## ✅ Ověření, že vše funguje

### Test 1: API Health Check

```bash
curl http://localhost:5000/api/health
```

Očekávaný výstup:
```json
{
  "status": "healthy",
  "service": "orakulum-onboarding-api"
}
```

### Test 2: Automatické API testy

```bash
python3 test_onboarding_api.py
```

Měli byste vidět:
```
✅ Health Check: PASS
✅ Create Lead: PASS
✅ Get Lead: PASS
✅ Validation: PASS

🎉 All tests passed!
```

---

## 🎯 Co dělat po spuštění

1. **Projděte onboarding flow**
   - Vyberte možnosti v každém kroku
   - Sledujte Live Activity Panel (rotace každých 6-8s)
   - Všimněte si progress baru

2. **Otestujte validace**
   - Zkuste poslat formulář s chybějícími údaji
   - Zkuste neplatný email
   - Zkuste krátký popis (méně než 20 znaků)

3. **Sledujte loading screen**
   - Po submitu uvidíte animovaný loading
   - Rotující kroky procesování
   - Minimálně 8 sekund pro "perceived value"

4. **Zkontrolujte data v Supabase**
   - Přihlaste se do Supabase Dashboard
   - Otevřete tabulku `junior_leads`
   - Najděte nově vytvořený lead se statusem `FLAGGED`

---

## 📊 Struktura dat v Supabase

Po submitu uvidíte v `junior_leads`:

```json
{
  "id": "uuid-here",
  "name": "Jan Novák",
  "email": "jan@example.com",
  "description": "Full text description with all answers",
  "status": "FLAGGED",
  "input_transform": {
    "obor": "Frontend Development",
    "seniorita": "Začátečník",
    "hlavni_cil": "První práce v IT",
    "casovy_horizont": "6 měsíců",
    "technologie": [],
    "raw_description": "Original user input"
  },
  "plan": null,
  "created_at": "2025-12-16T..."
}
```

---

## 🔧 Troubleshooting

### Problém: API nereaguje

**Řešení:**
```bash
# Zkontrolujte, že běží na portu 5000
lsof -i :5000

# Pokud ne, restartujte
python3 api_onboarding.py
```

### Problém: CORS error v browseru

**Řešení:**
Ujistěte se, že:
1. API běží na `localhost:5000`
2. Frontend běží na `localhost:8000`
3. V `.env` je `CORS_ORIGINS=*`

### Problém: Supabase connection error

**Řešení:**
1. Zkontrolujte `.env` credentials
2. Ověřte že máte Supabase projekt vytvořený
3. Zkontrolujte že tabulka `junior_leads` existuje
4. Spusťte: `python3 -c "from pipeline.db import get_client; print(get_client())"`

### Problém: Live Activity Panel se nerotuje

**Řešení:**
1. Otevřete browser console (F12)
2. Zkontrolujte JavaScript errory
3. Obnovte stránku (Ctrl+R)
4. Vypněte browser extensions (ad-blockers)

---

## 🎨 Customizace

### Změna API endpointu

V `onboarding_demo.html`:
```javascript
window.ORAKULUM_API_ENDPOINT = 'https://your-api.com/api/leads';
```

### Změna success redirect URL

```javascript
window.ORAKULUM_SUCCESS_URL = 'https://your-app.com/dashboard';
```

### Změna Live Activity textu

V `onboarding.js`, editujte `ACTIVITY_DATA`:
```javascript
const ACTIVITY_DATA = [
    { avatar: '👨‍💻', role: 'Your Role', action: 'your action' },
    // ... přidejte další
];
```

### Změna Loading steps

V `onboarding.js`, editujte `LOADING_STEPS`:
```javascript
const LOADING_STEPS = [
    'Your step 1',
    'Your step 2',
    // ...
];
```

---

## 📱 Testování na mobilu

### Local Network Access

1. Zjistěte vaši IP adresu:
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Výsledek např: 192.168.1.100
```

2. Upravte API endpoint v `onboarding_demo.html`:
```javascript
window.ORAKULUM_API_ENDPOINT = 'http://192.168.1.100:5000/api/leads';
```

3. Na mobilu otevřete:
```
http://192.168.1.100:8000/onboarding_demo.html
```

---

## 🚀 Production Deployment

### Frontend (Vercel/Netlify)

1. Upload soubory:
   - `onboarding.html` (nebo přejmenujte na `index.html`)
   - `onboarding.css`
   - `onboarding.js`
   - `success.html`

2. Nastavte build settings:
   - Build Command: (none)
   - Publish Directory: `/`

3. Environment variables:
   ```
   ORAKULUM_API_ENDPOINT=https://your-api.com/api/leads
   ORAKULUM_SUCCESS_URL=https://your-app.com/dashboard
   ```

### Backend (Heroku/Railway)

1. Vytvořte `Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT api_onboarding:app
```

2. Deploy:
```bash
git add .
git commit -m "Add onboarding API"
git push heroku main
```

3. Nastavte environment variables v hosting platformě

---

## 📚 Další kroky

1. **Přečtěte plnou dokumentaci**: `ONBOARDING_README.md`
2. **Prozkoumejte pipeline**: `PIPELINE_SOLUTION.md`
3. **Customizujte design**: Editujte CSS variables v `onboarding.css`
4. **Přidejte analytics**: Viz sekce Analytics v dokumentaci

---

## 🆘 Podpora

- 📖 Plná dokumentace: `ONBOARDING_README.md`
- 🧪 Test API: `python3 test_onboarding_api.py`
- 🐛 Problém s pipeline: `PIPELINE_SOLUTION.md`
- 💬 Obecné dotazy: Otevřete issue v repozitáři

---

**Vytvořeno**: 2025-12-16  
**Verze**: 1.0.0
