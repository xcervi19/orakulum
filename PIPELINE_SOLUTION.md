# Daily GPT Planning Pipeline (Local Automation)

## 1. Goals & Operating Principles
- Fully automate the career-plan pipeline described in `PLAN.md`, but keep it runnable on a single local machine that drives ChatGPT through `pyautogui`.
- Start every run by selecting `junior_leads` rows whose `status = 'flagged'`, then process each client end-to-end.
- Persist the output of every prompt and transformation (database columns *and* local files) so that any failure can resume without repeating the entire flow.
- Maintain a strict "safety rule": never overwrite user data without first snapshotting, and only advance a client’s status after a step succeeds.
- Provide clear observability (structured logging + Supabase status fields) so you always know where a client is in the pipeline.

## 2. Data & Storage Contracts
| Location | Purpose | Notes |
| --- | --- | --- |
| Supabase `junior_leads` | Source queue + checkpoints | Required columns: `id`, `status`, `description`, `input_transform` (jsonb), `plan` (text), plus two new timestamps (`processing_started_at`, `processing_completed_at`).
| Supabase `client_learning_pages` | Final multi-page learning content | Populated by `upload_learning_content.py`. Page index is derived from filenames (e.g., `parthtml5.json → page_index 5`).
| Local `runs/<client_id>/<run_date>/` | Durable artifacts per step | Store prompt inputs, raw ChatGPT replies, html/json outputs, and logs for forensic replay.
| Existing stage folders | Reuse the current pipeline layout: `parsed_parts/`, `stage_2_generated_parts/`, `stage_2_prepared_html/`, `stage_3_generated_html/`, `transformed/`.

**Suggested status lifecycle in `junior_leads.status`:** `flagged → processing → plan_ready → html_ready → uploaded → archived`. Store failure reason in a new nullable column `last_error` to help with recovery.

## 3. Step-by-Step Flow
1. **Fetch work queue**
   - `SELECT id, description FROM junior_leads WHERE status = 'flagged';`
   - Immediately set each picked row to `processing` with `processing_started_at = now()` so the same client is not double-processed.
2. **Input transform prompt**
   - Template: `prompts/input_transform.txt` (fills `[VSTUP]` with `junior_leads.description`).
   - Save the prepared prompt to `runs/<client>/input_transform/prompt.txt`, execute it via the existing ChatGPT automation (`automate_chatgpt.py` can read that directory analogously to stage 2), then store the response both as `runs/<client>/input_transform/output.json` and in Supabase (`input_transform = <json>`).
   - If the prompt fails, leave status `processing` and capture the error + retry count; do *not* clear the queued prompt so it can resume.
3. **Plan synthesis prompt**
   - Base template: `prompts/init_plan.txt` (it produces the 15-block master plan using `<blok-n>` tags).
   - Input uses the structured output from step 2 (inject into placeholders inside the init-plan prompt; e.g., pass the interpreted field values).
   - Store the raw plan text in `junior_leads.plan` and in `runs/<client>/plan/plan.txt`.
4. **Generate per-block prompts (`manual.py`)**
   - Replace `manual_input/tutorial.txt` content with the plan text for the current client (or change `manual.py` to accept `--input` so it can read the per-client file in `runs/<client>/plan/plan.txt`).
   - Run `python manual.py --input runs/<client>/plan/plan.txt --json runs/<client>/plan/profile.json --output parsed_parts/<client_id>/` (light CLI tweak). Each `prompt_block_<n>.txt` stays alongside existing blocks for traceability.
5. **Send prompts to ChatGPT (Stage 2)**
   - Point `automate_chatgpt.py` at `parsed_parts/<client_id>/` via an argument such as `python automate_chatgpt.py --input parsed_parts/<client_id> --output stage_2_generated_parts/<client_id>` (both directories live under the client’s run folder).
   - After each response is saved, append metadata (`prompt_name`, timestamp, success flag) to `runs/<client>/logs/stage2.jsonl`.
   - Once all blocks succeed, update Supabase `status = 'plan_ready'`.
