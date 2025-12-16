'use client';

import { useState } from 'react';
import { BaseStep } from './BaseStep';
import { OnboardingFormData } from '@/types/onboarding';

interface EmailStepProps {
  email: string;
  name?: string;
  onBack: () => void;
  onSubmit: () => void;
  onDataChange: (data: Partial<OnboardingFormData>) => void;
  error: string | null;
}

export function EmailStep({ email, name, onBack, onSubmit, onDataChange, error }: EmailStepProps) {
  const [emailValue, setEmailValue] = useState(email);
  const [nameValue, setNameValue] = useState(name || '');
  const [emailError, setEmailError] = useState<string | null>(null);

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleSubmit = () => {
    if (!emailValue.trim()) {
      setEmailError('Email je povinný');
      return;
    }

    if (!validateEmail(emailValue)) {
      setEmailError('Zadejte platný email');
      return;
    }

    setEmailError(null);
    onDataChange({
      email: emailValue,
      name: nameValue.trim() || undefined,
    });
    onSubmit();
  };

  return (
    <BaseStep
      title="Téměř hotovo!"
      description="Zadejte svůj email, abychom vám mohli poslat váš plán"
      onNext={handleSubmit}
      onBack={onBack}
      nextLabel="Vytvořit plán"
      canProceed={emailValue.trim().length > 0}
    >
      <div className="space-y-6">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
            Email *
          </label>
          <input
            id="email"
            type="email"
            value={emailValue}
            onChange={(e) => {
              setEmailValue(e.target.value);
              setEmailError(null);
            }}
            placeholder="vas@email.cz"
            className={`w-full p-4 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
              emailError || error ? 'border-red-300' : 'border-slate-300'
            }`}
            autoFocus
          />
          {(emailError || error) && (
            <p className="mt-2 text-sm text-red-600">{emailError || error}</p>
          )}
        </div>

        <div>
          <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-2">
            Jméno (volitelné)
          </label>
          <input
            id="name"
            type="text"
            value={nameValue}
            onChange={(e) => setNameValue(e.target.value)}
            placeholder="Vaše jméno"
            className="w-full p-4 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div className="bg-slate-50 rounded-lg p-4 text-sm text-slate-600">
          <p>Po dokončení vám zašleme váš osobní kariérní plán na uvedený email.</p>
        </div>
      </div>
    </BaseStep>
  );
}
