import { ActivityItem, ProcessingStep } from '../types';

// Static activity data - rotates every 6-8 seconds
// These are passive, non-clickable signals of platform activity
export const ACTIVITY_ITEMS: ActivityItem[] = [
  {
    id: '1',
    avatar: '👨‍💻',
    role: 'Backend Engineer',
    action: 'dokončil kariérní plán',
  },
  {
    id: '2',
    avatar: '👩‍🎨',
    role: 'Frontend Developer',
    action: 'zahájil trénink',
  },
  {
    id: '3',
    avatar: '🧑‍💼',
    role: 'Product Manager',
    action: 'přešel do IT',
  },
  {
    id: '4',
    avatar: '👨‍🔬',
    role: 'Data Analyst',
    action: 'dosáhl milníku',
  },
  {
    id: '5',
    avatar: '👩‍💻',
    role: 'Fullstack Developer',
    action: 'získal certifikaci',
  },
  {
    id: '6',
    avatar: '🧑‍🎓',
    role: 'Junior Developer',
    action: 'dokončil 1. modul',
  },
  {
    id: '7',
    avatar: '👨‍🏫',
    role: 'DevOps Engineer',
    action: 'splnil výzvu',
  },
  {
    id: '8',
    avatar: '👩‍🔧',
    role: 'Mobile Developer',
    action: 'aktualizoval plán',
  },
];

// Score changes shown alongside activity
export const SCORE_UPDATES = [
  'Interview Readiness +6',
  'Technical Skills +4',
  'Portfolio Score +8',
  'Learning Progress +12',
  'Career Match +5',
  'Skill Coverage +7',
];

// Processing steps shown after form submission
export const PROCESSING_STEPS: ProcessingStep[] = [
  {
    id: 'analyze',
    text: 'Analyzujeme váš cíl',
    duration: 800,
  },
  {
    id: 'map',
    text: 'Mapujeme příležitosti',
    duration: 900,
  },
  {
    id: 'skills',
    text: 'Vyhodnocujeme dovednosti',
    duration: 700,
  },
  {
    id: 'plan',
    text: 'Sestavujeme plán',
    duration: 850,
  },
  {
    id: 'prepare',
    text: 'Připravujeme osobní prostor',
    duration: 750,
  },
];

// Passive micro-copy signals
export const MICRO_COPY = {
  weeklyPlans: 'Tento týden vytvořeno několik plánů',
  activeUsers: 'Právě aktivních několik uživatelů',
  recentSuccess: 'Nedávno dosaženo více milníků',
};
