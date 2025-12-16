'use client';

import { useState } from 'react';
import { BaseStep } from './BaseStep';
import { OnboardingFormData } from '@/types/onboarding';

interface CilStepProps {
  value: string;
  onNext: () => void;
  onDataChange: (data: Partial<OnboardingFormData>) => void;
}

export function CilStep({ value, onNext, onDataChange }: CilStepProps) {
  const [cil, setCil] = useState(value);

  const handleNext = () => {
    onDataChange({
      inputTransform: {
        hlavni_cil: cil,
      } as any,
    });
    onNext();
  };

  return (
    <BaseStep
      title="Jaký je váš hlavní cíl?"
      description="Co chcete v kariéře dosáhnout?"
      onNext={handleNext}
      canProceed={cil.trim().length > 0}
    >
      <textarea
        value={cil}
        onChange={(e) => setCil(e.target.value)}
        placeholder="Např. stát se senior frontend vývojářem, získat práci v IT, změnit obor..."
        className="w-full h-32 p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
        autoFocus
      />
    </BaseStep>
  );
}
