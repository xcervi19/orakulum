'use client';

import { useState } from 'react';
import { BaseStep } from './BaseStep';
import { OnboardingFormData } from '@/types/onboarding';

interface OblastStepProps {
  value: string;
  onNext: () => void;
  onBack: () => void;
  onDataChange: (data: Partial<OnboardingFormData>) => void;
}

const OBLASTI = [
  'Frontend Development',
  'Backend Development',
  'Full Stack Development',
  'DevOps',
  'Data Science',
  'Machine Learning',
  'Mobile Development',
  'UI/UX Design',
  'Product Management',
  'QA/Testing',
  'Cybersecurity',
  'Cloud Architecture',
  'Jiné',
];

export function OblastStep({ value, onNext, onBack, onDataChange }: OblastStepProps) {
  const [oblast, setOblast] = useState(value);
  const [customOblast, setCustomOblast] = useState('');

  const handleNext = () => {
    const finalOblast = oblast === 'Jiné' ? customOblast : oblast;
    onDataChange({
      inputTransform: {
        obor: finalOblast,
      } as any,
    });
    onNext();
  };

  const handleSelect = (selected: string) => {
    setOblast(selected);
    if (selected !== 'Jiné') {
      setCustomOblast('');
    }
  };

  return (
    <BaseStep
      title="V jaké oblasti chcete pracovat?"
      description="Vyberte hlavní obor nebo doménu"
      onNext={handleNext}
      onBack={onBack}
      canProceed={oblast === 'Jiné' ? customOblast.trim().length > 0 : oblast.length > 0}
    >
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {OBLASTI.map((item) => (
          <button
            key={item}
            onClick={() => handleSelect(item)}
            className={`p-4 rounded-lg border-2 transition-all ${
              oblast === item
                ? 'border-primary-500 bg-primary-50 text-primary-900'
                : 'border-slate-200 hover:border-slate-300 text-slate-700'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {oblast === 'Jiné' && (
        <input
          type="text"
          value={customOblast}
          onChange={(e) => setCustomOblast(e.target.value)}
          placeholder="Zadejte svou oblast..."
          className="w-full p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent mt-4"
          autoFocus
        />
      )}
    </BaseStep>
  );
}
