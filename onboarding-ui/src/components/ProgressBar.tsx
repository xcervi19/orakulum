import { motion } from 'framer-motion';

interface ProgressBarProps {
  progress: number;
  currentStep: number;
  totalSteps: number;
}

export function ProgressBar({ progress, currentStep, totalSteps }: ProgressBarProps) {
  return (
    <div className="w-full max-w-md mx-auto mb-8">
      {/* Step indicator */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-surface-400">
          Krok {currentStep + 1} z {totalSteps}
        </span>
        <span className="text-sm text-surface-400">
          {Math.round(progress)}%
        </span>
      </div>
      
      {/* Progress track */}
      <div className="h-1.5 bg-surface-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}
