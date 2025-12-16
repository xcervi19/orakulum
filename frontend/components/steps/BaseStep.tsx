'use client';

import { ReactNode } from 'react';

interface BaseStepProps {
  title: string;
  description?: string;
  children: ReactNode;
  onNext: () => void;
  onBack?: () => void;
  nextLabel?: string;
  backLabel?: string;
  canProceed?: boolean;
}

export function BaseStep({
  title,
  description,
  children,
  onNext,
  onBack,
  nextLabel = 'Pokračovat',
  backLabel = 'Zpět',
  canProceed = true,
}: BaseStepProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
      <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-3">
        {title}
      </h1>
      {description && (
        <p className="text-lg text-slate-600 mb-8">{description}</p>
      )}

      <div className="mb-8">{children}</div>

      <div className="flex gap-4 justify-end">
        {onBack && (
          <button
            onClick={onBack}
            className="px-6 py-3 text-slate-600 hover:text-slate-900 transition-colors"
          >
            {backLabel}
          </button>
        )}
        <button
          onClick={onNext}
          disabled={!canProceed}
          className={`px-8 py-3 rounded-lg font-medium transition-all ${
            canProceed
              ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-md hover:shadow-lg'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
          }`}
        >
          {nextLabel}
        </button>
      </div>
    </div>
  );
}
