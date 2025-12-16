/**
 * Orakulum Onboarding
 * Modern onboarding flow with live activity panel
 */

// ============================================
// State Management
// ============================================
const state = {
    currentStep: 0,
    totalSteps: 7,
    formData: {
        goal: null,
        area: null,
        level: null,
        description: '',
        timeline: null,
        name: '',
        email: ''
    }
};

// ============================================
// Live Activity Data
// ============================================
const ACTIVITY_DATA = [
    { avatar: '👨‍💻', role: 'Backend Engineer', action: 'dokončil osobní plán' },
    { avatar: '👩‍💼', role: 'Frontend Developer', action: 'zahájil trénink' },
    { avatar: '🎯', role: 'Junior Developer', action: 'Interview Readiness Score +8' },
    { avatar: '💡', role: 'Full-Stack Developer', action: 'aktualizoval profil' },
    { avatar: '🚀', role: 'Data Analyst', action: 'dokončil lekci SQL' },
    { avatar: '⚡', role: 'DevOps Engineer', action: 'zahájil projekt deployment' },
    { avatar: '🎨', role: 'UI/UX Designer', action: 'přidal nové portfolio' },
    { avatar: '📊', role: 'Product Manager', action: 'vytvořil roadmapu' },
    { avatar: '🔧', role: 'Mobile Developer', action: 'dokončil React Native kurz' },
    { avatar: '🌟', role: 'Tech Lead', action: 'sdílel zkušenosti' },
    { avatar: '💼', role: 'Career Switcher', action: 'získal první práci' },
    { avatar: '🎓', role: 'Junior Frontend', action: 'Interview Readiness Score +12' },
    { avatar: '⚙️', role: 'System Administrator', action: 'dokončil certifikaci AWS' },
    { avatar: '🔐', role: 'Security Analyst', action: 'zahájil bug bounty' },
    { avatar: '📱', role: 'iOS Developer', action: 'vydal první aplikaci' },
];

let activityInterval = null;
let activityIndex = 0;

// ============================================
// Loading Steps Data
// ============================================
const LOADING_STEPS = [
    'Analyzujeme váš cíl',
    'Mapujeme příležitosti',
    'Vytváříme personalizovaný plán',
    'Připravujeme váš osobní prostor',
    'Finalizujeme detaily'
];

let loadingStepIndex = 0;
let loadingInterval = null;

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeOnboarding();
    startLiveActivity();
    setupCharacterCounter();
});

function initializeOnboarding() {
    updateProgress();
    updateNavigationButtons();
}

// ============================================
// Live Activity Panel
// ============================================
function startLiveActivity() {
    const activityList = document.getElementById('activityList');
    
    // Show initial 3 activities
    for (let i = 0; i < 3; i++) {
        addActivityItem(i);
    }
    
    activityIndex = 3;
    
    // Rotate activities every 6-8 seconds
    activityInterval = setInterval(() => {
        rotateActivity();
    }, getRandomInterval(6000, 8000));
}

