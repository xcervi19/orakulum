import { motion } from 'framer-motion';

interface StepIntroProps {
  onContinue: () => void;
}

export function StepIntro({ onContinue }: StepIntroProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="text-center max-w-lg mx-auto"
    >
      {/* Logo/Icon */}
      <motion.div
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="w-20 h-20 mx-auto mb-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/20"
      >
        <span className="text-4xl">🔮</span>
      </motion.div>

      {/* Title */}
      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.4 }}
        className="text-3xl md:text-4xl font-bold text-white mb-4"
      >
        Vítejte v Orakulum
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
        className="text-lg text-surface-300 mb-8 leading-relaxed"
      >
        Vytvořte si osobní kariérní plán na míru.
        <br />
        Zabere to jen pár minut.
      </motion.p>

      {/* Features list */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.4 }}
        className="flex flex-col gap-3 mb-10 text-left"
      >
        {[
          { icon: '🎯', text: 'Personalizovaný plán podle vašich cílů' },
          { icon: '📚', text: 'Konkrétní kroky a zdroje ke studiu' },
          { icon: '📈', text: 'Sledování pokroku a milníků' },
        ].map((item, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 + index * 0.1, duration: 0.3 }}
            className="flex items-center gap-3 bg-surface-800/50 rounded-lg p-3"
          >
            <span className="text-xl">{item.icon}</span>
            <span className="text-surface-200">{item.text}</span>
          </motion.div>
        ))}
      </motion.div>

      {/* CTA Button */}
      <motion.button
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9, duration: 0.4 }}
        onClick={onContinue}
        className="btn-primary text-lg px-10 py-4 shadow-lg shadow-primary-500/20"
      >
        Začít →
      </motion.button>
    </motion.div>
  );
}
