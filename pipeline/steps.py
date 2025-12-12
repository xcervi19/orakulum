"""
Pipeline Steps

Each function implements one step of the career-plan generation pipeline.
Uses OpenAI API for all LLM interactions.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional

from .db import update_lead_field, mark_status
from .db import STATUS_PLAN_READY, STATUS_HTML_READY
from .logger import PipelineLogger
from .llm import call_llm, process_prompt_batch

# Import processors
from processors.block_parser import parse_plan_blocks, fill_expand_template, load_expand_template
from processors.html_wrapper import wrap_directory
from processors.html_to_json import transform_html_directory
from processors.json_cleaner import clean_json_directory
from processors.uploader import upload_from_directory


def run_input_transform(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 1: Input transform prompt.
    Converts raw client description into structured JSON.
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
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    # Call OpenAI API
    logger.log_info("Calling OpenAI API for input transform...")
    
    response = call_llm(
        prompt=prompt,
        system_prompt="You are a career counselor assistant. Analyze the input and return structured JSON only.",
        json_mode=True
    )
    
    # Save response
    output_path = run_dir / "input_transform" / "output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)
    
    # Parse and store in database
    try:
        result_json = json.loads(response)
        update_lead_field(lead["id"], "input_transform", result_json)
        logger.log_info("Input transform result stored in database")
    except json.JSONDecodeError:
        logger.log_info("Response is not valid JSON, storing as text")
        result_json = {"raw": response}
        update_lead_field(lead["id"], "input_transform", result_json)
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("input_transform", duration_ms, str(output_path))
    
    return {
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
        "response_length": len(response),
        "parsed_data": result_json,
    }


def run_plan_prompt(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 2: Plan synthesis prompt.
    Generates the 15-block master plan.
    """
    logger.log_step_start("plan_prompt")
    start_time = time.time()
    
    # Load template
    template_path = Path("prompts/init_plan.txt")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Get input transform data (reload from file to ensure fresh data)
    input_transform_path = run_dir / "input_transform" / "output.json"
    input_data = {}
    if input_transform_path.exists():
        with open(input_transform_path, "r", encoding="utf-8") as f:
            try:
                input_data = json.load(f)
            except json.JSONDecodeError:
                pass
    
    # Build context from input_transform
    context_parts = []
    if input_data.get("obor"):
        context_parts.append(f"Obor: {input_data['obor']}")
    if input_data.get("seniorita"):
        context_parts.append(f"Seniorita: {input_data['seniorita']}")
    if input_data.get("hlavni_cil"):
        context_parts.append(f"Hlavní cíl: {input_data['hlavni_cil']}")
    if input_data.get("technologie"):
        context_parts.append(f"Technologie: {', '.join(input_data['technologie'])}")
    
    context = "\n".join(context_parts) if context_parts else lead.get("description", "")
    
    # Fill template - append context
    prompt = template
    if "[VSTUP]" in prompt:
        prompt = prompt.replace("[VSTUP]", context)
    else:
        prompt = prompt + f"\n\n### KONTEXT KLIENTA:\n{context}"
    
    # Save prompt
    prompt_path = run_dir / "plan" / "prompt.txt"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    
    # Call OpenAI API
    logger.log_info("Calling OpenAI API for plan generation...")
    
    response = call_llm(
        prompt=prompt,
        system_prompt="You are an expert career counselor. Generate a comprehensive 15-step career plan with <blok-n> tags as specified.",
        max_tokens=8000,
    )
    
    # Save response
    output_path = run_dir / "plan" / "plan.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(response)
    
    # Store in database
    update_lead_field(lead["id"], "plan", response)
    logger.log_info("Plan text stored in database")
    
    # Update status
    mark_status(lead["id"], STATUS_PLAN_READY)
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("plan_prompt", duration_ms, str(output_path))
    
    return {
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
        "response_length": len(response),
        "input_data": input_data,
    }


