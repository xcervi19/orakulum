# Integrace Onboarding Frontendu

## Přehled změn

Refaktorovaný onboarding zachovává **100% kompatibilitu** s existujícím backendem a databázovým schématem.

## Zachované komponenty

### Field Names
Všechny existující field names zůstávají stejné:
- `obor` - hlavní obor/doména
- `seniorita` - úroveň zkušeností
- `hlavni_cil` - hlavní kariérní cíl
- `technologie` - seznam technologií (pole)
- `platove_ocekavani` - platové očekávání
- `email` - email uživatele
- `name` - jméno uživatele (volitelné)
- `description` - raw input text

### Nová pole (volitelná, neporušují constrainty)
- `konkretnost` - přidáno do `input_transform` JSONB
- `casovy_horizont` - přidáno do `input_transform` JSONB

### API Payload Struktura

```json
{
  "name": "string",
  "email": "string",
  "description": "string",
  "input_transform": {
    "obor": "string",
    "seniorita": "string",
    "hlavni_cil": "string",
    "technologie": ["string"],
    "platove_ocekavani": "string | null",
    "konkretnost": "string",
    "casovy_horizont": "string",
    "puvodni_text": "string"
  },
  "status": "FLAGGED"
}
```

### DB Zápis

Data se ukládají do tabulky `junior_leads` se stejnou strukturou:
- `name` → `name` (text)
- `email` → `email` (text)
- `description` → `description` (text) - raw input
- `input_transform` → `input_transform` (jsonb) - strukturovaná data
- `status` → `status` (text) - nastaveno na 'FLAGGED'

## API Endpoint

### POST `/api/leads`

**Request:**
```typescript
{
  name?: string;
  email: string;
  description: string;
  input_transform: {
    obor: string;
    seniorita: string;
    hlavni_cil: string;
    technologie: string[];
    platove_ocekavani: string | null;
    konkretnost: string;
    casovy_horizont: string;
    puvodni_text: string;
  };
}
```

**Response:**
```typescript
{
  id: string; // UUID lead ID
  success: boolean;
}
```

## Validace

- Email je povinný a musí být validní
- Description je povinný
- `input_transform` je povinný objekt

## Submit Handler

Submit handler zachovává stejnou logiku:
1. Validuje požadovaná pole
2. Volá Supabase API endpoint
3. Vrací lead ID nebo chybu

## Změny pouze v UI/UX

- **Stepper orchestrátor**: Rozděluje formulář na 7 kroků
- **Live Activity Panel**: Pasivní rotující signály
- **Loading Screen**: Processing screen po submitu
- **Progress Bar**: Vizuální indikátor pokroku
- **Animace**: Jemné přechody mezi kroky

## Kompatibilita s Pipeline

Frontend generuje data ve formátu, který pipeline očekává:
- `input_transform` JSONB struktura odpovídá schématu
- `status: 'FLAGGED'` spustí pipeline zpracování
- `description` obsahuje raw input pro referenci

## Testování

1. Spusťte frontend: `npm run dev`
2. Projděte všechny kroky onboarding flow
3. Ověřte, že data se správně ukládají do DB
4. Zkontrolujte, že pipeline může zpracovat nový lead

## Rollback

Pokud je potřeba vrátit se k původnímu onboarding:
- Frontend je v samostatné složce `/frontend`
- Backend a pipeline zůstávají beze změn
- Stačí změnit routing na původní formulář
