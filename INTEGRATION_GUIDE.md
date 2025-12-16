# Orakulum Onboarding - Integration Guide

Tento průvodce vám ukáže, jak integrovat onboarding do vaší existující aplikace.

---

## 🎯 Scénář 1: Standalone Onboarding

**Use Case**: Onboarding jako samostatná stránka před vstupem do aplikace.

### Implementace

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Orakulum - Začněte</title>
    <script>
        window.ORAKULUM_API_ENDPOINT = 'https://api.yourdomain.com/api/leads';
        window.ORAKULUM_SUCCESS_URL = 'https://app.yourdomain.com/dashboard';
    </script>
</head>
<body>
    <!-- Redirect to onboarding -->
    <script>window.location.href = '/onboarding.html';</script>
</body>
</html>
```

### Routing (Nginx)

```nginx
location / {
    # Check if user is authenticated
    if ($cookie_auth_token = "") {
        return 302 /onboarding.html;
    }
    
    # Serve app
    try_files $uri /index.html;
}

location /onboarding.html {
    add_header Cache-Control "no-cache";
}
```

---

## 🎯 Scénář 2: Embedded Modal

**Use Case**: Onboarding jako modal overlay v existující aplikaci.

### Implementace

```javascript
// app.js

// Import onboarding styles
import './onboarding.css';

// Check if user needs onboarding
if (!user.onboardingCompleted) {
    showOnboardingModal();
}

function showOnboardingModal() {
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'onboarding-modal';
    modal.innerHTML = `
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <iframe src="/onboarding.html" 
                    frameborder="0"
                    style="width:100%;height:100vh;">
            </iframe>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Listen for completion
    window.addEventListener('message', (event) => {
        if (event.data.type === 'onboarding_completed') {
            closeOnboardingModal();
            refreshUserData();
        }
    });
}
```

### Modify onboarding.js

```javascript
// onboarding.js - add at the end of submitOnboarding()

function submitOnboarding() {
    // ... existing code ...
    
    // Notify parent window (if embedded)
    if (window.parent !== window) {
        window.parent.postMessage({
            type: 'onboarding_completed',
            lead_id: leadId
        }, '*');
    }
    
    // ... rest of code ...
}
```

---

## 🎯 Scénář 3: React Integration

**Use Case**: Integrovat do React aplikace jako komponenta.

### Implementace

```jsx
// OnboardingFlow.jsx

import React, { useEffect, useState } from 'react';
import './onboarding.css';

export function OnboardingFlow({ onComplete }) {
    const [currentStep, setCurrentStep] = useState(0);
    const [formData, setFormData] = useState({
        goal: null,
        area: null,
        level: null,
        description: '',
        timeline: null,
        name: '',
        email: ''
    });
    
    useEffect(() => {
        // Load onboarding.js logic
        // Or reimplement in React
    }, []);
    
    const handleSubmit = async () => {
        try {
            const response = await fetch('/api/leads', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                const data = await response.json();
                onComplete(data.lead_id);
            }
        } catch (error) {
            console.error(error);
        }
    };
    
    return (
        <div className="onboarding-flow">
            {/* Render steps based on currentStep */}
            {/* Use same HTML structure from onboarding.html */}
        </div>
    );
}
```

### Usage

```jsx
// App.jsx

import { OnboardingFlow } from './OnboardingFlow';

function App() {
    const [showOnboarding, setShowOnboarding] = useState(true);
    
    const handleOnboardingComplete = (leadId) => {
        console.log('Lead created:', leadId);
        setShowOnboarding(false);
        // Redirect to dashboard
    };
    
    if (showOnboarding) {
        return <OnboardingFlow onComplete={handleOnboardingComplete} />;
    }
    
    return <Dashboard />;
}
```

---

## 🎯 Scénář 4: Next.js Integration

**Use Case**: Server-side rendered onboarding v Next.js.

### Implementace

```jsx
// pages/onboarding.jsx

import Head from 'next/head';
import { useRouter } from 'next/router';

export default function Onboarding() {
    const router = useRouter();
    
    useEffect(() => {
        // Configure API endpoint
        window.ORAKULUM_API_ENDPOINT = process.env.NEXT_PUBLIC_API_URL;
        window.ORAKULUM_SUCCESS_URL = '/dashboard';
        
        // Load onboarding script
        const script = document.createElement('script');
        script.src = '/onboarding.js';
        document.body.appendChild(script);
        
        return () => {
            document.body.removeChild(script);
        };
    }, []);
    
    return (
        <>
            <Head>
                <title>Začněte s Orakulum</title>
                <link rel="stylesheet" href="/onboarding.css" />
            </Head>
            
            {/* Include onboarding HTML structure */}
            <div dangerouslySetInnerHTML={{ 
                __html: onboardingHTML 
            }} />
        </>
    );
}

export async function getServerSideProps(context) {
    // Check if user already completed onboarding
    const { req } = context;
    const user = await getUserFromSession(req);
    
    if (user && user.onboardingCompleted) {
        return {
            redirect: {
                destination: '/dashboard',
                permanent: false,
            },
        };
    }
    
    return { props: {} };
}
```

---

## 🎯 Scénář 5: API Integration Only

**Use Case**: Použít pouze backend API, vlastní frontend.

### Custom Frontend → Orakulum API

```javascript
// your-app.js

async function submitUserOnboarding(userData) {
    const payload = {
        name: userData.name,
        email: userData.email,
        description: buildDescription(userData),
        input_transform: {
            obor: mapArea(userData.area),
            seniorita: mapLevel(userData.level),
            hlavni_cil: mapGoal(userData.goal),
            casovy_horizont: mapTimeline(userData.timeline),
            technologie: [],
            raw_description: userData.description
        },
        status: 'FLAGGED'
    };
    
    try {
        const response = await fetch('https://api.orakulum.com/api/leads', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${YOUR_API_KEY}`  // if needed
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.lead_id;
        
    } catch (error) {
        console.error('Onboarding submission failed:', error);
        throw error;
    }
}

