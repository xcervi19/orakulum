# Orakulum Onboarding UI

Modern, high-conversion onboarding flow pro Orakulum kariérní plány.

## Funkce

- **Stepper pattern** - 1 otázka = 1 obrazovka
- **Live Activity Panel** - pasivní signály aktivity (rotace každých 6-8s)
- **Processing Screen** - animovaná sekvence po odeslání
- **Fullscreen design** - bez navigace, maximální focus
- **Validace** - okamžitá zpětná vazba
- **Responsive** - desktop + mobile

## Flow kroků

0. **Intro** - Uvítání a přehled hodnot
1. **Cíl** - Hlavní kariérní ambice (výběr)
2. **Oblast** - Technická specializace (výběr)
3. **Úroveň** - Aktuální zkušenosti (výběr)
4. **Konkrétnost** - Detailní popis situace (text)
5. **Časový horizont** - Preferovaný timeline (výběr)
6. **Email** - Kontakt pro přístup (email + submit)

## Instalace

```bash
npm install
```

## Development

```bash
npm run dev
```

Aplikace běží na `http://localhost:3000`

## Build

```bash
npm run build
```

Output v `/dist`

## Integrace s backendem

### API payload

Při submitu se volá API s následující strukturou:

```typescript
interface SubmitPayload {
  name: string;        // Z emailu nebo výchozí
  email: string;       // Email uživatele
  description: string; // Složený text ze všech odpovědí
  metadata: {          // Strukturovaná data
    goal: string;
    area: string;
    level: string;
    specificity: string;
    timeHorizon: string;
  };
}
```

### Připojení k Supabase

V `src/hooks/useOnboarding.ts` nahraďte simulovanou API call:

```typescript
// Aktuální (simulované)
await simulateApiCall(payload);

// Produkce (Supabase)
const { error } = await supabase
  .from('junior_leads')
  .insert({
    id: crypto.randomUUID(),
    name: payload.name,
    email: payload.email,
    description: payload.description,
    status: 'FLAGGED',
    input_transform: payload.metadata,
  });
if (error) throw error;
```

### Konfigurace endpointu

Pro REST API:

```typescript
const response = await fetch('/api/leads', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});
if (!response.ok) throw new Error('API error');
```

## Přizpůsobení

### Kroky a možnosti

Editujte `src/data/steps.ts`:

```typescript
{
  id: 1,
  key: 'goal',
  title: 'Jaký je váš hlavní cíl?',
  type: 'selection',
  options: [
    { value: 'first_job', label: 'Získat první práci', icon: '🚀' },
    // ...
  ],
}
```

### Live Activity data

Editujte `src/data/activity.ts`:

```typescript
export const ACTIVITY_ITEMS = [
  { id: '1', avatar: '👨‍💻', role: 'Backend Engineer', action: 'dokončil plán' },
  // ...
];
```

### Barvy a styly

Editujte `tailwind.config.js` pro změnu barevného schématu.

## Zachované constrainty

- ✅ Zachována struktura pro DB zápis (`junior_leads`)
- ✅ Zachován API payload format
- ✅ Zachovány field names a mapování
- ✅ Žádné nové povinné fieldy
- ✅ Žádné hard-coded URL/routes
- ✅ Pouze UI/UX změny

## Technologie

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
