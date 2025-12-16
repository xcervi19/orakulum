# Orakulum Onboarding - Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ONBOARDING FRONTEND                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │onboarding.html│  │onboarding.css│  │onboarding.js│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  Features:                                                       │
│  • 7-step wizard (Intro → Email)                               │
│  • Live Activity Panel (6-8s rotation)                         │
│  • Progress bar                                                 │
│  • Validation (client-side)                                    │
│  • Loading screen (8s animation)                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST /api/leads
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API SERVER (Flask)                         │
│                    api_onboarding.py                            │
│                                                                  │
│  Endpoints:                                                      │
│  • POST   /api/leads       - Create new lead                   │
│  • GET    /api/leads/:id   - Get lead by ID                    │
│  • GET    /api/health      - Health check                      │
│                                                                  │
│  Features:                                                       │
│  • Validation (server-side)                                    │
│  • Error handling                                               │
│  • CORS support                                                 │
│  • UUID generation                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Supabase Client (Python)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE DATABASE                            │
│                                                                  │
│  Table: junior_leads                                            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ id              │ text (UUID)                           │   │
│  │ name            │ text                                   │   │
│  │ email           │ text                                   │   │
│  │ description     │ text (full description)              │   │
│  │ status          │ text (FLAGGED → PROCESSING → ...)   │   │
│  │ input_transform │ jsonb (structured data)              │   │
│  │ plan            │ text (null initially)                │   │
│  │ created_at      │ text (ISO timestamp)                 │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Status: FLAGGED
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE PROCESSOR                           │
│                     run_pipeline.py                             │
│                                                                  │
│  Steps:                                                          │
│  1. Input transform       (AI analysis)                        │
│  2. Plan synthesis        (Generate 15-block plan)             │
│  3. Block expansion       (Detailed content)                   │
│  4. HTML generation       (Formatted output)                   │
│  5. JSON transformation   (Structured data)                    │
│  6. Upload to DB          (client_learning_pages)              │
│                                                                  │
│  Status flow: FLAGGED → PROCESSING → UPLOADED                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. User Onboarding Flow

```
User → Step 0 (Intro)
     → Step 1 (Cíl: first_job)
     → Step 2 (Oblast: frontend)
     → Step 3 (Úroveň: beginner)
     → Step 4 (Popis: "Učím se JS...")
     → Step 5 (Timeline: 6_months)
     → Step 6 (Email: jan@example.com)
     → Submit
```

### 2. Frontend Processing

```javascript
// Collect form data
formData = {
  goal: 'first_job',
  area: 'frontend',
  level: 'beginner',
  description: 'Učím se JS...',
  timeline: '6_months',
  name: 'Jan Novák',
  email: 'jan@example.com'
}

// Build API payload
payload = buildPayload(formData)

// Show loading screen (8s)
showLoadingScreen()

// Send to API
fetch('/api/leads', {
  method: 'POST',
  body: JSON.stringify(payload)
})

// Redirect to success
redirectToSuccess()
```

### 3. Backend Processing

```python
# api_onboarding.py

@app.route('/api/leads', methods=['POST'])
def create_lead():
    # 1. Parse request
    data = request.get_json()
    
    # 2. Validate
    validate_required_fields(data)
    validate_email(data['email'])
    
    # 3. Generate UUID
    lead_id = str(uuid.uuid4())
    
    # 4. Prepare data
    lead_data = {
        "id": lead_id,
        "name": data['name'],
        "email": data['email'],
        "description": data['description'],
        "status": "FLAGGED",
        "input_transform": data['input_transform']
    }
    
    # 5. Insert to Supabase
    supabase.table("junior_leads").insert(lead_data)
    
    # 6. Return success
    return {"success": True, "lead_id": lead_id}
```

### 4. Database Structure

```json
{
  "id": "a1b2c3d4-...",
  "name": "Jan Novák",
  "email": "jan@example.com",
  "description": "Učím se JS...\n\nCíl: První práce v IT\nOblast: Frontend Development\n...",
  "status": "FLAGGED",
  "input_transform": {
    "obor": "Frontend Development",
    "seniorita": "Začátečník",
    "hlavni_cil": "První práce v IT",
    "casovy_horizont": "6 měsíců",
    "technologie": [],
    "raw_description": "Učím se JS..."
  },
  "plan": null,
  "created_at": "2025-12-16T12:00:00Z"
}
```

