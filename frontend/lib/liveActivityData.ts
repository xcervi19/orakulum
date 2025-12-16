/**
 * Statická data pro Live Activity Panel
 * Rotující pasivní signály aktivity
 */

import { LiveActivityItem } from '@/types/onboarding';

export const LIVE_ACTIVITY_ITEMS: LiveActivityItem[] = [
  {
    avatar: '👨‍💻',
    role: 'Backend Engineer',
    action: 'dokončil plán',
  },
  {
    avatar: '📊',
    role: 'Interview Readiness Score',
    action: '+6',
  },
  {
    avatar: '👩‍💻',
    role: 'Frontend Developer',
    action: 'zahájil trénink',
  },
  {
    avatar: '🎯',
    role: 'Data Scientist',
    action: 'dokončil krok 5',
  },
  {
    avatar: '⚡',
    role: 'Full Stack Developer',
    action: 'zlepšil skóre',
  },
  {
    avatar: '🚀',
    role: 'DevOps Engineer',
    action: 'dokončil plán',
  },
  {
    avatar: '💡',
    role: 'Product Manager',
    action: 'zahájil nový plán',
  },
  {
    avatar: '🎨',
    role: 'UI/UX Designer',
    action: 'dokončil trénink',
  },
];

export const MICRO_COPY_ITEMS = [
  'Tento týden vytvořeno několik plánů',
  'Aktivní uživatelé tento měsíc',
  'Nové plány se připravují',
];
