import { motion } from 'framer-motion';

interface NavigationButtonsProps {
  onPrev?: () => void;
  onNext: () => void;
  showPrev?: boolean;
  isLastStep?: boolean;
  isSubmitting?: boolean;
  disabled?: boolean;
}

export function NavigationButtons({
  onPrev,
  onNext,
  showPrev = true,
  isLastStep = false,
  isSubmitting = false,
  disabled = false,
}: NavigationButtonsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3, duration: 0.3 }}
      className="flex justify-center gap-4 mt-10"
    >
      {showPrev && onPrev && (
        <button
          onClick={onPrev}
          disabled={isSubmitting}
          className="btn-secondary"
        >
          ← Zpět
        </button>
      )}
      
      <button
        onClick={onNext}
        disabled={disabled || isSubmitting}
        className="btn-primary min-w-[140px] flex items-center justify-center gap-2"
      >
        {isSubmitting ? (
          <>
            <motion.div
              className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
            <span>Odesílám...</span>
          </>
        ) : isLastStep ? (
          'Vytvořit plán →'
        ) : (
          'Pokračovat →'
        )}
      </button>
    </motion.div>
  );
}
