# Orakulum Onboarding Frontend

Refaktorovaný onboarding systém s live activity panelem a stepper orchestrátorem.

## Funkce

- **Stepper orchestrátor**: 7 kroků (Intro → Cíl → Oblast → Úroveň → Konkrétnost → Časový horizont → Email)
- **Live Activity Panel**: Rotující pasivní signály aktivity každých 6-8 sekund
- **Loading Screen**: Processing screen s rotujícími kroky po submitu
- **Progress Bar**: Vizuální indikátor pokroku
- **Zachování existující struktury**: Field names, API payload a DB zápis zůstávají stejné

## Instalace

```bash
npm install
```

## Vývoj

```bash
npm run dev
```

Aplikace poběží na [http://localhost:3000](http://localhost:3000)

## Build

```bash
npm run build
npm start
```

## Environment Variables

Vytvořte `.env.local`:

```env
NEXT_PUBLIC_API_URL=/api/leads
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

## Struktura

- `app/` - Next.js App Router stránky
- `components/` - React komponenty
  - `OnboardingStepper.tsx` - Hlavní orchestrátor
  - `LiveActivityPanel.tsx` - Pasivní activity panel
  - `LoadingScreen.tsx` - Loading screen po submitu
  - `ProgressBar.tsx` - Progress indikátor
  - `steps/` - Jednotlivé kroky formuláře
- `types/` - TypeScript typy
- `lib/` - Utility funkce a API client

## Zachování kompatibility

- **Field names**: Zachovány všechny existující field names (`obor`, `seniorita`, `hlavni_cil`, `technologie`, atd.)
- **API payload**: Struktura odpovídá schématu `junior_leads` v Supabase
- **DB zápis**: `description`, `email`, `input_transform` JSONB struktura zachována
- **Submit handler**: Používá stejný endpoint a validace
