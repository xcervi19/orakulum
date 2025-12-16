'use client';

import { useState } from 'react';
import { BaseStep } from './BaseStep';
import { OnboardingFormData } from '@/types/onboarding';

interface UrovenStepProps {
  value: string;
  onNext: () => void;
  onBack: () => void;
  onDataChange: (data: Partial<OnboardingFormData>) => void;
}

const UROVNE = [
  { value: 'junior', label: 'Junior', description: 'Začínám nebo mám základní zkušenosti' },
  { value: 'medior', label: 'Medior', description: 'Mám několik let praxe' },
  { value: 'senior', label: 'Senior', description: 'Zkušený profesionál' },
  { value: 'nezadano', label: 'Nevím', description: 'Ještě si nejsem jistý' },
];

export function UrovenStep({ value, onNext, onBack, onDataChange }: UrovenStepProps) {
  const [uroven, setUroven] = useState(value);

  const handleNext = () => {
    onDataChange({
      inputTransform: {
        seniorita: uroven === 'nezadano' ? 'nezadáno' : uroven,
      } as any,
    });
    onNext();
  };

  return (
    <BaseStep
      title="Jaká je vaše úroveň zkušeností?"
      description="Vyberte úroveň, která nejlépe odpovídá vašim zkušenostem"
      onNext={handleNext}
      onBack={onBack}
      canProceed={uroven.length > 0}
    >
      <div className="space-y-3">
        {UROVNE.map((item) => (
          <button
            key={item.value}
            onClick={() => setUroven(item.value)}
            className={`w-full p-5 rounded-lg border-2 text-left transition-all ${
              uroven === item.value
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
