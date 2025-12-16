'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { OnboardingFormData, OnboardingStep } from '@/types/onboarding';
import { submitOnboarding } from '@/lib/api';
import { LiveActivityPanel } from './LiveActivityPanel';
import { LoadingScreen } from './LoadingScreen';
import { ProgressBar } from './ProgressBar';
import { IntroStep } from './steps/IntroStep';
import { CilStep } from './steps/CilStep';
import { OblastStep } from './steps/OblastStep';
import { UrovenStep } from './steps/UrovenStep';
import { KonkretnostStep } from './steps/KonkretnostStep';
import { CasovyHorizontStep } from './steps/CasovyHorizontStep';
import { EmailStep } from './steps/EmailStep';

const STEPS: OnboardingStep[] = [
  'intro',
  'cil',
  'oblast',
  'uroven',
  'konkretnost',
  'casovy_horizont',
  'email',
];

const STEP_LABELS: Record<OnboardingStep, string> = {
  intro: 'Úvod',
  cil: 'Cíl',
  oblast: 'Oblast',
  uroven: 'Úroveň',
  konkretnost: 'Konkrétnost',
  casovy_horizont: 'Časový horizont',
  email: 'Email',
};

export function OnboardingStepper() {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('intro');
  const [formData, setFormData] = useState<OnboardingFormData>({
    description: '',
    email: '',
    inputTransform: {
      obor: '',
      seniorita: '',
      hlavni_cil: '',
      technologie: [],
      platove_ocekavani: null,
      konkretnost: '',
      casovy_horizont: '',
    },
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const currentStepIndex = STEPS.indexOf(currentStep);
  const progress = ((currentStepIndex + 1) / STEPS.length) * 100;

  const handleNext = () => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < STEPS.length) {
      setCurrentStep(STEPS[nextIndex]);
    }
  };

  const handleBack = () => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(STEPS[prevIndex]);
    }
  };

  const handleStepData = (step: OnboardingStep, data: Partial<OnboardingFormData>) => {
    setFormData((prev) => {
      const updated = { ...prev };
      
      // Aktualizace podle kroku - pouze strukturovaná data, description se sestaví při submitu
      if (step === 'cil' && data.inputTransform?.hlavni_cil) {
        updated.inputTransform.hlavni_cil = data.inputTransform.hlavni_cil;
      } else if (step === 'oblast' && data.inputTransform?.obor) {
        updated.inputTransform.obor = data.inputTransform.obor;
      } else if (step === 'uroven' && data.inputTransform?.seniorita) {
        updated.inputTransform.seniorita = data.inputTransform.seniorita;
      } else if (step === 'konkretnost' && data.inputTransform?.konkretnost) {
        updated.inputTransform.konkretnost = data.inputTransform.konkretnost;
      } else if (step === 'casovy_horizont' && data.inputTransform?.casovy_horizont) {
        updated.inputTransform.casovy_horizont = data.inputTransform.casovy_horizont;
      } else if (step === 'email' && data.email) {
        updated.email = data.email;
        if (data.name) {
          updated.name = data.name;
        }
      }
      
      return updated;
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Sestavení finálního description z jednotlivých kroků
      // Zachovává strukturu pro DB - description jako raw input
      const descriptionParts = [
        formData.inputTransform.hlavni_cil && `Cíl: ${formData.inputTransform.hlavni_cil}`,
        formData.inputTransform.obor && `Oblast: ${formData.inputTransform.obor}`,
        formData.inputTransform.seniorita && `Úroveň: ${formData.inputTransform.seniorita}`,
        formData.inputTransform.konkretnost && `Konkrétnost: ${formData.inputTransform.konkretnost}`,
        formData.inputTransform.casovy_horizont && `Časový horizont: ${formData.inputTransform.casovy_horizont}`,
      ].filter(Boolean);

      const finalDescription = descriptionParts.join('. ') || formData.inputTransform.hlavni_cil || '';

      const finalData: OnboardingFormData = {
        ...formData,
        description: finalDescription,
      };

      const result = await submitOnboarding(finalData);
      
      if (!result.success) {
        setSubmitError(result.error || 'Chyba při odesílání');
        setIsSubmitting(false);
      }
      // Pokud úspěch, loading screen zůstane zobrazený
      // Po minimálním delay (3s) může být přesměrování nebo success screen
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Neznámá chyba');
      setIsSubmitting(false);
    }
  };

  if (isSubmitting) {
    return <LoadingScreen />;
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-50 to-slate-100 overflow-hidden">
      {/* Progress Bar */}
      <ProgressBar progress={progress} />

      {/* Live Activity Panel */}
      <LiveActivityPanel />

      {/* Main Content */}
      <div className="flex items-center justify-center min-h-screen p-4">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-2xl"
        >
          <AnimatePresence mode="wait">
            {currentStep === 'intro' && (
              <IntroStep onNext={handleNext} />
            )}
            {currentStep === 'cil' && (
              <CilStep
                value={formData.inputTransform.hlavni_cil}
                onNext={handleNext}
                onDataChange={(data) => handleStepData('cil', data)}
              />
            )}
            {currentStep === 'oblast' && (
              <OblastStep
                value={formData.inputTransform.obor}
                onNext={handleNext}
                onBack={handleBack}
                onDataChange={(data) => handleStepData('oblast', data)}
              />
            )}
            {currentStep === 'uroven' && (
              <UrovenStep
                value={formData.inputTransform.seniorita}
                onNext={handleNext}
                onBack={handleBack}
                onDataChange={(data) => handleStepData('uroven', data)}
              />
            )}
            {currentStep === 'konkretnost' && (
              <KonkretnostStep
                value={formData.inputTransform.konkretnost}
                onNext={handleNext}
                onBack={handleBack}
                onDataChange={(data) => handleStepData('konkretnost', data)}
              />
            )}
            {currentStep === 'casovy_horizont' && (
              <CasovyHorizontStep
                value={formData.inputTransform.casovy_horizont}
                onNext={handleNext}
                onBack={handleBack}
                onDataChange={(data) => handleStepData('casovy_horizont', data)}
              />
            )}
            {currentStep === 'email' && (
              <EmailStep
                email={formData.email}
                name={formData.name}
                onBack={handleBack}
                onSubmit={handleSubmit}
                onDataChange={(data) => handleStepData('email', data)}
                error={submitError}
              />
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