function addActivityItem(index) {
    const activityList = document.getElementById('activityList');
    const data = ACTIVITY_DATA[index % ACTIVITY_DATA.length];
    
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
        <div class="activity-avatar">${data.avatar}</div>
        <div class="activity-content">
            <div class="activity-role">${data.role}</div>
            <div class="activity-action">${data.action}</div>
        </div>
    `;
    
    activityList.appendChild(item);
    
    // Trigger animation
    setTimeout(() => {
        item.style.opacity = '1';
    }, 50);
}

function rotateActivity() {
    const activityList = document.getElementById('activityList');
    const items = activityList.querySelectorAll('.activity-item');
    
    if (items.length >= 3) {
        // Remove oldest item (first)
        const oldestItem = items[0];
        oldestItem.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
        oldestItem.style.opacity = '0';
        oldestItem.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            oldestItem.remove();
        }, 300);
    }
    
    // Add new item
    setTimeout(() => {
        addActivityItem(activityIndex);
        activityIndex = (activityIndex + 1) % ACTIVITY_DATA.length;
    }, 150);
}

function getRandomInterval(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ============================================
// Stepper Navigation
// ============================================
function nextStep() {
    if (state.currentStep < state.totalSteps - 1) {
        transitionStep(state.currentStep + 1);
    }
}

function prevStep() {
    if (state.currentStep > 0) {
        transitionStep(state.currentStep - 1, 'backward');
    }
}

function transitionStep(newStep, direction = 'forward') {
    const steps = document.querySelectorAll('.step');
    const currentStepEl = steps[state.currentStep];
    const newStepEl = steps[newStep];
    
    // Exit current step
    currentStepEl.classList.remove('active');
    currentStepEl.classList.add(direction === 'forward' ? 'exiting-left' : 'exiting-right');
    
    // Enter new step
    setTimeout(() => {
        currentStepEl.classList.remove('exiting-left', 'exiting-right');
        newStepEl.classList.add('active');
        
        state.currentStep = newStep;
        updateProgress();
        updateNavigationButtons();
        
        // Scroll to top
        document.getElementById('stepContainer').scrollTop = 0;
    }, 150);
}

function updateProgress() {
    const progressFill = document.getElementById('progressFill');
    const progressLabel = document.getElementById('progressLabel');
    
    const percentage = (state.currentStep / (state.totalSteps - 1)) * 100;
    progressFill.style.width = `${percentage}%`;
    
    if (state.currentStep === 0) {
        progressLabel.textContent = 'Začínáme';
    } else {
        progressLabel.textContent = `Krok ${state.currentStep} z ${state.totalSteps - 1}`;
    }
}

function updateNavigationButtons() {
    const backButton = document.getElementById('backButton');
    
    if (state.currentStep > 0 && state.currentStep < state.totalSteps - 1) {
        backButton.classList.add('visible');
    } else {
        backButton.classList.remove('visible');
    }
}

// ============================================
// Option Selection
// ============================================
function selectOption(field, value) {
    // Store value
    state.formData[field] = value;
    
    // Visual feedback
    const currentStep = document.querySelector('.step.active');
    const options = currentStep.querySelectorAll(`[data-field="${field}"]`);
    
    options.forEach(option => {
        if (option.dataset.value === value) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
    
    // Auto-advance after short delay
    setTimeout(() => {
        nextStep();
    }, 400);
}

// ============================================
// Character Counter
// ============================================
function setupCharacterCounter() {
    const textarea = document.getElementById('description');
    const charCount = document.getElementById('charCount');
    
    if (textarea) {
        textarea.addEventListener('input', () => {
            const count = textarea.value.length;
            charCount.textContent = count;
            state.formData.description = textarea.value;
        });
    }
}

// ============================================
// Validation
// ============================================
function validateAndNextStep(step) {
    switch(step) {
        case 4: // Description step
            const description = document.getElementById('description').value.trim();
            if (description.length < 20) {
                showError('Prosím, popište svou situaci alespoň ve 20 znacích.');
                return;
            }
            state.formData.description = description;
            nextStep();
            break;
        
        default:
            nextStep();
    }
}

function showError(message) {
    // Simple alert for now - can be enhanced with toast notifications
    alert(message);
}

// ============================================
// Form Submission
// ============================================
async function submitOnboarding() {
    // Validate final step
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    
    if (!name || name.length < 2) {
        showError('Prosím, zadejte vaše jméno.');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('Prosím, zadejte platný email.');
        return;
    }
    
    state.formData.name = name;
    state.formData.email = email;
    
    // Validate all required fields
    if (!state.formData.goal || !state.formData.area || !state.formData.level || 
        !state.formData.description || !state.formData.timeline) {
        showError('Prosím, dokončete všechny kroky.');
        return;
    }
    
    // Show loading screen
    showLoadingScreen();
    
    // Prepare payload for API
    const payload = buildPayload();
    
    try {
        // Send to API (configure endpoint as needed)
        await submitToAPI(payload);
        
        // Success - redirect after loading animation completes
        setTimeout(() => {
            redirectToSuccess();
        }, 8000); // Min 8 seconds for loading animation
        
    } catch (error) {
        console.error('Submission error:', error);
        hideLoadingScreen();
        showError('Něco se pokazilo. Prosím, zkuste to znovu.');
    }
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// ============================================
// API Payload Building
// ============================================
function buildPayload() {
    // Map form data to database structure
    // This maintains compatibility with existing junior_leads table
    
    const goalLabels = {
        'first_job': 'První práce v IT',
        'career_switch': 'Změna kariéry do IT',
        'level_up': 'Posun na vyšší úroveň',
        'skill_upgrade': 'Rozšíření dovedností'
    };
    
    const areaLabels = {
        'frontend': 'Frontend Development',
        'backend': 'Backend Development',
        'fullstack': 'Full-Stack Development',
        'mobile': 'Mobile Development',
        'data': 'Data & Analytics',
        'devops': 'DevOps & Cloud'
    };
    
    const levelLabels = {
        'absolute_beginner': 'Absolutní začátečník',
        'beginner': 'Začátečník',
        'intermediate': 'Mírně pokročilý',
        'advanced': 'Pokročilý'
    };
    
    const timelineLabels = {
        '3_months': '3 měsíce',
        '6_months': '6 měsíců',
        '12_months': '12 měsíců',
        'flexible': 'Flexibilně'
    };
    
    // Build description field (combines all info for backward compatibility)
    const description = `${state.formData.description}\n\nCíl: ${goalLabels[state.formData.goal]}\nOblast: ${areaLabels[state.formData.area]}\nÚroveň: ${levelLabels[state.formData.level]}\nČasový horizont: ${timelineLabels[state.formData.timeline]}`;
    
    // Build input_transform field (structured data)
    const inputTransform = {
        obor: areaLabels[state.formData.area],
        seniorita: levelLabels[state.formData.level],
        hlavni_cil: goalLabels[state.formData.goal],
        casovy_horizont: timelineLabels[state.formData.timeline],
        technologie: [],
        raw_description: state.formData.description
    };
    
    return {
        name: state.formData.name,
        email: state.formData.email,
        description: description,
        input_transform: inputTransform,
        status: 'FLAGGED' // Ready for pipeline processing
    };
}

// ============================================
// API Submission
// ============================================
async function submitToAPI(payload) {
    // Configure your API endpoint here
    // For now, using environment variable or default
    const API_ENDPOINT = window.ORAKULUM_API_ENDPOINT || '/api/leads';
    
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
}

// ============================================
// Loading Screen
// ============================================
function showLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    loadingScreen.classList.add('active');
    
    // Start rotating loading steps
    loadingStepIndex = 0;
    updateLoadingStep();
    
    loadingInterval = setInterval(() => {
        loadingStepIndex = (loadingStepIndex + 1) % LOADING_STEPS.length;
        updateLoadingStep();
    }, 1500);
}

function updateLoadingStep() {
    const loadingStep = document.getElementById('loadingStep');
    loadingStep.textContent = LOADING_STEPS[loadingStepIndex];
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    loadingScreen.classList.remove('active');
    
    if (loadingInterval) {
        clearInterval(loadingInterval);
        loadingInterval = null;
    }
}

// ============================================
// Redirect
// ============================================
function redirectToSuccess() {
    // Configure your success page URL
    // Use environment variable or default
    const SUCCESS_URL = window.ORAKULUM_SUCCESS_URL || '/dashboard';
    window.location.href = SUCCESS_URL;
}

// ============================================
// Cleanup
// ============================================
window.addEventListener('beforeunload', () => {
    if (activityInterval) {
        clearInterval(activityInterval);
    }
    if (loadingInterval) {
        clearInterval(loadingInterval);
    }
});

// ============================================
// Export for external use (if needed)
// ============================================
window.OrakulumOnboarding = {
    state,
    nextStep,
    prevStep,
    selectOption,
    validateAndNextStep,
    submitOnboarding
};