// Helper functions
function buildDescription(userData) {
    return `${userData.description}\n\nCíl: ${userData.goal}\nOblast: ${userData.area}\nÚroveň: ${userData.level}\nČasový horizont: ${userData.timeline}`;
}

function mapArea(area) {
    const mapping = {
        'frontend': 'Frontend Development',
        'backend': 'Backend Development',
        // ... etc
    };
    return mapping[area] || area;
}
```

---

## 🎯 Scénář 6: WordPress Plugin

**Use Case**: Onboarding jako WordPress plugin/shortcode.

### Plugin Structure

```php
<?php
/*
Plugin Name: Orakulum Onboarding
Description: Career onboarding form
Version: 1.0.0
*/

// Enqueue scripts
function orakulum_enqueue_scripts() {
    wp_enqueue_style('orakulum-onboarding', 
        plugins_url('onboarding.css', __FILE__));
    
    wp_enqueue_script('orakulum-onboarding', 
        plugins_url('onboarding.js', __FILE__), 
        array(), '1.0.0', true);
    
    // Pass config to JavaScript
    wp_localize_script('orakulum-onboarding', 'orakulumConfig', array(
        'apiEndpoint' => get_option('orakulum_api_endpoint'),
        'successUrl' => get_option('orakulum_success_url')
    ));
}
add_action('wp_enqueue_scripts', 'orakulum_enqueue_scripts');

// Shortcode [orakulum-onboarding]
function orakulum_onboarding_shortcode() {
    ob_start();
    include(plugin_dir_path(__FILE__) . 'templates/onboarding.php');
    return ob_get_clean();
}
add_shortcode('orakulum-onboarding', 'orakulum_onboarding_shortcode');
```

### Usage

```
[orakulum-onboarding]
```

---

## 🔌 API Authentication (Optional)

Pokud chcete zabezpečit API endpoint, přidejte autentizaci.

### Backend (api_onboarding.py)

```python
from functools import wraps
from flask import request

API_KEYS = os.getenv('API_KEYS', '').split(',')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key or api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/leads', methods=['POST'])
@require_api_key  # Add authentication
def create_lead():
    # ... existing code ...
```

### Frontend

```javascript
// onboarding.js

async function submitToAPI(payload) {
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': 'your-api-key-here'  // Add API key
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}
```

---

## 🎨 Custom Styling

### Override CSS Variables

```css
/* your-custom.css */

:root {
    /* Override colors */
    --primary: #FF6B6B;
    --primary-hover: #EE5A5A;
    
    /* Override spacing */
    --space-xl: 3rem;
    
    /* Override typography */
    --font-sans: 'Inter', sans-serif;
}

