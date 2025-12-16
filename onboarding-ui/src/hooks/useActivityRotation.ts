import { useState, useEffect, useCallback, useRef } from 'react';
import { ActivityItem } from '../types';
import { ACTIVITY_ITEMS, SCORE_UPDATES } from '../data/activity';

const ROTATION_INTERVAL_MIN = 6000; // 6 seconds
const ROTATION_INTERVAL_MAX = 8000; // 8 seconds

function getRandomInterval(): number {
  return Math.floor(
    Math.random() * (ROTATION_INTERVAL_MAX - ROTATION_INTERVAL_MIN) + ROTATION_INTERVAL_MIN
  );
}

function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export function useActivityRotation() {
  const [currentActivity, setCurrentActivity] = useState<ActivityItem>(ACTIVITY_ITEMS[0]);
  const [currentScore, setCurrentScore] = useState<string>(SCORE_UPDATES[0]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Use refs to track queue and index without causing re-renders
  const activityQueueRef = useRef<ActivityItem[]>(shuffleArray(ACTIVITY_ITEMS));
  const activityIndexRef = useRef(0);

  const rotateActivity = useCallback(() => {
    setIsTransitioning(true);
    
    setTimeout(() => {
      const nextIndex = (activityIndexRef.current + 1) % activityQueueRef.current.length;
      
      // Reshuffle when we've gone through all items
      if (nextIndex === 0) {
        activityQueueRef.current = shuffleArray(ACTIVITY_ITEMS);
      }
      
      activityIndexRef.current = nextIndex;
      setCurrentActivity(activityQueueRef.current[nextIndex]);
      
      // Also rotate score update
      setCurrentScore(prev => {
        const currentScoreIndex = SCORE_UPDATES.indexOf(prev);
        const nextScoreIndex = (currentScoreIndex + 1) % SCORE_UPDATES.length;
        return SCORE_UPDATES[nextScoreIndex];
      });
      
      setIsTransitioning(false);
    }, 300); // Transition duration
  }, []);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;
    
    const scheduleNextRotation = () => {
      const interval = getRandomInterval();
      timeoutId = setTimeout(() => {
        rotateActivity();
        scheduleNextRotation();
      }, interval);
    };
    
    scheduleNextRotation();
    
    return () => {
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [rotateActivity]);

  return {
    currentActivity,
    currentScore,
    isTransitioning,
  };
}
