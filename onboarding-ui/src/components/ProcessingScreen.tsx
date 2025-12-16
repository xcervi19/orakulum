import { motion } from 'framer-motion';
import { useProcessingSteps } from '../hooks';

interface ProcessingScreenProps {
  isActive: boolean;
  onComplete: () => void;
}

export function ProcessingScreen({ isActive, onComplete }: ProcessingScreenProps) {
  const { currentStep, progress, isComplete } = useProcessingSteps(isActive);

  // Trigger completion callback
  if (isComplete && isActive) {
    setTimeout(onComplete, 500);
  }

  if (!isActive) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-surface-950 z-50 flex items-center justify-center"
    >
      <div className="max-w-md w-full px-6 text-center">
        {/* Animated loader */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="w-20 h-20 mx-auto relative">
            {/* Outer ring */}
            <motion.div
              className="absolute inset-0 border-4 border-surface-700 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            />
            {/* Inner ring with gradient */}
            <motion.div
              className="absolute inset-2 border-4 border-transparent border-t-primary-500 rounded-full"
              animate={{ rotate: -360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            />
            {/* Center dot */}
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div
                className="w-3 h-3 bg-primary-500 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
            </div>
          </div>
        </motion.div>

        {/* Current step text */}
        <motion.div
          key={currentStep?.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="mb-6"
        >
          <h2 className="text-xl font-semibold text-white mb-2">
            {currentStep?.text || 'Dokončujeme...'}
          </h2>
          <p className="text-surface-400 text-sm">
            Chvilku strpení, připravujeme váš osobní plán
          </p>
        </motion.div>

        {/* Progress bar */}
        <div className="h-1.5 bg-surface-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>
        
        <p className="text-surface-500 text-xs mt-3">
          {Math.round(progress)}%
        </p>
      </div>
    </motion.div>
  );
}