/* Load after onboarding.css */
<link rel="stylesheet" href="onboarding.css">
<link rel="stylesheet" href="your-custom.css">
```

### Add Custom Branding

```html
<!-- onboarding.html - Step 0 -->
<div class="step active" data-step="0">
    <div class="step-content intro-content">
        <!-- Add your logo -->
        <img src="/logo.svg" alt="Logo" class="onboarding-logo">
        
        <div class="step-icon">🎯</div>
        <h1 class="step-title">Vítejte v [Your Brand]</h1>
        <!-- ... rest -->
    </div>
</div>
```

---

## 📊 Analytics Integration

### Google Analytics

```html
<!-- Add to onboarding.html <head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Track Events

```javascript
// onboarding.js - add to existing functions

function nextStep() {
    // ... existing code ...
    
    // Track step completion
    if (typeof gtag !== 'undefined') {
        gtag('event', 'onboarding_step_completed', {
            'step_number': state.currentStep,
            'step_name': getStepName(state.currentStep)
        });
    }
}

function submitOnboarding() {
    // ... existing code ...
    
    // Track conversion
    if (typeof gtag !== 'undefined') {
        gtag('event', 'onboarding_completed', {
            'method': 'form_submission',
            'goal': state.formData.goal,
            'area': state.formData.area
        });
    }
}
```

---

## 🧪 Testing Integration

### Test API Connection

```javascript
// test-integration.js

async function testAPIConnection() {
    try {
        const response = await fetch('http://localhost:5000/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('✅ API connection successful');
            return true;
        }
    } catch (error) {
        console.error('❌ API connection failed:', error);
        return false;
    }
}

testAPIConnection();
```

### Test Full Flow

```javascript
// test-flow.js

async function testOnboardingFlow() {
    const testData = {
        name: 'Test User',
        email: 'test@example.com',
        description: 'Test description with minimum 20 characters',
        input_transform: {
            obor: 'Frontend Development',
            seniorita: 'Začátečník',
            hlavni_cil: 'První práce v IT',
            casovy_horizont: '6 měsíců',
            technologie: [],
            raw_description: 'Test'
        },
        status: 'FLAGGED'
    };
    
    try {
        const response = await fetch('http://localhost:5000/api/leads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        
        const result = await response.json();
        console.log('✅ Test lead created:', result.lead_id);
        
        // Verify in database
        const verifyResponse = await fetch(`http://localhost:5000/api/leads/${result.lead_id}`);
        const lead = await verifyResponse.json();
        
        console.log('✅ Lead verified:', lead.data);
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

testOnboardingFlow();
```

---

## 🚀 Production Checklist

### Before Going Live

- [ ] Update `ORAKULUM_API_ENDPOINT` to production URL
- [ ] Update `ORAKULUM_SUCCESS_URL` to dashboard URL
- [ ] Set `FLASK_ENV=production` in backend
- [ ] Configure CORS with specific domains (not `*`)
- [ ] Enable HTTPS/SSL on all endpoints
- [ ] Add rate limiting to API
- [ ] Set up error monitoring (Sentry)
- [ ] Configure database backups
- [ ] Test on all target browsers
- [ ] Test on mobile devices
- [ ] Set up uptime monitoring
- [ ] Configure CDN for static assets
- [ ] Add API authentication (if needed)
- [ ] Review and test privacy policy links
- [ ] Load test API endpoint

---

## 📚 Reference

### Environment Variables

```env
# Frontend
ORAKULUM_API_ENDPOINT=https://api.yourdomain.com/api/leads
ORAKULUM_SUCCESS_URL=https://app.yourdomain.com/dashboard

# Backend
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
API_PORT=5000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FLASK_ENV=production
```

### API Response Format

**Success (201)**:
```json
{
  "success": true,
  "lead_id": "uuid-here",
  "message": "Lead created successfully",
  "data": { /* lead object */ }
}
```

**Error (400/500)**:
```json
{
  "error": "Error message",
  "details": "Optional detailed error"
}
```

---

## 🆘 Support

- 📖 Full docs: `ONBOARDING_README.md`
- 🚀 Quick start: `ONBOARDING_QUICKSTART.md`
- 🏗️ Architecture: `ONBOARDING_ARCHITECTURE.md`
- 🐛 Issues: Open GitHub issue

---

**Last Updated**: 2025-12-16  
**Version**: 1.0.0
