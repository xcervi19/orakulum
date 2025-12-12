# Orakulum Pipeline (OpenAI API)

## 1. Overview

This is the **main branch** implementation using the **OpenAI API** directly for all LLM operations. No browser automation or pyautogui required.

### Key Features
- **Fully automated** - runs end-to-end without manual intervention
- **API-based** - uses OpenAI Chat Completions API (GPT-4 / GPT-4o)
- **Resumable** - each step persists artifacts, failed runs can resume
- **Observable** - structured JSONL logging + Supabase status tracking
- **Cost-effective** - direct API calls, no browser overhead

## 2. Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Supabase       │────▶│ daily_runner │────▶│ client_learning_    │
│  junior_leads   │     │     .py      │     │ pages               │
│  (FLAGGED)      │     └──────────────┘     └─────────────────────┘
└─────────────────┘            │
                               ▼
                    ┌──────────────────────┐
                    │   OpenAI API         │
                    │   (GPT-4 / GPT-4o)   │
                    └──────────────────────┘
```

## 3. Environment Variables

```bash
# .env file
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o                    # or gpt-4, gpt-3.5-turbo
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
```

## 4. Database Schema

### junior_leads
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| name | text | Client name |
| email | text | Client email |
| description | text | Raw input from client |
| status | text | FLAGGED → PROCESSING → PLAN_READY → HTML_READY → UPLOADED → ARCHIVED |
| input_transform | jsonb | Structured interpretation of description |
| plan | text | Generated master plan with `<blok-n>` tags |
| processing_started_at | timestamptz | When processing began |
| processing_completed_at | timestamptz | When processing finished |
| last_error | text | Error message if blocked |

### client_learning_pages
| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| client_id | uuid | Reference to junior_leads.id |
| page_index | integer | Page order (from filename number) |
| content | jsonb | Transformed JSON content |
| created_at | timestamptz | Creation timestamp |
| updated_at | timestamptz | Last update timestamp |

## 5. Pipeline Steps

### Step 1: Fetch Work Queue
```python
SELECT * FROM junior_leads WHERE status = 'FLAGGED';
```
Mark each as `PROCESSING` with `processing_started_at = now()`.

### Step 2: Input Transform (OpenAI API)
- **Template:** `prompts/input_transform.txt`
- **Input:** `junior_leads.description`
- **Output:** Structured JSON → `junior_leads.input_transform`
- **API Call:** Single completion request with JSON mode

### Step 3: Plan Synthesis (OpenAI API)
- **Template:** `prompts/init_plan.txt`
- **Input:** Values from `input_transform`
- **Output:** Master plan with `<blok-n>` tags → `junior_leads.plan`
- **API Call:** Single completion request (max_tokens: 8000)

### Step 4: Generate Block Prompts
- **Script:** `manual.py --input plan.txt --output parsed_parts/`
- **Output:** `prompt_block_1.txt` through `prompt_block_N.txt`
- **No API call** - local text processing

### Step 5: Expand Blocks - Stage 2 (OpenAI API)
- **Input:** `parsed_parts/prompt_block_*.txt`
- **Output:** `stage_2_generated_parts/part*.txt`
- **API Calls:** One per block (processed sequentially with retry)

### Step 6: Prepare HTML Prompts
- **Script:** `prepare_html_prompts.py`
- **Template:** `prompts/html_transform.txt`
- **Output:** `stage_2_prepared_html/part*.txt`
- **No API call** - local text processing

### Step 7: HTML Generation - Stage 3 (OpenAI API)
- **Input:** `stage_2_prepared_html/part*.txt`
- **Output:** `stage_3_generated_html/parthtml*.txt`
- **API Calls:** One per file

### Step 8: HTML → JSON
- **Script:** `html_to_json.py`
- **Output:** `transformed/parthtml*.json`
- **No API call** - local parsing

### Step 9: Clean & Upload
- **Script:** `clean_markdown.py` → `upload_learning_content.py`
- **Output:** Records in `client_learning_pages`
- Mark status as `UPLOADED`

## 6. Usage

### Process all flagged leads:
```bash
python3 daily_runner.py
```

### Process specific client:
```bash
python3 daily_runner.py --client CLIENT_ID
```

### Dry run (preview only):
```bash
python3 daily_runner.py --dry-run
```

### Resume failed client:
```bash
python3 daily_runner.py --resume CLIENT_ID
```

## 7. Run Directory Structure

Each client processing creates:
```
runs/<client_id>/<YYYYMMDD_HHMM>/
├── logs/
│   └── pipeline.jsonl          # Structured event log
├── input_transform/
│   ├── prompt.txt              # Sent to API
│   └── output.json             # API response
├── plan/
│   ├── prompt.txt
│   └── plan.txt
├── parsed_parts/
│   └── prompt_block_*.txt
├── stage_2_generated_parts/
│   └── part*.txt
├── stage_2_prepared_html/
│   └── part*.txt
├── stage_3_generated_html/
│   └── parthtml*.txt
├── transformed/
│   └── parthtml*.json
└── run_summary.json            # Final status + metrics
```

## 8. Error Handling & Recovery

### Automatic Retries
- Each API call retries up to 3 times with exponential backoff
- Rate limit errors (429) handled automatically with longer delays

### Manual Recovery
```bash
# View blocked clients
python3 -c "from pipeline.db import get_leads_by_status; print(get_leads_by_status('BLOCKED'))"

