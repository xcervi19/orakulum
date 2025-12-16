'use client';

import { useState } from 'react';
import { BaseStep } from './BaseStep';
import { OnboardingFormData } from '@/types/onboarding';

interface KonkretnostStepProps {
  value: string;
  onNext: () => void;
  onBack: () => void;
  onDataChange: (data: Partial<OnboardingFormData>) => void;
}

const KONKRETNOST_OPTIONS = [
  { value: 'velmi_konkretni', label: 'Velmi konkrétní', description: 'Vím přesně, co chci' },
  { value: 'konkretni', label: 'Konkrétní', description: 'Mám představu, ale potřebuji upřesnit' },
  { value: 'obecny', label: 'Obecný', description: 'Zatím jen obecná představa' },
];

export function KonkretnostStep({ value, onNext, onBack, onDataChange }: KonkretnostStepProps) {
  const [konkretnost, setKonkretnost] = useState(value);

  const handleNext = () => {
    onDataChange({
      inputTransform: {
        konkretnost: konkretnost,
      } as any,
    });
    onNext();
  };

  return (
    <BaseStep
      title="Jak konkrétní je váš cíl?"
      description="Pomůže nám to připravit plán přesně pro vás"
      onNext={handleNext}
      onBack={onBack}
      canProceed={konkretnost.length > 0}
    >
      <div className="space-y-3">
        {KONKRETNOST_OPTIONS.map((item) => (
          <button
            key={item.value}
            onClick={() => setKonkretnost(item.value)}
            className={`w-full p-5 rounded-lg border-2 text-left transition-all ${
              konkretnost === item.value
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