6. **Prepare HTML prompts**
   - Use `prepare_html_prompts.py` with `INPUT_DIR=stage_2_generated_parts/<client_id>` and `OUTPUT_DIR=stage_2_prepared_html/<client_id>` to wrap each response in the HTML transform template (`prompts/html_transform.txt`).
7. **ChatGPT HTML generation (Stage 3)**
   - Run `automate_chatgpt.py` again, this time pointing to `stage_2_prepared_html/<client_id>` → `stage_3_generated_html/<client_id>`.
   - On completion, set `status = 'html_ready'` in Supabase.
8. **HTML → JSON**
   - Execute `python html_to_json.py --input stage_3_generated_html/<client_id> --output transformed/<client_id>` so each `parthtmlN.txt` becomes `parthtmlN.json`.
9. **Clean + upload**
   - `python clean_markdown.py --directory transformed/<client_id>`.
   - `python upload_learning_content.py <client_id> --directory transformed/<client_id>` pushes final pages into `client_learning_pages`.
   - Mark the row as `status = 'uploaded'`, set `processing_completed_at = now()`, and attach the list of uploaded page indices to the run log.
10. **Archival & notification**
    - Zip the `runs/<client_id>/<timestamp>/` folder, move it to cold storage (optional), and notify the operator (email/Slack) with the summary.

## 4. Orchestrator Structure (`daily_runner.py`)
Pseudo-code sketch:
```python
from pathlib import Path
from supabase import create_client

from pipeline.steps import (
    fetch_flagged_leads, mark_status, run_input_transform,
    run_plan_prompt, generate_blocks, run_stage2, prep_html,
    run_stage3, html_to_json, clean_json, upload_pages
)

def process_client(client):
    run_dir = Path("runs") / client.id / datetime.now().strftime("%Y%m%d_%H%M")
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        mark_status(client.id, "processing")
        run_input_transform(client, run_dir)
        run_plan_prompt(client, run_dir)
        generate_blocks(client, run_dir)
        run_stage2(client, run_dir)
        prep_html(client, run_dir)
        run_stage3(client, run_dir)
        html_to_json(client, run_dir)
        clean_json(client, run_dir)
        upload_pages(client, run_dir)
        mark_status(client.id, "uploaded")
    except Exception as exc:
        mark_failure(client.id, exc)
        raise

def main():
    for client in fetch_flagged_leads():
        process_client(client)

if __name__ == "__main__":
    main()
```
Schedule `daily_runner.py` via `cron` (`0 6 * * * /usr/bin/python /workspace/daily_runner.py >> logs/pipeline.log 2>&1`) or a `systemd` user service so it executes every morning.

## 5. Safety, Logging & Recovery
- **Atomic status updates:** a client only advances when the current step wrote both disk artifacts and Supabase columns successfully.
- **Idempotent directories:** every step writes to a `{client_id}/{run}` namespace so reruns don’t clobber previous outputs. If a rerun starts, it checks for completed files and skips them (mirroring `automate_chatgpt.py`’s existing “skip if output exists” behavior).
- **Structured logs:** store JSONL logs per stage (prompt path, response path, duration, retries, error message). Aggregate summary appended to `runs/<client>/run_summary.json`.
- **Retries + manual intervention:** allow up to 3 automated retries for ChatGPT calls; if they all fail, set `status = 'blocked'` and include `last_error`. Operators can unblock by editing the status back to `flagged`.
- **Credential safety:** load Supabase service keys from `.env` (already supported by `upload_learning_content.py`). Never print secrets to logs; scrub PII from console output before sharing.
- **Daily snapshots:** each run archives its input files alongside the prompts, so you can recreate ChatGPT outputs later if OpenAI changes its behavior.

## 6. Immediate Next Actions
1. Add CLI arguments to `manual.py`, `prepare_html_prompts.py`, `automate_chatgpt.py`, `html_to_json.py`, and `clean_markdown.py` so each step can target a client-specific directory without manual file shuffling.
2. Implement the `daily_runner.py` orchestrator (or equivalent) plus helper modules for Supabase I/O and logging.
3. Extend the Supabase schema with the additional status/timestamp/error columns for `junior_leads`.
4. Test the end-to-end flow with a single flagged client, validate that each checkpoint persists, then enable the cron job for daily automation.