# Unblock and retry
python3 daily_runner.py --resume CLIENT_ID
```

### Status Lifecycle
```
FLAGGED ──▶ PROCESSING ──▶ PLAN_READY ──▶ HTML_READY ──▶ UPLOADED ──▶ ARCHIVED
                │
                ▼
            BLOCKED (on failure, check last_error)
```

## 9. Cost Estimation

Approximate tokens per client (GPT-4o pricing):
| Step | Input Tokens | Output Tokens | Cost |
|------|--------------|---------------|------|
| Input Transform | ~500 | ~300 | $0.01 |
| Plan Synthesis | ~2,000 | ~3,000 | $0.05 |
| Stage 2 (15 blocks) | ~15,000 | ~20,000 | $0.35 |
| Stage 3 (15 blocks) | ~20,000 | ~25,000 | $0.45 |
| **Total per client** | | | **~$0.86** |

*Prices based on GPT-4o at $5/1M input, $15/1M output tokens*

## 10. Scheduling

### Cron (daily at 6 AM):
```bash
0 6 * * * cd /path/to/orakulum && python3 daily_runner.py >> logs/cron.log 2>&1
```

### Systemd service:
```ini
[Unit]
Description=Orakulum Daily Pipeline
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/orakulum
ExecStart=/usr/bin/python3 daily_runner.py
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

## 11. Project Structure

```
orakulum/
├── pipeline/                    # Core pipeline module
│   ├── __init__.py
│   ├── db.py                   # Supabase operations
│   ├── openai_client.py        # OpenAI API wrapper
│   ├── steps.py                # Pipeline step implementations
│   └── logging_utils.py        # Structured logging
├── prompts/                    # Prompt templates
│   ├── input_transform.txt
│   ├── init_plan.txt
│   ├── expand.txt
│   └── html_transform.txt
├── daily_runner.py             # Main orchestrator
├── manual.py                   # Block parser
├── prepare_html_prompts.py     # HTML prompt generator
├── html_to_json.py            # HTML to JSON converter
├── clean_markdown.py          # Markdown artifact cleaner
├── upload_learning_content.py # Supabase uploader
└── requirements.txt
```

## 12. Development Notes

- **Main branch** uses OpenAI API (this implementation)
- Prompts are in `prompts/` directory - edit to customize output
- All API calls logged to `runs/<client>/logs/pipeline.jsonl`
- Test with `--dry-run` before processing real clients
- Set `OPENAI_MODEL=gpt-3.5-turbo` for cheaper testing