### 5. Pipeline Processing (Existing)

```
Status: FLAGGED
         ↓
run_pipeline.py detects FLAGGED lead
         ↓
Status: PROCESSING
         ↓
Step 1: Input Transform (analyze → structured JSON)
Step 2: Plan Synthesis (generate 15-block plan)
Step 3: Block Expansion (detailed content per block)
Step 4: HTML Generation (formatted with data-ui attributes)
Step 5: JSON Transform (parse HTML → JSON)
Step 6: Upload (client_learning_pages table)
         ↓
Status: UPLOADED
         ↓
User receives email with access
```

---

## 🎨 Frontend Architecture

### Component Structure

```
onboarding.html
├── <div id="app">
│   ├── <aside> Live Activity Panel
│   │   ├── Activity Header (pulse indicator)
│   │   ├── Activity List (rotates every 6-8s)
│   │   └── Activity Footer (stats)
│   │
│   ├── <main> Onboarding Main
│   │   ├── Progress Bar Container
│   │   │   ├── Progress Bar (animated fill)
│   │   │   └── Progress Label (step X/7)
│   │   │
│   │   ├── Step Container
│   │   │   ├── Step 0: Intro (active)
│   │   │   ├── Step 1: Cíl
│   │   │   ├── Step 2: Oblast
│   │   │   ├── Step 3: Úroveň
│   │   │   ├── Step 4: Konkrétnost
│   │   │   ├── Step 5: Timeline
│   │   │   └── Step 6: Email
│   │   │
│   │   └── Navigation Buttons
│   │       └── Back Button (conditionally visible)
│   │
│   └── <div> Loading Screen (hidden by default)
│       ├── Loading Spinner (CSS animation)
│       ├── Loading Title
│       └── Loading Step (rotates every 1.5s)
```

### State Management

```javascript
const state = {
    currentStep: 0,          // Current step index (0-6)
    totalSteps: 7,           // Total number of steps
    formData: {              // Collected form data
        goal: null,
        area: null,
        level: null,
        description: '',
        timeline: null,
        name: '',
        email: ''
    }
};
```

### Key Functions

```javascript
// Navigation
- nextStep()              // Advance to next step
- prevStep()              // Go back to previous step
- transitionStep(n)       // Transition to specific step

// Form handling
- selectOption(field, value)    // Handle option selection
- validateAndNextStep(step)     // Validate before advancing
- submitOnboarding()            // Final form submission

// Live Activity
- startLiveActivity()     // Initialize activity panel
- rotateActivity()        // Rotate activities every 6-8s
- addActivityItem(index)  // Add new activity to panel

// Loading
- showLoadingScreen()     // Display loading overlay
- updateLoadingStep()     // Rotate loading messages
- hideLoadingScreen()     // Hide loading overlay

// API
- buildPayload()          // Build API payload from formData
- submitToAPI(payload)    // Send data to backend
- redirectToSuccess()     // Redirect after successful submit
```

---

## 🔐 Security & Validation

### Client-side Validation

```javascript
// onboarding.js

// Email validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Required fields
- goal: required (auto-selected)
- area: required (auto-selected)
- level: required (auto-selected)
- description: required, min 20 chars
- timeline: required (auto-selected)
- name: required, min 2 chars
- email: required, valid format
```

### Server-side Validation

```python
# api_onboarding.py

# Required fields check
required_fields = ['name', 'email', 'description']
missing = [f for f in required_fields if not data.get(f)]
if missing:
    return error(400, f"Missing: {missing}")

# Email format check
if '@' not in email or '.' not in email:
    return error(400, "Invalid email")

# SQL injection protection
# ✅ Handled by Supabase Python client (parameterized queries)

# XSS protection
# ✅ Data stored as-is, sanitized on output in frontend
```

---

## 📊 Performance Considerations

### Frontend Optimization

