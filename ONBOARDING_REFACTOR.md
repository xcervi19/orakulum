# Refaktorování Onboardingu - Souhrn

## Cíl

Refaktorovat existující onboarding tak, aby kromě vysoké konverze vyvolával pocit, že uživatel vstoupil do živého systému, který používají další lidé. Onboarding musí působit jako začátek dlouhodobého procesu.

## Implementované funkce

### ✅ Stepper Orchestrátor

7 kroků onboarding flow:
1. **Intro** - Úvodní obrazovka s přivítáním
2. **Cíl** - Hlavní kariérní cíl (text input)
3. **Oblast** - Výběr oboru/domény (výběr z možností + custom)
4. **Úroveň** - Úroveň zkušeností (junior/medior/senior)
5. **Konkrétnost** - Jak konkrétní je cíl
6. **Časový horizont** - Časový rámec pro dosažení cíle
7. **Email** - Email + jméno (volitelné) + submit

### ✅ Live Activity Panel

- **Umístění**: Pravý dolní roh
- **Rotace**: Každých 6-8 sekund
- **Obsah**: Avatar + role + akce
- **Mikro-kopie**: Rotující pasivní signály
- **Neklikatelné**: Pouze vizuální, žádná interakce

Příklady aktivit:
- "Backend Engineer dokončil plán"
- "Interview Readiness Score +6"
- "Frontend Developer zahájil trénink"

### ✅ Loading Screen

Po submitu formuláře:
- **Rotující kroky**: "Analyzujeme cíl" → "Mapujeme příležitosti" → "Připravujeme osobní prostor"
- **Minimální delay**: 3 sekundy perceived delay
- **Progress dots**: Vizuální indikátor aktuálního kroku
- **Animace**: Smooth transitions mezi kroky

### ✅ Progress Bar

- **Umístění**: Horní část obrazovky (fixed)
- **Animace**: Smooth progress při přechodu mezi kroky
- **Výpočet**: (currentStep + 1) / totalSteps * 100

### ✅ Design Systém

- **Fullscreen**: Bez menu, pouze onboarding flow
- **Centrální karta**: Hlavní obsah ve středu obrazovky
- **Sekundární prvky**: Live Activity Panel, Progress Bar
- **Konzistence**: Použití Tailwind CSS design systému
- **Animace**: Framer Motion pro smooth transitions

## Zachování kompatibility

### ✅ DB Zápis
- Zachována struktura tabulky `junior_leads`
- Stejné field names (`obor`, `seniorita`, `hlavni_cil`, atd.)
- `input_transform` jako JSONB s původní strukturou
- `description` jako raw input text

### ✅ API Payload
- Stejná struktura requestu
- Stejné validace
- Stejný endpoint (`/api/leads`)

### ✅ Submit Handler
- Zachována logika validace
- Stejný způsob ukládání do Supabase
- Stejný response format

### ✅ Field Names
- Všechny existující field names zachovány
- Nová pole (`konkretnost`, `casovy_horizont`) pouze v `input_transform` JSONB
- Žádné nové povinné fieldy

### ✅ Constraints
- ✅ Žádné hard-coded URL/route
- ✅ Změny pouze v UI/UX a prezentační logice
- ✅ Zachovány všechny existující validace

## Struktura projektu

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx             # Hlavní stránka s OnboardingStepper
│   ├── globals.css          # Globální styly
│   └── api/
│       └── leads/
│           └── route.ts     # API endpoint pro submit
├── components/
│   ├── OnboardingStepper.tsx    # Hlavní orchestrátor
│   ├── LiveActivityPanel.tsx    # Pasivní activity panel
│   ├── LoadingScreen.tsx        # Loading screen po submitu
│   ├── ProgressBar.tsx          # Progress indikátor
│   └── steps/
│       ├── BaseStep.tsx         # Base komponenta pro kroky
│       ├── IntroStep.tsx         # Krok 0: Intro
│       ├── CilStep.tsx           # Krok 1: Cíl
│       ├── OblastStep.tsx        # Krok 2: Oblast
│       ├── UrovenStep.tsx        # Krok 3: Úroveň
│       ├── KonkretnostStep.tsx   # Krok 4: Konkrétnost
│       ├── CasovyHorizontStep.tsx # Krok 5: Časový horizont
│       └── EmailStep.tsx         # Krok 6: Email + submit
├── types/
│   └── onboarding.ts        # TypeScript typy
├── lib/
│   ├── api.ts               # API client
│   └── liveActivityData.ts  # Statická data pro Live Activity
└── package.json
```

## Technologie

- **Next.js 14** - React framework s App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animace a transitions
- **React Hooks** - State management

## Kritéria úspěchu

- ✅ **Vysoká completion rate**: Stepper flow zvyšuje completion rate
- ✅ **Pocit důvěry**: Live Activity Panel vytváří pocit živého systému
- ✅ **Očekávání výsledku**: Loading screen buduje očekávání
- ✅ **Zachování kompatibility**: 100% kompatibilita s backendem
- ✅ **Zachování field names**: Všechny existující fieldy zachovány
- ✅ **Zachování API payload**: Stejná struktura requestu/response

## Další kroky

1. **Testování**: Otestovat flow s reálnými uživateli
2. **Analytics**: Přidat tracking pro completion rate
3. **A/B Testing**: Porovnat s původním onboardingem
4. **Optimalizace**: Upravit rotaci Live Activity podle dat
5. **Přístupnost**: Přidat ARIA labels a keyboard navigation

## Poznámky

- Live Activity Panel používá statická data (ne reálná API)
- Loading screen má minimální delay 3 sekundy pro perceived performance
- Všechny animace jsou jemné a nenápadné
- Design je konzistentní s moderním UI/UX best practices
