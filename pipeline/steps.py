"""
Pipeline step implementations.
Each function implements one step of the career-plan generation pipeline.
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Optional

from .db import update_lead_field, mark_status
from .db import STATUS_PLAN_READY, STATUS_HTML_READY
from .logging_utils import PipelineLogger


def run_input_transform(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 2: Input transform prompt.
    Converts raw client description into structured JSON.
    
    Template: prompts/input_transform.txt
    Placeholder: [VSTUP] -> lead['description']
    """
    logger.log_step_start("input_transform", {"description_length": len(lead.get("description", ""))})
    start_time = time.time()
    
    # Load template
    template_path = Path("prompts/input_transform.txt")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Fill template
    prompt = template.replace("[VSTUP]", lead.get("description", ""))
    
    # Save prompt to run directory
    prompt_path = run_dir / "input_transform" / "prompt.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    # Output path for ChatGPT response
    output_path = run_dir / "input_transform" / "output.json"
    
    logger.log_info(f"Input transform prompt saved to {prompt_path}")
    logger.log_info("Waiting for ChatGPT response (run automate_chatgpt.py or paste manually)")
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("input_transform", duration_ms, str(prompt_path))
    
    return {
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
    }


def load_input_transform_result(lead_id: str, run_dir: Path, logger: PipelineLogger) -> Optional[Dict]:
    """
    Load the input transform result after ChatGPT has responded.
    Updates the lead in database with the parsed JSON.
    """
    output_path = run_dir / "input_transform" / "output.json"
    
    if not output_path.exists():
        logger.log_info(f"Waiting for input transform output at {output_path}")
        return None
    
    with open(output_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    
    # Store in database
    update_lead_field(lead_id, "input_transform", result)
    logger.log_info("Input transform result stored in database")
    
    return result


def run_plan_prompt(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 3: Plan synthesis prompt.
    Generates the 15-block master plan using init_plan.txt template.
    """
    logger.log_step_start("plan_prompt")
    start_time = time.time()
    
    # Load template
    template_path = Path("prompts/init_plan.txt")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Get input transform data (should be loaded already)
    input_data = lead.get("input_transform", {})
    
    # Fill template with structured data
    # (Adjust placeholders based on your actual template)
    prompt = template
    if isinstance(input_data, dict):
        for key, value in input_data.items():
            placeholder = f"[{key.upper()}]"
            if isinstance(value, str):
                prompt = prompt.replace(placeholder, value)
    
    # Also replace with description if template uses it
    prompt = prompt.replace("[DESCRIPTION]", lead.get("description", ""))
    prompt = prompt.replace("[VSTUP]", lead.get("description", ""))
    
    # Save prompt
    prompt_path = run_dir / "plan" / "prompt.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    output_path = run_dir / "plan" / "plan.txt"
    
    logger.log_info(f"Plan prompt saved to {prompt_path}")
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("plan_prompt", duration_ms, str(prompt_path))
    
    return {
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
    }


def load_plan_result(lead_id: str, run_dir: Path, logger: PipelineLogger) -> Optional[str]:
    """
    Load the plan result after ChatGPT has responded.
    Updates the lead in database with the plan text.
    """
    output_path = run_dir / "plan" / "plan.txt"
    
    if not output_path.exists():
        logger.log_info(f"Waiting for plan output at {output_path}")
        return None
    
    with open(output_path, "r", encoding="utf-8") as f:
        plan_text = f.read()
    
    # Store in database
    update_lead_field(lead_id, "plan", plan_text)
    logger.log_info("Plan text stored in database")
    
    return plan_text


def generate_blocks(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 4: Generate per-block prompts using manual.py.
    Parses the plan into individual block prompts.
    """
    logger.log_step_start("generate_blocks")
    start_time = time.time()
    
    plan_path = run_dir / "plan" / "plan.txt"
    output_dir = run_dir / "parsed_parts"
    
    # Run manual.py with client-specific paths
    cmd = [
        "python3", "manual.py",
        "--input", str(plan_path),
        "--output", str(output_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"manual.py failed: {result.stderr}")
    
    # Count generated files
    block_files = list(output_dir.glob("prompt_block_*.txt"))
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("generate_blocks", duration_ms)
    logger.log_info(f"Generated {len(block_files)} block prompts")
    
    return {
        "output_dir": str(output_dir),
        "block_count": len(block_files),
    }


def run_stage2(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 5: Send prompts to ChatGPT (Stage 2).
    Processes each block prompt through ChatGPT.
    """
    logger.log_step_start("stage2_chatgpt")
    start_time = time.time()
    
    input_dir = run_dir / "parsed_parts"
    output_dir = run_dir / "stage_2_generated_parts"
    
    # Run automate_chatgpt.py
    cmd = [
        "python3", "automate_chatgpt.py",
        "--input", str(input_dir),
        "--output", str(output_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    logger.log_info("This step requires ChatGPT automation...")
    
    # Note: This will be run separately or manually
    # For now, just prepare the directories
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("stage2_chatgpt", duration_ms)
    
    return {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
    }


def prep_html(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 6: Prepare HTML prompts.
    Wraps Stage 2 responses with HTML transform template.
    """
    logger.log_step_start("prep_html")
    start_time = time.time()
    
    input_dir = run_dir / "stage_2_generated_parts"
    output_dir = run_dir / "stage_2_prepared_html"
    
    # Run prepare_html_prompts.py
    cmd = [
        "python3", "prepare_html_prompts.py",
        "--input", str(input_dir),
        "--output", str(output_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"prepare_html_prompts.py failed: {result.stderr}")
    
    # Count prepared files
    html_files = list(output_dir.glob("*.txt"))
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("prep_html", duration_ms)
    logger.log_info(f"Prepared {len(html_files)} HTML prompts")
    
    return {
        "output_dir": str(output_dir),
        "file_count": len(html_files),
    }


def run_stage3(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 7: ChatGPT HTML generation (Stage 3).
    Processes HTML prompts through ChatGPT.
    """
    logger.log_step_start("stage3_chatgpt")
    start_time = time.time()
    
    input_dir = run_dir / "stage_2_prepared_html"
    output_dir = run_dir / "stage_3_generated_html"
    
    # Run automate_chatgpt.py for stage 3
    cmd = [
        "python3", "automate_chatgpt.py",
        "--input", str(input_dir),
        "--output", str(output_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    logger.log_info("This step requires ChatGPT automation...")
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("stage3_chatgpt", duration_ms)
    
    # Update status
    mark_status(lead["id"], STATUS_HTML_READY)
    
    return {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
    }


def html_to_json_step(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 8: HTML → JSON transformation.
    Converts HTML files to structured JSON.
    """
    logger.log_step_start("html_to_json")
    start_time = time.time()
    
    input_dir = run_dir / "stage_3_generated_html"
    output_dir = run_dir / "transformed"
    
    # Run html_to_json.py
    cmd = [
        "python3", "html_to_json.py",
        "--input", str(input_dir),
        "--output", str(output_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"html_to_json.py failed: {result.stderr}")
    
    # Count JSON files
    json_files = list(output_dir.glob("*.json"))
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("html_to_json", duration_ms)
    logger.log_info(f"Created {len(json_files)} JSON files")
    
    return {
        "output_dir": str(output_dir),
        "file_count": len(json_files),
    }


def clean_json(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 9a: Clean markdown artifacts from JSON.
    """
    logger.log_step_start("clean_json")
    start_time = time.time()
    
    json_dir = run_dir / "transformed"
    
    # Run clean_markdown.py
    cmd = [
        "python3", "clean_markdown.py",
        "--directory", str(json_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"clean_markdown.py failed: {result.stderr}")
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("clean_json", duration_ms)
    
    return {
        "directory": str(json_dir),
    }


def upload_pages(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 9b: Upload to Supabase.
    Uploads cleaned JSON files to client_learning_pages.
    """
    logger.log_step_start("upload_pages")
    start_time = time.time()
    
    json_dir = run_dir / "transformed"
    client_id = lead["id"]
    
    # Run upload_learning_content.py
    cmd = [
        "python3", "upload_learning_content.py",
        client_id,
        "--directory", str(json_dir),
    ]
    
    logger.log_info(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"upload_learning_content.py failed: {result.stderr}")
    
    # Count uploaded files
    json_files = list(json_dir.glob("*.json"))
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("upload_pages", duration_ms)
    logger.log_info(f"Uploaded {len(json_files)} pages for client {client_id}")
    
    return {
        "client_id": client_id,
        "page_count": len(json_files),
    }

