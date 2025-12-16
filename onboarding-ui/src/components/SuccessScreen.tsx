import { motion } from 'framer-motion';

interface SuccessScreenProps {
  email: string;
}

export function SuccessScreen({ email }: SuccessScreenProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen flex items-center justify-center p-6"
    >
      <div className="max-w-md w-full text-center">
        {/* Success icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          className="w-24 h-24 mx-auto mb-8 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center shadow-lg shadow-green-500/30"
        >
          <motion.svg
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="w-12 h-12 text-white"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <motion.path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={3}
              d="M5 13l4 4L19 7"
            />
          </motion.svg>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-3xl font-bold text-white mb-4"
        >
          Váš plán je připraven!
        </motion.h1>

        {/* Description */}
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="text-surface-300 mb-6"
        >
          Poslali jsme vám přístupový odkaz na
        </motion.p>

        {/* Email badge */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="inline-flex items-center gap-2 bg-surface-800 border border-surface-700 rounded-lg px-4 py-2 mb-8"
        >
          <svg className="w-5 h-5 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
          <span className="text-white font-medium">{email}</span>
        </motion.div>

        {/* What's next */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-surface-800/50 rounded-xl p-6 text-left"
        >
          <h3 className="text-sm font-semibold text-surface-300 uppercase tracking-wide mb-4">
            Co vás čeká
          </h3>
          <ul className="space-y-3">
            {[
              'Personalizovaný kariérní plán',
              'Konkrétní kroky a milníky',
              'Doporučené zdroje a materiály',
              'Sledování vašeho pokroku',
            ].map((item, index) => (
              <motion.li
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.9 + index * 0.1 }}
                className="flex items-center gap-3 text-surface-200"
              >
                <span className="w-5 h-5 bg-primary-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="w-2 h-2 bg-primary-500 rounded-full" />
                </span>
                {item}
              </motion.li>
            ))}
          </ul>
        </motion.div>

        {/* Note */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.3 }}
          className="text-xs text-surface-500 mt-6"
        >
          Zkontrolujte svou schránku včetně složky spam.
        </motion.p>
      </div>
    </motion.div>
  );
}
