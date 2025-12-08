# Orakulum - Project Plan

## Project Overview

**Goal:** Fully automated system that generates personalized IT career guidance plans for clients in Czech Republic, processes content through multi-stage pipeline, and uploads to Supabase database.

**Current State:** Research/experimental phase. Content processing pipeline works, but automation needs completion.

---

## Short-Term Goals

### Working Pipeline (The Good Code)

1. **`manual.py`** → Generates prompts in `parsed_parts/` (prompt_block_*.txt)
2. **Manual Step:** Run prompts through ChatGPT → Outputs to `stage_2_generated_parts/` (part*.txt)
3. **`prepare_html_prompts.py`** → Prepares HTML prompts in `stage_2_prepared_html/`
4. **Manual Step:** Run HTML prompts → Outputs to `stage_3_generated_html/` (parthtml*.txt)
5. **`html_to_json.py`** → Converts HTML to JSON in `transformed/` (parthtml*.json)
6. **`clean_markdown.py`** → Cleans markdown artifacts from JSON
7. **`upload_learning_content.py`** → Uploads to Supabase database

**Current Gap:** Steps 2 and 4 are manual (copy-paste prompts, wait for responses, copy outputs).

---

## Long-Term Vision

**Final Product:**
- Fully automated, ad-hoc, non-standard program
- Runs on your computer (not a web service)
- Takes client input → generates complete career plan → processes → uploads to database
- Zero manual intervention
- Uses `pyautogui` for UI automation (clicking, typing, copying) since it's custom workflow

**Why pyautogui?**
- Lazy automation: don't want to manually write/run prompts
- Custom workflow that requires screen interaction
- Non-standard automation needs

---

## Implementation Plan

### Phase 1: Cleanup (Immediate)

**Remove all Playwright code:**
- ❌ `mainb.py` - Playwright automation attempt
- ❌ `mainc.py` - Async Playwright attempt  
- ❌ `maind.py` - Chrome profile automation
- ❌ `logic.py` - Playwright step definitions
- ❌ `login.py` - Playwright login helper
- ❌ `config.py` - Playwright settings (if only used by Playwright)

**Keep:**
- ✅ `main.py` - pyautogui automation (needs fixing)
- ✅ All stage_* pipeline scripts
- ✅ All processing scripts (manual.py, prepare_html_prompts.py, html_to_json.py, etc.)

### Phase 2: Fix pyautogui Automation

**Current `main.py` issues:**
- Missing `send_text()` function (referenced but not defined)
- Incomplete automation flow
- No error handling
- No retry logic
- No progress tracking

**What needs to be added:**

1. **Complete automation flow:**
   - Find textarea → paste prompt → click send
   - Wait for response → detect completion
   - Copy response → save to file
   - Handle "Continue generating" buttons
   - Handle rate limit messages

2. **Error handling:**
   - Retry failed image matches with different thresholds
   - Handle UI changes gracefully
   - Detect and handle captchas/verification
   - Session timeout detection

3. **Integration with pipeline:**
   - Read prompts from `parsed_parts/` or `stage_2_prepared_html/`
   - Save outputs to `stage_2_generated_parts/` or `stage_3_generated_html/`
   - Track which prompts completed
   - Resume from checkpoint

4. **Rate limit management:**
   - Track messages per hour/day
   - Add delays between requests
   - Pause when limits hit
   - Log usage statistics

### Phase 3: End-to-End Automation

**Create master script that:**
1. Takes client input (JSON or form)
2. Runs `manual.py` to generate prompts
3. Automates ChatGPT interaction for all prompts
4. Runs `prepare_html_prompts.py`
5. Automates ChatGPT interaction for HTML prompts
6. Runs `html_to_json.py`
7. Runs `clean_markdown.py`
8. Runs `upload_learning_content.py`
9. Reports completion status

---

## ChatGPT Usage Strategy

### Testing Phase (100 tests)

**Use ChatGPT Plus ($20/month):**
- 150 messages per 3 hours
- ~1,200 messages/day
- ~20,000-25,000 messages/month practical max
- **100 plans = 3,000-5,000 prompts** ✅ Feasible

**Requirements:**
- Add error handling for rate limits
- Implement retry logic
- Track usage to avoid hitting limits
- Add delays between requests

### Scaling Phase

**Stay on ChatGPT Plus if:**
- <500 plans/month (15,000-25,000 prompts)
- Cost-effective at $20/month
- Web UI automation works reliably

**Switch to OpenAI API when:**
- >500 plans/month consistently
- Need better reliability (web UI can break)
- Need faster responses
- API becomes cost-effective (~$250-750/month for 500 plans)

**API Cost Estimate:**
- GPT-4o: ~$0.0025 per 1K input tokens, ~$0.01 per 1K output tokens
- 100 plans: ~$50-150 (vs $20/month Plus)
- 500 plans: ~$250-750 (API becomes competitive)
- 1,000+ plans: API is cheaper

**Theoretical Maximum with Plus:** ~20,000-25,000 prompts/month = 400-800 career plans

---

## File Structure

```
orakulum/
├── buttons/              # Button images for pyautogui
├── manual_input/         # Client input data
├── parsed_parts/         # Generated prompts (from manual.py)
├── stage_2_generated_parts/  # ChatGPT outputs (step 2)
├── stage_2_prepared_html/    # HTML prompts (from prepare_html_prompts.py)
├── stage_3_generated_html/   # ChatGPT HTML outputs (step 4)
├── transformed/         # Final JSON files (from html_to_json.py)
├── main.py              # pyautogui automation (TO FIX)
├── manual.py            # Generate prompts ✅
├── prepare_html_prompts.py  # Prepare HTML prompts ✅
├── html_to_json.py      # Convert HTML to JSON ✅
├── clean_markdown.py    # Clean JSON ✅
├── upload_learning_content.py  # Upload to Supabase ✅
├── prompts.toml         # Prompt templates
└── PLAN.md              # This file
```

---

## Next Steps

1. **Cleanup:** Remove Playwright files (mainb.py, mainc.py, maind.py, logic.py, login.py)
2. **Fix main.py:** Complete pyautogui automation with error handling
3. **Test:** Run 10-20 tests to validate automation
4. **Integrate:** Connect automation to pipeline stages
5. **Scale:** Test with 100 plans using ChatGPT Plus
6. **Monitor:** Track usage, errors, and costs
7. **Optimize:** Improve reliability and speed
8. **Scale Further:** Switch to API when needed (>500 plans/month)

---

## Notes

- This is a research/experimental project
- Automation is ad-hoc and non-standard (by design)
- Focus on getting it working, then optimize
- Keep it simple - pyautogui is fine for this use case
- Delay API switch as long as possible (cost optimization)

