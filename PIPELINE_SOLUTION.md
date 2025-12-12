# Orakulum Pipeline

Automated end-to-end career-plan generation system using OpenAI API.

## Overview

This pipeline automatically processes client leads from Supabase, generates personalized career plans, and uploads structured learning content.

### Key Features
- **Fully automated** - runs end-to-end without manual intervention
- **API-based** - uses OpenAI Chat Completions API (GPT-4 / GPT-4o)
- **Resumable** - each step persists artifacts, failed runs can resume
- **Observable** - structured JSONL logging + Supabase status tracking

## Project Structure

```
orakulum/
├── run_pipeline.py              # Main entry point
├── pipeline/                    # Core pipeline module
│   ├── __init__.py
│   ├── db.py                   # Supabase database operations
│   ├── llm.py                  # OpenAI API client
│   ├── steps.py                # Pipeline step implementations
│   └── logger.py               # Structured logging
├── processors/                  # Data processors
│   ├── __init__.py
│   ├── block_parser.py         # Parse plan into blocks
│   ├── html_wrapper.py         # Wrap content with HTML template
│   ├── html_to_json.py         # Convert HTML to JSON
│   ├── json_cleaner.py         # Clean markdown artifacts
│   └── uploader.py             # Upload to Supabase
├── prompts/                     # Prompt templates
│   ├── input_transform.txt     # Client input → structured JSON
│   ├── init_plan.txt           # Generate 15-block plan
│   ├── expand.txt              # Expand individual blocks
│   └── html_transform.txt      # Convert to HTML
├── runs/                        # Per-client run artifacts
└── requirements.txt
```

## Environment Variables

```bash
# .env file
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=your-service-key

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
```

## Database Schema

### junior_leads
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| name | text | Client name |
| email | text | Client email |
| description | text | Raw input from client |
| status | text | FLAGGED → PROCESSING → PLAN_READY → HTML_READY → UPLOADED |
| input_transform | jsonb | Structured interpretation |
| plan | text | Generated plan with `<blok-n>` tags |
| processing_started_at | timestamptz | When processing began |
| processing_completed_at | timestamptz | When finished |
| last_error | text | Error message if blocked |

### client_learning_pages
| Column | Type | Description |
|--------|------|-------------|
| id | integer | Primary key |
| client_id | uuid | Reference to junior_leads.id |
| page_index | integer | Page order |
| content | jsonb | Transformed JSON content |
| created_at | timestamptz | Creation timestamp |
| updated_at | timestamptz | Last update |

## Pipeline Steps

1. **Input Transform** - Parse client description into structured JSON
2. **Plan Generation** - Create 15-block career plan
3. **Block Parsing** - Split plan into individual block prompts
4. **Stage 2: Expand** - Expand each block with detailed content
5. **HTML Wrapping** - Wrap with HTML transform template
6. **Stage 3: HTML** - Generate semantic HTML with data-ui attributes
7. **HTML to JSON** - Convert HTML to structured JSON
8. **Clean** - Remove markdown artifacts
9. **Upload** - Upload to Supabase

## Usage

### Process all flagged leads
```bash
python3 run_pipeline.py
```

### Process specific client
```bash
python3 run_pipeline.py --client CLIENT_UUID
```

### Preview without processing
```bash
python3 run_pipeline.py --dry-run
```

### Resume failed processing
```bash
python3 run_pipeline.py --resume CLIENT_UUID
```

## Run Directory Structure

Each client run creates:
```
runs/<client_id>/<YYYYMMDD_HHMM>/
├── logs/
│   └── pipeline.jsonl
├── input_transform/
│   ├── prompt.txt
│   └── output.json
├── plan/
│   ├── prompt.txt
│   └── plan.txt
├── parsed_parts/
│   └── prompt_block_*.txt
├── stage_2_generated_parts/
│   └── prompt_block_*.txt
├── stage_2_prepared_html/
│   └── prompt_block_*.txt
├── stage_3_generated_html/
│   └── prompt_block_*.txt
├── transformed/
│   └── page_*.json
└── run_summary.json
```

## Status Lifecycle

```
FLAGGED → PROCESSING → PLAN_READY → HTML_READY → UPLOADED → ARCHIVED
              ↓
          BLOCKED (on failure)
```

## Error Recovery

```bash
# View blocked clients
python3 -c "from pipeline.db import get_leads_by_status; print(get_leads_by_status('BLOCKED'))"

# Unblock and retry
python3 run_pipeline.py --resume CLIENT_UUID
```

## Cost Estimation (GPT-4o)

| Step | Input Tokens | Output Tokens | Cost |
|------|--------------|---------------|------|
| Input Transform | ~500 | ~300 | $0.01 |
| Plan | ~2,000 | ~3,000 | $0.05 |
| Stage 2 (15 blocks) | ~15,000 | ~20,000 | $0.35 |
| Stage 3 (15 blocks) | ~20,000 | ~25,000 | $0.45 |
| **Total per client** | | | **~$0.86** |

## Scheduling

### Cron (daily at 6 AM)
```bash
0 6 * * * cd /path/to/orakulum && python3 run_pipeline.py >> logs/cron.log 2>&1
```

### Systemd service
```ini
[Unit]
Description=Orakulum Pipeline
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/path/to/orakulum
ExecStart=/usr/bin/python3 run_pipeline.py
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
