"""
Pipeline Module

Core pipeline components for the Orakulum automated career-plan generator.
Uses OpenAI API for all LLM operations.
"""

from .db import (
    get_client,
    fetch_flagged_leads,
    fetch_lead_by_id,
    mark_status,
    mark_failure,
    update_lead_field,
    get_leads_by_status,
    unblock_lead,
    STATUS_FLAGGED,
    STATUS_PROCESSING,
    STATUS_PLAN_READY,
    STATUS_HTML_READY,
    STATUS_UPLOADED,
    STATUS_ARCHIVED,
    STATUS_BLOCKED,
)
from .llm import (
    call_llm,
    call_llm_with_file,
    process_prompt_batch,
    estimate_tokens,
    estimate_cost,
)
from .logger import (
    PipelineLogger,
    setup_run_directory,
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

__all__ = [
    # Database
    "get_client",
    "fetch_flagged_leads",
    "fetch_lead_by_id",
    "mark_status",
    "mark_failure",
    "update_lead_field",
    "get_leads_by_status",
    "unblock_lead",
    # Status constants
    "STATUS_FLAGGED",
    "STATUS_PROCESSING",
    "STATUS_PLAN_READY",
    "STATUS_HTML_READY",
    "STATUS_UPLOADED",
    "STATUS_ARCHIVED",
    "STATUS_BLOCKED",
    # LLM
    "call_llm",
    "call_llm_with_file",
    "process_prompt_batch",
    "estimate_tokens",
    "estimate_cost",
    # Logging
    "PipelineLogger",
    "setup_run_directory",
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
]
