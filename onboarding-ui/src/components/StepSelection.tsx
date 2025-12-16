import { motion } from 'framer-motion';
import clsx from 'clsx';
import { StepOption } from '../types';

interface StepSelectionProps {
  title: string;
  subtitle?: string;
  options: StepOption[];
  value: string;
  onChange: (value: string) => void;
  error?: string | null;
}

export function StepSelection({
  title,
  subtitle,
  options,
  value,
  onChange,
  error,
}: StepSelectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-xl mx-auto"
    >
      {/* Title */}
      <motion.h2
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="text-2xl md:text-3xl font-bold text-white text-center mb-2"
      >
        {title}
      </motion.h2>

      {subtitle && (
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.3 }}
          className="text-surface-400 text-center mb-8"
        >
          {subtitle}
        </motion.p>
      )}

      {/* Options grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {options.map((option, index) => (
          <motion.button
            key={option.value}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + index * 0.05, duration: 0.3 }}
            onClick={() => onChange(option.value)}
            className={clsx(
              'option-card text-left',
              value === option.value && 'selected'
            )}
          >
            {option.icon && (
              <span className="text-2xl flex-shrink-0">{option.icon}</span>
            )}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-white">{option.label}</p>
              {option.description && (
                <p className="text-sm text-surface-400 mt-0.5">
                  {option.description}
                </p>
              )}
            </div>
            {/* Selection indicator */}
            <div
              className={clsx(
                'w-5 h-5 rounded-full border-2 flex-shrink-0 flex items-center justify-center transition-colors',
                value === option.value
                  ? 'border-primary-500 bg-primary-500'
                  : 'border-surface-500'
              )}
            >
              {value === option.value && (
                <motion.svg
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-3 h-3 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </motion.svg>
              )}
            </div>
          </motion.button>
        ))}
      </div>

      {/* Error message */}
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-red-400 text-sm text-center mt-4"
        >
          {error}
        </motion.p>
      )}
    </motion.div>
  );
}