| Item | Implementation | Impact |
|------|----------------|--------|
| CSS animations | GPU-accelerated transforms | Smooth 60fps |
| Image optimization | No images (emoji only) | Fast load |
| JavaScript | Vanilla JS, no frameworks | <10KB bundle |
| Lazy loading | N/A (single page) | Instant load |
| Minification | Not yet (dev mode) | Production ready |

### Backend Optimization

| Item | Implementation | Impact |
|------|----------------|--------|
| Database indexing | UUID primary key | Fast lookups |
| Connection pooling | Supabase client | Efficient queries |
| CORS caching | flask-cors | Reduced preflight |
| Error logging | Try/catch blocks | Quick debugging |
| Rate limiting | Not yet | Add in production |

### Network Optimization

| Item | Current | Recommended |
|------|---------|-------------|
| HTTP/2 | ✅ (Supabase) | Use HTTP/2 for API |
| Compression | - | Enable gzip/brotli |
| CDN | - | Cloudflare/Fastly |
| Caching | - | Browser cache headers |

---

## 🧪 Testing Strategy

### Manual Testing Checklist

```
✅ Step 0: Intro loads correctly
✅ Step 1-5: All options selectable
✅ Step 4: Character counter works
✅ Step 6: Email validation works
✅ Submit: Loading screen appears
✅ Live Activity: Rotates every 6-8s
✅ Progress bar: Updates correctly
✅ Back button: Shows/hides appropriately
✅ Mobile: Responsive layout works
✅ Accessibility: Keyboard navigation works
```

### Automated Testing

```bash
# API tests
python3 test_onboarding_api.py

Tests:
✅ Health check endpoint
✅ Create lead (valid data)
✅ Get lead by ID
✅ Validation (missing fields)
✅ Validation (invalid email)
```

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Tested |
| Firefox | 88+ | ✅ Tested |
| Safari | 14+ | ✅ Tested |
| Edge | 90+ | ✅ Compatible |
| Mobile Safari | iOS 14+ | ✅ Tested |
| Chrome Mobile | Android 10+ | ✅ Tested |

---

## 🚀 Deployment Architecture

### Development

```
Local Machine
├── Frontend: http://localhost:8000
└── Backend:  http://localhost:5000
     └── Supabase: Remote (production DB)
```

### Production

```
┌─────────────────────────────────────┐
│    CDN (Cloudflare/Fastly)         │
│    Static assets, caching           │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Frontend Hosting                 │
│    (Vercel/Netlify)                 │
│    • onboarding.html                │
│    • onboarding.css                 │
│    • onboarding.js                  │
│    • success.html                   │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    API Server                       │
│    (Heroku/Railway/Fly.io)          │
│    • api_onboarding.py              │
│    • gunicorn (4 workers)           │
│    • SSL/HTTPS                      │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│    Supabase                         │
│    • PostgreSQL database            │
│    • Row-level security             │
│    • Auto-backups                   │
└─────────────────────────────────────┘
```

---

## 📈 Monitoring & Analytics

### Recommended Tracking Events

```javascript
// Google Analytics / Mixpanel events

onboarding_started
step_viewed (step_number, step_name)
step_completed (step_number, time_spent)
step_abandoned (step_number)
validation_error (field, error_type)
api_error (status_code, error_message)
onboarding_completed (total_time)
success_page_viewed
```

### Health Monitoring

```python
# Recommended tools

- Sentry (error tracking)
- DataDog (APM)
- Pingdom (uptime monitoring)
- LogRocket (session replay)
```

---

## 🔄 Future Enhancements

### Phase 2 (Q1 2026)

- [ ] Real-time activity stream (WebSocket)
- [ ] Progressive form save (localStorage)
- [ ] Email verification flow
- [ ] Social proof: "X people completed this step"

### Phase 3 (Q2 2026)

- [ ] A/B testing framework
- [ ] Multi-language support (EN, DE)
- [ ] Personalized activity messages
- [ ] Video testimonials in intro

### Phase 4 (Q3 2026)

- [ ] AI-powered suggestions
- [ ] Interview prep integration
- [ ] Resume upload & analysis
- [ ] Portfolio review

---

**Last Updated**: 2025-12-16  
**Version**: 1.0.0  
**Status**: Production Ready
