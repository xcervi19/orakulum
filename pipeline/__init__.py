"""
Orakulum Pipeline Module

Automated career-plan generation pipeline that processes junior_leads
through ChatGPT prompts and uploads learning content to Supabase.
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
from .logging_utils import PipelineLogger

__all__ = [
    "get_client",
    "fetch_flagged_leads",
    "mark_status",
    "mark_failure",
    "update_lead_field",
    "run_input_transform",
    "run_plan_prompt",
    "generate_blocks",
    "run_stage2",
    "prep_html",
    "run_stage3",
    "html_to_json_step",
    "clean_json",
    "upload_pages",
    "PipelineLogger",
]

