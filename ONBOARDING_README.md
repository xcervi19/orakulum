# Orakulum Onboarding

Moderní, fullscreen onboarding s "live activity" panelem navržený pro vysokou konverzi a vytvoření pocitu živého systému.

## 🎯 Přehled

Onboarding vede uživatele přes 7 kroků:

0. **Intro** - Úvodní obrazovka s CTA
1. **Cíl** - Výběr hlavního kariérního cíle
2. **Oblast** - Výběr IT oblasti (frontend, backend, atc.)
3. **Úroveň** - Určení současné úrovně znalostí
4. **Konkrétnost** - Popis situace volným textem
5. **Časový horizont** - Výběr časového rámce
6. **Email + Submit** - Kontaktní údaje a odeslání

## 🚀 Klíčové funkce

### Live Activity Panel
- **Pasivní, neklikatelný** - pouze vizuální signál
- **Rotace každých 6-8s** - automatická výměna položek
- **Statická data** - žádné API volání
- **Obsahuje**: avatar, role, krátká akce

Příklady aktivit:
- "Backend Engineer dokončil osobní plán"
- "Interview Readiness Score +6"
- "Frontend Developer zahájil trénink"

### Progress Bar
- Ukazuje pokrok celým flow
- Smooth transitions
- Responzivní design

### Loading Screen
- Zobrazí se po submitu formuláře
- Rotující kroky s 2s intervalem:
  - "Analyzujeme váš cíl"
  - "Mapujeme příležitosti"
  - "Vytváříme personalizovaný plán"
  - "Připravujeme váš osobní prostor"
  - "Finalizujeme detaily"
- Minimálně 8 sekund pro perceived value

### Animace & Transitions
- Smooth step transitions
- Fade in/out efekty
- Hover states na všech interaktivních prvcích
- Respektuje `prefers-reduced-motion`

## 📁 Struktura souborů

```
/workspace/
├── onboarding.html       # HTML struktura
├── onboarding.css        # Styling & design system
├── onboarding.js         # Logika, validace, API calls
├── api_onboarding.py     # Flask API endpoint
└── ONBOARDING_README.md  # Tato dokumentace
```

## 🔧 Instalace & Spuštění

### 1. Nainstalovat závislosti

```bash
pip install -r requirements.txt
```

### 2. Konfigurovat environment

Zkopírujte `.env.example` na `.env` a vyplňte hodnoty:

```bash
cp .env.example .env
```

Minimální konfigurace:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
API_PORT=5000
```

### 3. Spustit API server

```bash
python3 api_onboarding.py
```

API běží na `http://localhost:5000`

### 4. Otevřít onboarding

Otevřete `onboarding.html` v prohlížeči nebo nasaďte na webový server.

**Pro development s live reload:**
```bash
# Použijte jednoduchý HTTP server
python3 -m http.server 8000
# Otevřete http://localhost:8000/onboarding.html
```

## 🔌 API Endpoints

### POST /api/leads
Vytvoří nový lead z onboarding formuláře.

**Request:**
```json
{
  "name": "Jan Novák",
  "email": "jan@example.com",
  "description": "Full description...",
  "input_transform": {
    "obor": "Frontend Development",
    "seniorita": "Začátečník",
    "hlavni_cil": "První práce v IT",
    "casovy_horizont": "6 měsíců",
    "raw_description": "..."
  },
  "status": "FLAGGED"
}
```

**Response (201):**
```json
{
  "success": true,
  "lead_id": "uuid-here",
  "message": "Lead created successfully"
}
```

### GET /api/health
Health check endpoint.

### GET /api/leads/<lead_id>
Získá detail leadu podle ID.

## 🗄️ Databázová struktura

Data se ukládají do tabulky `junior_leads`:

| Pole | Typ | Popis |
|------|-----|-------|
| id | text | UUID leadu |
| name | text | Jméno uživatele |
| email | text | Email |
| description | text | Kompletní popis (včetně všech odpovědí) |
| status | text | FLAGGED (připraveno k procesingu) |
| input_transform | jsonb | Strukturovaná data z formuláře |
| plan | text | NULL (vyplní se později v pipeline) |
| created_at | text | ISO timestamp |

## 🎨 Design System

### Barvy
- **Primary**: `#4F46E5` (Indigo)
- **Success**: `#10B981` (Green)
- **Text Primary**: `#0F172A`
- **Text Secondary**: `#64748B`
- **Background**: `#F8FAFC`

### Typography
- **Font**: System font stack (SF Pro, Segoe UI, Roboto)
- **Sizes**: 14px - 32px (responsive)

