'use client';

import { BaseStep } from './BaseStep';

interface IntroStepProps {
  onNext: () => void;
}

export function IntroStep({ onNext }: IntroStepProps) {
  return (
    <BaseStep
      title="Vítejte v Orakulum"
      description="Pomůžeme vám vytvořit osobní kariérní plán na míru. Proces trvá jen pár minut."
      onNext={onNext}
      nextLabel="Začít"
      canProceed={true}
    >
      <div className="space-y-4 text-slate-700">
        <p className="text-lg">
          Vytvoříme pro vás strukturovaný plán, který vás posune vpřed ve vaší kariéře.
        </p>
        <ul className="list-disc list-inside space-y-2 ml-4">
          <li>Personalizovaný přístup</li>
          <li>Konkrétní kroky k cíli</li>
          <li>Podpora na každém kroku</li>
        </ul>
      </div>
    </BaseStep>
  );
}
