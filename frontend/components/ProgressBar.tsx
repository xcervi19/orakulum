'use client';

import { motion } from 'framer-motion';

interface ProgressBarProps {
  progress: number; // 0-100
}

export function ProgressBar({ progress }: ProgressBarProps) {
  return (
    <div className="fixed top-0 left-0 right-0 h-1 bg-slate-200 z-50">
      <motion.div
        className="h-full bg-gradient-to-r from-primary-500 to-primary-600"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
      />
    </div>
  );
}
