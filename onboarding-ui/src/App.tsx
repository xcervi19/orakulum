import { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { useOnboarding } from './hooks';
import { STEPS } from './data/steps';
import {
  ProgressBar,
  LiveActivityPanel,
  ProcessingScreen,
  StepIntro,
  StepSelection,
  StepText,
  StepEmail,
  NavigationButtons,
  SuccessScreen,
} from './components';
import { OnboardingFormData } from './types';

function App() {
  const {
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
  } = useOnboarding();

  const [showProcessing, setShowProcessing] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const currentStepConfig = STEPS[currentStep];

  // Handle form submission with processing screen
  const onSubmit = async () => {
    setShowProcessing(true);
    await handleSubmit();
  };

  // Handle processing complete
  const onProcessingComplete = () => {
    setShowProcessing(false);
    setShowSuccess(true);
  };

  // Show success screen after processing
  if (showSuccess && isComplete) {
    return <SuccessScreen email={formData.email} />;
  }

  // Render step content
  const renderStepContent = () => {
    const stepConfig = currentStepConfig;
    const fieldKey = stepConfig.key as keyof OnboardingFormData;

    switch (stepConfig.type) {
      case 'intro':
        return <StepIntro onContinue={goToNextStep} />;

      case 'selection':
        return (
          <>
            <StepSelection
              title={stepConfig.title}
              subtitle={stepConfig.subtitle}
              options={stepConfig.options || []}
              value={formData[fieldKey] || ''}
              onChange={(value) => updateField(fieldKey, value)}
              error={error}
            />
            <NavigationButtons
              onPrev={goToPrevStep}
              onNext={goToNextStep}
              showPrev={!isFirstStep}
            />
          </>
        );

      case 'text':
        return (
          <>
            <StepText
              title={stepConfig.title}
              subtitle={stepConfig.subtitle}
              placeholder={stepConfig.placeholder}
              value={formData[fieldKey] || ''}
              onChange={(value) => updateField(fieldKey, value)}
              error={error}
            />
            <NavigationButtons
              onPrev={goToPrevStep}
              onNext={goToNextStep}
              showPrev={!isFirstStep}
            />
          </>
        );

      case 'email':
        return (
          <>
            <StepEmail
              title={stepConfig.title}
              subtitle={stepConfig.subtitle}
              placeholder={stepConfig.placeholder}
              value={formData[fieldKey] || ''}
              onChange={(value) => updateField(fieldKey, value)}
              error={error}
            />
            <NavigationButtons
              onPrev={goToPrevStep}
              onNext={onSubmit}
              showPrev={!isFirstStep}
              isLastStep={isLastStep}
              isSubmitting={isSubmitting}
            />
          </>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-surface-950 relative overflow-hidden">
      {/* Background gradient */}
      <div className="fixed inset-0 bg-gradient-to-br from-surface-900 via-surface-950 to-surface-950 pointer-events-none" />
      
      {/* Subtle grid pattern */}
      <div 
        className="fixed inset-0 opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      {/* Live Activity Panel (desktop only) */}
      <LiveActivityPanel />

      {/* Main content */}
      <main className="relative z-10 min-h-screen flex flex-col items-center justify-center p-6">
        {/* Progress bar - hidden on intro step */}
        {currentStep > 0 && (
          <div className="w-full max-w-xl mb-8">
            <ProgressBar
              progress={progress}
              currentStep={currentStep}
              totalSteps={totalSteps}
            />
          </div>
        )}

        {/* Step content */}
        <div className="w-full max-w-2xl">
          <AnimatePresence mode="wait">
            <div key={currentStep}>{renderStepContent()}</div>
          </AnimatePresence>
        </div>
      </main>

      {/* Processing overlay */}
      <AnimatePresence>
        {showProcessing && (
          <ProcessingScreen
            isActive={showProcessing}
            onComplete={onProcessingComplete}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
