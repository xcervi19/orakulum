'use client';

import { useState } from 'react';
import { BaseStep } from './BaseStep';
import { OnboardingFormData } from '@/types/onboarding';

interface CasovyHorizontStepProps {
  value: string;
  onNext: () => void;
  onBack: () => void;
  onDataChange: (data: Partial<OnboardingFormData>) => void;
}

const CASOVY_HORIZONT_OPTIONS = [
  { value: '1_mesic', label: '1 měsíc', description: 'Rychlý start' },
  { value: '3_mesice', label: '3 měsíce', description: 'Krátkodobý plán' },
  { value: '6_mesicu', label: '6 měsíců', description: 'Střednědobý plán' },
  { value: '1_rok', label: '1 rok', description: 'Dlouhodobý plán' },
  { value: '2_roky', label: '2+ roky', description: 'Velmi dlouhodobý plán' },
];

export function CasovyHorizontStep({ value, onNext, onBack, onDataChange }: CasovyHorizontStepProps) {
  const [casovyHorizont, setCasovyHorizont] = useState(value);

  const handleNext = () => {
    onDataChange({
      inputTransform: {
        casovy_horizont: casovyHorizont,
      } as any,
    });
    onNext();
  };

  return (
    <BaseStep
      title="Jaký je váš časový horizont?"
      description="Za jak dlouho chcete dosáhnout svého cíle?"
      onNext={handleNext}
      onBack={onBack}
      canProceed={casovyHorizont.length > 0}
    >
      <div className="space-y-3">
        {CASOVY_HORIZONT_OPTIONS.map((item) => (
          <button
            key={item.value}
            onClick={() => setCasovyHorizont(item.value)}
            className={`w-full p-5 rounded-lg border-2 text-left transition-all ${
              casovyHorizont === item.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="font-semibold text-slate-900 mb-1">{item.label}</div>
            <div className="text-sm text-slate-600">{item.description}</div>
          </button>
        ))}
      </div>
    </BaseStep>
  );
}
