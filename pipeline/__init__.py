"""
Orakulum Pipeline Module

Automated career-plan generation pipeline that processes junior_leads
through OpenAI API and uploads learning content to Supabase.

Main branch uses OpenAI Chat Completions API for all LLM operations.
No browser automation required - fully API-driven.
"""

from .db import (
    get_client,
    fetch_flagged_leads,
    mark_status,
    mark_failure,
    update_lead_field,
)
from .steps import (
    run_input_transform,
    run_plan_prompt,
    generate_blocks,
    run_stage2,
    prep_html,
    run_stage3,
    html_to_json_step,
    clean_json,
    upload_pages,
)
from .openai_client import (
    call_llm,
    call_llm_with_file,
    process_prompt_batch,
)
from .logging_utils import PipelineLogger

__all__ = [
    # Database
    "get_client",
    "fetch_flagged_leads",
    "mark_status",
    "mark_failure",
    "update_lead_field",
    # Pipeline steps
    "run_input_transform",
    "run_plan_prompt",
    "generate_blocks",
    "run_stage2",
    "prep_html",
    "run_stage3",
    "html_to_json_step",
    "clean_json",
    "upload_pages",
    # OpenAI client
    "call_llm",
    "call_llm_with_file",
    "process_prompt_batch",
    # Logging
    "PipelineLogger",
]

