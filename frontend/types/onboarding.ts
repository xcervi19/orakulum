/**
 * Onboarding types - zachovává existující field names a strukturu z DB
 */

export interface OnboardingFormData {
  // Raw input - zachovává se jako "description" v DB
  description: string;
  
  // Strukturovaná data - zachovává se jako "input_transform" JSONB v DB
  inputTransform: {
    obor: string; // "hlavní obor/doména"
    seniorita: string; // "úroveň zkušeností"
    hlavni_cil: string; // "hlavní kariérní cíl"
    technologie: string[]; // "seznam relevantních technologií"
    platove_ocekavani: string | null; // "platové očekávání pokud zmíněno"
    konkretnost: string; // nové pole pro konkrétnost
    casovy_horizont: string; // nové pole pro časový horizont
    kvalita_vstupu?: {
      skore: number;
      popis: string;
    };
    inference?: {
      poznamky: string[];
    };
    puvodni_text?: string;
  };
  
  // Email - zachovává se jako "email" v DB
  email: string;
  
  // Name - zachovává se jako "name" v DB (volitelné)
  name?: string;
}

export type OnboardingStep = 
  | 'intro'
  | 'cil'
  | 'oblast'
  | 'uroven'
  | 'konkretnost'
  | 'casovy_horizont'
  | 'email';

export interface LiveActivityItem {
  avatar: string;
  role: string;
  action: string;
}
