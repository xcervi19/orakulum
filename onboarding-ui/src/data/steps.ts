import { StepConfig } from '../types';

export const STEPS: StepConfig[] = [
  {
    id: 0,
    key: 'intro',
    title: 'Vítejte v Orakulum',
    subtitle: 'Vytvořte si osobní kariérní plán na míru během několika minut.',
    type: 'intro',
  },
  {
    id: 1,
    key: 'goal',
    title: 'Jaký je váš hlavní cíl?',
    subtitle: 'Vyberte, co nejlépe vystihuje vaši kariérní ambici.',
    type: 'selection',
    options: [
      { 
        value: 'first_job', 
        label: 'Získat první práci v IT',
        description: 'Chci se prosadit a nastartovat svou kariéru',
        icon: '🚀'
      },
      { 
        value: 'career_change', 
        label: 'Změnit kariéru',
        description: 'Chci přejít do IT z jiného oboru',
        icon: '🔄'
      },
      { 
        value: 'level_up', 
        label: 'Posunout se výš',
        description: 'Chci růst v aktuální pozici',
        icon: '📈'
      },
      { 
        value: 'specialize', 
        label: 'Specializovat se',
        description: 'Chci se stát expertem v konkrétní oblasti',
        icon: '🎯'
      },
    ],
  },
  {
    id: 2,
    key: 'area',
    title: 'Jaká oblast vás zajímá?',
    subtitle: 'Vyberte technickou oblast, které se chcete věnovat.',
    type: 'selection',
    options: [
      { 
        value: 'frontend', 
        label: 'Frontend Development',
        description: 'React, Vue, Angular, webové aplikace',
        icon: '🎨'
      },
      { 
        value: 'backend', 
        label: 'Backend Development',
        description: 'Node.js, Python, Java, API, databáze',
        icon: '⚙️'
      },
      { 
        value: 'fullstack', 
        label: 'Fullstack Development',
        description: 'Kompletní vývoj webových aplikací',
        icon: '🔗'
      },
      { 
        value: 'mobile', 
        label: 'Mobile Development',
        description: 'iOS, Android, React Native, Flutter',
        icon: '📱'
      },
      { 
        value: 'data', 
        label: 'Data & Analytics',
        description: 'Data science, ML, analýza dat',
        icon: '📊'
      },
      { 
        value: 'devops', 
        label: 'DevOps & Cloud',
        description: 'AWS, Docker, Kubernetes, CI/CD',
        icon: '☁️'
      },
    ],
  },
  {
    id: 3,
    key: 'level',
    title: 'Jaká je vaše aktuální úroveň?',
    subtitle: 'Buďte upřímní – plán přizpůsobíme vašim zkušenostem.',
    type: 'selection',
    options: [
      { 
        value: 'beginner', 
        label: 'Úplný začátečník',
        description: 'Teprve začínám, mám minimum zkušeností',
        icon: '🌱'
      },
      { 
        value: 'learning', 
        label: 'Učím se',
        description: 'Absolvoval/a jsem kurzy, tvořím projekty',
        icon: '📚'
      },
      { 
        value: 'junior', 
        label: 'Junior',
        description: 'Mám základní komerční zkušenosti',
        icon: '💼'
      },
      { 
        value: 'mid', 
        label: 'Mid-level',
        description: 'Pracuji samostatně, 2-4 roky praxe',
        icon: '🏆'
      },
    ],
  },
  {
    id: 4,
    key: 'specificity',
    title: 'Upřesněte svou situaci',
    subtitle: 'Čím konkrétnější informace, tím přesnější plán.',
    type: 'text',
    placeholder: 'Např.: Učím se JavaScript 6 měsíců, vytvořil jsem pár projektů v Reactu, hledám první práci jako frontend developer...',
    validation: (value: string) => value.trim().length >= 20,
  },
  {
    id: 5,
    key: 'timeHorizon',
    title: 'Jaký je váš časový horizont?',
    subtitle: 'Za jak dlouho byste chtěl/a dosáhnout svého cíle?',
    type: 'selection',
    options: [
      { 
        value: '3_months', 
        label: '3 měsíce',
        description: 'Intenzivní tempo, rychlé výsledky',
        icon: '⚡'
      },
      { 
        value: '6_months', 
        label: '6 měsíců',
        description: 'Vyvážené tempo, důkladná příprava',
        icon: '📅'
      },
      { 
        value: '12_months', 
        label: '12 měsíců',
        description: 'Dlouhodobý plán, hluboké znalosti',
        icon: '🎯'
      },
      { 
        value: 'flexible', 
        label: 'Flexibilní',
        description: 'Nemám pevný termín',
        icon: '🌊'
      },
    ],
  },
  {
    id: 6,
    key: 'email',
    title: 'Kam vám máme poslat plán?',
    subtitle: 'Zadejte email pro přístup k vašemu osobnímu prostoru.',
    type: 'email',
    placeholder: 'vas@email.cz',
    validation: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
  },
];

export const TOTAL_STEPS = STEPS.length;
