'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LIVE_ACTIVITY_ITEMS, MICRO_COPY_ITEMS } from '@/lib/liveActivityData';
import { LiveActivityItem } from '@/types/onboarding';

const ROTATION_INTERVAL = 7000; // 6-8 sekund

export function LiveActivityPanel() {
  const [currentItem, setCurrentItem] = useState<LiveActivityItem>(LIVE_ACTIVITY_ITEMS[0]);
  const [currentMicroCopy, setCurrentMicroCopy] = useState<string>(MICRO_COPY_ITEMS[0]);
  const [itemIndex, setItemIndex] = useState(0);
  const [microCopyIndex, setMicroCopyIndex] = useState(0);

  useEffect(() => {
    // Rotace hlavních aktivit
    const itemInterval = setInterval(() => {
      setItemIndex((prev) => {
        const next = (prev + 1) % LIVE_ACTIVITY_ITEMS.length;
        setCurrentItem(LIVE_ACTIVITY_ITEMS[next]);
        return next;
      });
    }, ROTATION_INTERVAL);

    // Rotace mikro-kopie (pomaleji)
    const microCopyInterval = setInterval(() => {
      setMicroCopyIndex((prev) => {
        const next = (prev + 1) % MICRO_COPY_ITEMS.length;
        setCurrentMicroCopy(MICRO_COPY_ITEMS[next]);
        return next;
      });
    }, ROTATION_INTERVAL * 2);

    return () => {
      clearInterval(itemInterval);
      clearInterval(microCopyInterval);
    };
  }, []);

  return (
    <div className="fixed bottom-6 right-6 z-40 pointer-events-none">
      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-4 max-w-xs border border-slate-200">
        {/* Hlavní aktivita */}
        <AnimatePresence mode="wait">
          <motion.div
            key={itemIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.4 }}
            className="flex items-center gap-3 mb-2"
          >
            <div className="text-2xl">{currentItem.avatar}</div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-slate-900 truncate">
                {currentItem.role}
              </div>
              <div className="text-xs text-slate-600">
                {currentItem.action}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>

        {/* Mikro-kopie */}
        <AnimatePresence mode="wait">
          <motion.div
            key={microCopyIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="text-xs text-slate-500 pt-2 border-t border-slate-200"
          >
            {currentMicroCopy}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
