// Form field types - matching existing API/DB schema
export interface OnboardingFormData {
  goal: string;           // Cíl
  area: string;           // Oblast
  level: string;          // Úroveň
  specificity: string;    // Konkrétnost
  timeHorizon: string;    // Časový horizont
  email: string;          // Email
  name?: string;          // Optional name
}

// Step configuration
export interface StepConfig {
  id: number;
  key: keyof OnboardingFormData | 'intro';
  title: string;
  subtitle?: string;
  type: 'intro' | 'selection' | 'text' | 'email';
  options?: StepOption[];
  placeholder?: string;
  validation?: (value: string) => boolean;
}

export interface StepOption {
  value: string;
  label: string;
  description?: string;
  icon?: string;
}

// Live activity types
export interface ActivityItem {
  id: string;
  avatar: string;
  role: string;
  action: string;
  timestamp?: string;
}

// Processing step type
export interface ProcessingStep {
  id: string;
  text: string;
  duration: number;
}
