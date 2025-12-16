'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LOADING_STEPS = [
  'Analyzujeme cíl',
  'Mapujeme příležitosti',
  'Připravujeme osobní prostor',
];

const STEP_DURATION = 2000; // 2 sekundy na krok

export function LoadingScreen() {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => {
        const next = (prev + 1) % LOADING_STEPS.length;
        return next;
      });
    }, STEP_DURATION);

    // Minimální delay 3 sekundy
    const minDelayTimeout = setTimeout(() => {
      // Po minimálním delay může pokračovat
    }, 3000);

    return () => {
      clearInterval(interval);
      clearTimeout(minDelayTimeout);
    };
  }, []);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center z-50">
      <div className="text-center">
        {/* Logo nebo ikona */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="w-16 h-16 mx-auto bg-primary-500 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-white animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        </motion.div>

        {/* Rotující kroky */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStepIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.4 }}
            className="text-xl font-medium text-slate-900 mb-2"
          >
            {LOADING_STEPS[currentStepIndex]}
          </motion.div>
        </AnimatePresence>

        {/* Progress dots */}
        <div className="flex justify-center gap-2 mt-4">
          {LOADING_STEPS.map((_, index) => (
            <motion.div
              key={index}
              className={`w-2 h-2 rounded-full ${
                index === currentStepIndex
                  ? 'bg-primary-500'
                  : 'bg-slate-300'
              }`}
              animate={{
                scale: index === currentStepIndex ? 1.2 : 1,
                opacity: index === currentStepIndex ? 1 : 0.5,
              }}
              transition={{ duration: 0.3 }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
