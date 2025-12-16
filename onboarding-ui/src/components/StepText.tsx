import { motion } from 'framer-motion';

interface StepTextProps {
  title: string;
  subtitle?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string | null;
}

export function StepText({
  title,
  subtitle,
  placeholder,
  value,
  onChange,
  error,
}: StepTextProps) {
  const charCount = value.trim().length;
  const minChars = 20;
  const isValid = charCount >= minChars;

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

      {/* Textarea */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.3 }}
      >
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={5}
          className="input-field resize-none"
          autoFocus
        />
        
        {/* Character count */}
        <div className="flex justify-between items-center mt-2">
          <p className="text-xs text-surface-500">
            {isValid ? (
              <span className="text-green-400">✓ Dostatečně podrobné</span>
            ) : (
              <span>Ještě {minChars - charCount} znaků</span>
            )}
          </p>
          <p className="text-xs text-surface-500">
            {charCount} znaků
          </p>
        </div>
      </motion.div>

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
