import { useState, useEffect, useCallback } from 'react';
import { PROCESSING_STEPS } from '../data/activity';

export function useProcessingSteps(isActive: boolean) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState(0);

  const currentStep = PROCESSING_STEPS[currentStepIndex];
  const totalSteps = PROCESSING_STEPS.length;

  const reset = useCallback(() => {
    setCurrentStepIndex(0);
    setIsComplete(false);
    setProgress(0);
  }, []);

  useEffect(() => {
    if (!isActive) {
      reset();
      return;
    }

    let timeoutId: ReturnType<typeof setTimeout>;
    let progressInterval: ReturnType<typeof setInterval>;

    const runStep = (stepIndex: number) => {
      if (stepIndex >= totalSteps) {
        setIsComplete(true);
        setProgress(100);
        return;
      }

      const step = PROCESSING_STEPS[stepIndex];
      setCurrentStepIndex(stepIndex);
      
      // Animate progress within this step
      const stepStartProgress = (stepIndex / totalSteps) * 100;
      const stepEndProgress = ((stepIndex + 1) / totalSteps) * 100;
      const progressIncrement = (stepEndProgress - stepStartProgress) / (step.duration / 50);
      
      let currentProgress = stepStartProgress;
      progressInterval = setInterval(() => {
        currentProgress += progressIncrement;
        if (currentProgress >= stepEndProgress) {
          currentProgress = stepEndProgress;
          clearInterval(progressInterval);
        }
        setProgress(currentProgress);
      }, 50);

      timeoutId = setTimeout(() => {
        clearInterval(progressInterval);
        runStep(stepIndex + 1);
      }, step.duration);
    };

    // Start processing
    runStep(0);

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (progressInterval) clearInterval(progressInterval);
    };
  }, [isActive, totalSteps, reset]);

  return {
    currentStep,
    currentStepIndex,
    isComplete,
    progress,
    totalSteps,
  };
}
