import { motion, AnimatePresence } from 'framer-motion';
import { useActivityRotation } from '../hooks';
import { MICRO_COPY } from '../data/activity';

export function LiveActivityPanel() {
  const { currentActivity, currentScore, isTransitioning } = useActivityRotation();

  return (
    <div className="fixed right-6 top-1/2 -translate-y-1/2 w-72 pointer-events-none hidden lg:block">
      {/* Activity Card */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1, duration: 0.5 }}
        className="bg-surface-800/60 backdrop-blur-sm border border-surface-700/50 rounded-xl p-4 mb-4"
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse-subtle" />
          <span className="text-xs text-surface-400 uppercase tracking-wide">
            Živá aktivita
          </span>
        </div>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={currentActivity.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: isTransitioning ? 0 : 1, y: isTransitioning ? -10 : 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="flex items-center gap-3"
          >
            <div className="w-10 h-10 bg-surface-700 rounded-full flex items-center justify-center text-xl">
              {currentActivity.avatar}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {currentActivity.role}
              </p>
              <p className="text-xs text-surface-400 truncate">
                {currentActivity.action}
              </p>
            </div>
          </motion.div>
        </AnimatePresence>
      </motion.div>

      {/* Score Update */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.3, duration: 0.5 }}
        className="bg-primary-500/10 border border-primary-500/20 rounded-xl p-4 mb-4"
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentScore}
            initial={{ opacity: 0 }}
            animate={{ opacity: isTransitioning ? 0 : 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="flex items-center gap-2"
          >
            <span className="text-primary-400 text-lg">📈</span>
            <span className="text-sm text-primary-300 font-medium">
              {currentScore}
            </span>
          </motion.div>
        </AnimatePresence>
      </motion.div>

      {/* Micro-copy signal */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 1.6, duration: 0.5 }}
        className="text-center"
      >
        <p className="text-xs text-surface-500">
          {MICRO_COPY.weeklyPlans}
        </p>
      </motion.div>
    </div>
  );
}
