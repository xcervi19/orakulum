import { useState, useCallback } from 'react';
import { OnboardingFormData } from '../types';
import { STEPS } from '../data/steps';

const INITIAL_FORM_DATA: OnboardingFormData = {
  goal: '',
  area: '',
  level: '',
  specificity: '',
  timeHorizon: '',
  email: '',
  name: '',
};

export function useOnboarding() {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<OnboardingFormData>(INITIAL_FORM_DATA);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const totalSteps = STEPS.length;
  const progress = ((currentStep) / (totalSteps - 1)) * 100;
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === totalSteps - 1;

  const updateField = useCallback(<K extends keyof OnboardingFormData>(
    field: K,
    value: OnboardingFormData[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null);
  }, []);

  const validateCurrentStep = useCallback((): boolean => {
    const step = STEPS[currentStep];
    
    if (step.type === 'intro') return true;
    
    const fieldKey = step.key as keyof OnboardingFormData;
    const value = formData[fieldKey] || '';
    
    if (step.type === 'selection' && !value) {
      setError('Vyberte jednu z možností');
      return false;
    }
    
    if (step.type === 'text' && (!value || value.trim().length < 20)) {
      setError('Prosím, napište alespoň pár vět (min. 20 znaků)');
      return false;
    }
    
    if (step.type === 'email') {
      if (!value) {
        setError('Zadejte emailovou adresu');
        return false;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        setError('Zadejte platnou emailovou adresu');
        return false;
      }
    }
    
    return true;
  }, [currentStep, formData]);

  const goToNextStep = useCallback(() => {
    if (!validateCurrentStep()) return;
    
    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1);
      setError(null);
    }
  }, [currentStep, totalSteps, validateCurrentStep]);

  const goToPrevStep = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
      setError(null);
    }
  }, [currentStep]);

  const handleSubmit = useCallback(async () => {
    if (!validateCurrentStep()) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Prepare payload matching existing API structure
      const payload = {
        name: formData.name || formData.email.split('@')[0],
        email: formData.email,
        description: buildDescription(formData),
        // Additional structured data that could be used
        metadata: {
          goal: formData.goal,
          area: formData.area,
          level: formData.level,
          specificity: formData.specificity,
          timeHorizon: formData.timeHorizon,
        },
      };
      
      // This is where the existing API call would go
      // For now, we simulate the processing time
      console.log('Submitting payload:', payload);
      
      // Simulated API call - replace with actual endpoint
      await simulateApiCall(payload);
      
      setIsComplete(true);
    } catch (err) {
      setError('Něco se pokazilo. Zkuste to prosím znovu.');
      console.error('Submit error:', err);
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, validateCurrentStep]);

  return {
    currentStep,
    formData,
    isSubmitting,
    isComplete,
    error,
    progress,
    isFirstStep,
    isLastStep,
    totalSteps,
    updateField,
    goToNextStep,
    goToPrevStep,
    handleSubmit,
  };
}

// Helper to build description from form data
function buildDescription(data: OnboardingFormData): string {
  const parts: string[] = [];
  
  const goalLabels: Record<string, string> = {
    first_job: 'Chci získat první práci v IT',
    career_change: 'Chci změnit kariéru a přejít do IT',
    level_up: 'Chci se posunout výš v aktuální pozici',
    specialize: 'Chci se specializovat',
  };
  
  const areaLabels: Record<string, string> = {
    frontend: 'Frontend Development',
    backend: 'Backend Development',
    fullstack: 'Fullstack Development',
    mobile: 'Mobile Development',
    data: 'Data & Analytics',
    devops: 'DevOps & Cloud',
  };
  
  const levelLabels: Record<string, string> = {
    beginner: 'úplný začátečník',
    learning: 'učím se',
    junior: 'junior',
    mid: 'mid-level',
  };
  
  const timeLabels: Record<string, string> = {
    '3_months': '3 měsíce',
    '6_months': '6 měsíců',
    '12_months': '12 měsíců',
    flexible: 'flexibilní časový horizont',
  };
  
  if (data.goal && goalLabels[data.goal]) {
    parts.push(goalLabels[data.goal]);
  }
  
  if (data.area && areaLabels[data.area]) {
    parts.push(`v oblasti ${areaLabels[data.area]}`);
  }
  
  if (data.level && levelLabels[data.level]) {
    parts.push(`Aktuálně jsem ${levelLabels[data.level]}`);
  }
  
  if (data.specificity) {
    parts.push(data.specificity);
  }
  
  if (data.timeHorizon && timeLabels[data.timeHorizon]) {
    parts.push(`Časový horizont: ${timeLabels[data.timeHorizon]}`);
  }
  
  return parts.join('. ');
}

// Simulated API call - replace with actual implementation
async function simulateApiCall(payload: unknown): Promise<void> {
  // In production, this would be:
  // const response = await fetch('/api/leads', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(payload),
  // });
  // if (!response.ok) throw new Error('API error');
  
  // For demo, simulate network delay
  await new Promise(resolve => setTimeout(resolve, 100));
  console.log('API would receive:', payload);
}