### Spacing
- Konzistentní 8px grid
- Variables: `--space-xs` až `--space-2xl`

### Shadows
- 4 úrovně (`sm`, `md`, `lg`, `xl`)
- Subtilní, moderní

## 📱 Responzivita

- **Desktop (>1024px)**: Live Activity Panel vedle hlavního obsahu
- **Tablet (768-1024px)**: Live Activity Panel skryt
- **Mobile (<768px)**: Single column, vertikální layout

## ♿ Accessibility

- Semantic HTML5 elements
- Proper ARIA labels
- Keyboard navigation
- Focus states
- High contrast ratios
- Support for `prefers-reduced-motion`

## 🔒 Validace

### Client-side (JavaScript)
- Email format validation
- Minimální délka textu (20 znaků pro description)
- Povinná pole před odesláním
- Real-time character counter

### Server-side (Python)
- Email format check
- Required fields validation
- SQL injection protection (Supabase client)
- Error handling & logging

## 🔗 Integrace s pipeline

Po úspěšném submitu:

1. Lead je vytvořen se statusem `FLAGGED`
2. Pipeline (`run_pipeline.py`) automaticky zpracovává FLAGGED leady
3. Vygeneruje se personalizovaný kariérní plán
4. Status se postupně mění: `FLAGGED` → `PROCESSING` → `PLAN_READY` → `UPLOADED`
5. Uživatel dostane email s přístupem k plánu

## 🚫 Co NENÍ implementováno (podle constraintů)

- ❌ Klikatelné odkazy během onboardingu
- ❌ Reálná firemní loga
- ❌ Zmínky o AI nebo syntetických datech
- ❌ Nabídky práce během onboardingu
- ❌ Hard-coded URL/route (vše přes env variables)

## 🔧 Konfigurace Frontend

V `onboarding.js` můžete změnit:

```javascript
// API endpoint
window.ORAKULUM_API_ENDPOINT = '/api/leads';

// Success redirect URL
window.ORAKULUM_SUCCESS_URL = '/dashboard';
```

Nebo nastavte přes `<script>` před načtením `onboarding.js`:

```html
<script>
  window.ORAKULUM_API_ENDPOINT = 'https://your-api.com/api/leads';
  window.ORAKULUM_SUCCESS_URL = 'https://your-app.com/dashboard';
</script>
<script src="onboarding.js"></script>
```

## 📊 Metriky & Analytics

Pro tracking můžete přidat:

```javascript
// V onboarding.js po každém kroku
function nextStep() {
    // ... existing code ...
    
    // Track step completion
    if (window.analytics) {
        window.analytics.track('Onboarding Step Completed', {
            step: state.currentStep,
            stepName: getStepName(state.currentStep)
        });
    }
}
```

## 🐛 Troubleshooting

### API nereaguje
- Zkontrolujte, že `api_onboarding.py` běží
- Ověřte CORS nastavení
- Zkontrolujte network tab v browser DevTools

### Formulář se neodešle
- Otevřete browser console (F12)
- Zkontrolujte chybové hlášky
- Ověřte že všechna pole jsou vyplněná

### Live Activity Panel se nerotuje
- Zkontrolujte console errory
- Obnovte stránku (F5)
- Vypněte ad-blockery

### Supabase error
- Zkontrolujte `.env` konfiguraci
- Ověřte že SUPABASE_URL a SUPABASE_SERVICE_KEY jsou správné
- Zkontrolujte row-level security policies v Supabase

## 🚀 Deployment

### Frontend (Vercel, Netlify)
1. Upload `onboarding.html`, `onboarding.css`, `onboarding.js`
2. Nastavte environment variables v hosting platformě
3. Nakonfigurujte redirecty (optional)

### Backend (Heroku, Railway, Fly.io)
1. Deploy `api_onboarding.py`
2. Nastavte environment variables
3. Nakonfigurujte gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_onboarding:app
```

### Alternative: Supabase Edge Functions
API endpoint lze také implementovat jako Supabase Edge Function pro serverless deployment.

## 📝 Licence & Poznámky

- Pro interní použití projektu Orakulum
- Design inspirován moderními SaaS onboardingy (Linear, Notion, Stripe)
- Veškerý text v češtině pro cílovou skupinu

## 🤝 Contributing

Pro změny v onboardingu:
1. Testujte v různých prohlížečích
2. Zachovejte design system konzistenci
3. Aktualizujte tuto dokumentaci
4. Netlačte změny přímo na production

---

**Vytvořeno**: 2025-12-16  
**Verze**: 1.0.0  
**Autor**: Orakulum Team