def generate_blocks(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 3: Parse plan into individual block prompts.
    """
    logger.log_step_start("generate_blocks")
    start_time = time.time()
    
    plan_path = run_dir / "plan" / "plan.txt"
    output_dir = run_dir / "parsed_parts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read plan
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_text = f.read()
    
    # Parse blocks
    blocks = parse_plan_blocks(plan_text)
    
    if not blocks:
        raise RuntimeError("No blocks found in plan")
    
    # Get client data from input_transform
    input_transform_path = run_dir / "input_transform" / "output.json"
    input_data = {}
    if input_transform_path.exists():
        with open(input_transform_path, "r", encoding="utf-8") as f:
            try:
                input_data = json.load(f)
            except json.JSONDecodeError:
                pass
    
    # Extract client parameters
    obor = input_data.get("obor", "nezadáno")
    seniorita = input_data.get("seniorita", "nezadáno")
    hlavni_cil = input_data.get("hlavni_cil", "nezadáno")
    
    # Load and fill template for each block
    template = load_expand_template()
    
    generated_files = []
    for block_number, block_content in blocks:
        filled = fill_expand_template(
            template=template,
            block_content=block_content,
            obor=obor,
            seniorita=seniorita,
            hlavni_cil=hlavni_cil
        )
        
        output_path = output_dir / f"prompt_block_{block_number}.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(filled)
        
        generated_files.append(str(output_path))
        logger.log_info(f"Generated block {block_number}")
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("generate_blocks", duration_ms)
    logger.log_info(f"Generated {len(generated_files)} block prompts")
    
    return {
        "output_dir": str(output_dir),
        "block_count": len(generated_files),
        "client_params": {"obor": obor, "seniorita": seniorita, "hlavni_cil": hlavni_cil},
    }


def run_stage2(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 4: Expand block prompts via OpenAI API.
    """
    logger.log_step_start("stage2_expand")
    start_time = time.time()
    
    input_dir = run_dir / "parsed_parts"
    output_dir = run_dir / "stage_2_generated_parts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.log_info("Processing block prompts via OpenAI API...")
    
    results = process_prompt_batch(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        system_prompt="You are an expert career counselor. Expand the given career plan section with detailed, actionable content in Czech.",
        pattern="prompt_block_*.txt"
    )
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("stage2_expand", duration_ms)
    logger.log_info(f"Stage 2: {results['success']} succeeded, {results['failed']} failed")
    
    if results['failed'] > 0:
        raise RuntimeError(f"Stage 2 failed for {results['failed']} files")
    
    return {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "results": results,
    }


def prep_html(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 5: Wrap expanded content with HTML transform template.
    """
    logger.log_step_start("prep_html")
    start_time = time.time()
    
    input_dir = run_dir / "stage_2_generated_parts"
    output_dir = run_dir / "stage_2_prepared_html"
    
    logger.log_info("Wrapping content with HTML template...")
    
    count = wrap_directory(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        template_path="prompts/html_transform.txt"
    )
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("prep_html", duration_ms)
    logger.log_info(f"Wrapped {count} files with HTML template")
    
    return {
        "output_dir": str(output_dir),
        "file_count": count,
    }


def run_stage3(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 6: HTML generation via OpenAI API.
    """
    logger.log_step_start("stage3_html")
    start_time = time.time()
    
    input_dir = run_dir / "stage_2_prepared_html"
    output_dir = run_dir / "stage_3_generated_html"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.log_info("Processing HTML prompts via OpenAI API...")
    
    results = process_prompt_batch(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        system_prompt="You are a UI/HTML expert. Transform the input into semantic HTML with data-ui attributes. Output only valid HTML, no markdown, no explanations.",
        pattern="*.txt"
    )
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("stage3_html", duration_ms)
    logger.log_info(f"Stage 3: {results['success']} succeeded, {results['failed']} failed")
    
    if results['failed'] > 0:
        raise RuntimeError(f"Stage 3 failed for {results['failed']} files")
    
    # Update status
    mark_status(lead["id"], STATUS_HTML_READY)
    
    return {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "results": results,
    }


def html_to_json_step(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 7: Transform HTML to structured JSON.
    """
    logger.log_step_start("html_to_json")
    start_time = time.time()
    
    input_dir = run_dir / "stage_3_generated_html"
    output_dir = run_dir / "transformed"
    
    logger.log_info("Converting HTML to JSON...")
    
    results = transform_html_directory(
        input_dir=str(input_dir),
        output_dir=str(output_dir)
    )
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("html_to_json", duration_ms)
    logger.log_info(f"Transformed {results['success']} files to JSON")
    
    return {
        "output_dir": str(output_dir),
        "results": results,
    }


def clean_json(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 8: Clean markdown artifacts from JSON.
    """
    logger.log_step_start("clean_json")
    start_time = time.time()
    
    json_dir = run_dir / "transformed"
    
    logger.log_info("Cleaning markdown artifacts...")
    
    results = clean_json_directory(str(json_dir))
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("clean_json", duration_ms)
    
    return {
        "directory": str(json_dir),
        "results": results,
    }


def upload_pages(lead: Dict, run_dir: Path, logger: PipelineLogger) -> Dict:
    """
    Step 9: Upload to Supabase.
    """
    logger.log_step_start("upload_pages")
    start_time = time.time()
    
    json_dir = run_dir / "transformed"
    client_id = lead["id"]
    
    logger.log_info(f"Uploading pages for client {client_id}...")
    
    results = upload_from_directory(client_id, str(json_dir))
    
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_step_complete("upload_pages", duration_ms)
    logger.log_info(f"Uploaded {results['success']} pages")
    
    return {
        "client_id": client_id,
        "results": results,
    }
