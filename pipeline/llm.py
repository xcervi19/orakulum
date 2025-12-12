"""
OpenAI API Client for the pipeline.
Handles all LLM interactions using the OpenAI Chat Completions API.
"""

import os
import time
from typing import Optional, Dict, Any
import json
import dotenv

dotenv.load_dotenv()

# OpenAI settings from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def get_openai_client():
    """Get OpenAI client instance."""
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY environment variable")
    
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    json_mode: bool = False,
) -> str:
    """
    Call OpenAI Chat Completions API with retry logic.
    
    Args:
        prompt: The user prompt to send
        system_prompt: Optional system message
        model: Model to use (default: from env)
        max_tokens: Max response tokens (default: from env)
        temperature: Sampling temperature (default: from env)
        json_mode: If True, request JSON response format
        
    Returns:
        The assistant's response text
        
    Raises:
        RuntimeError: If all retries fail
    """
    client = get_openai_client()
    
    model = model or OPENAI_MODEL
    max_tokens = max_tokens or OPENAI_MAX_TOKENS
    temperature = temperature if temperature is not None else OPENAI_TEMPERATURE
    
    # Build messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Request parameters
    params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    if json_mode:
        params["response_format"] = {"type": "json_object"}
    
    # Retry loop
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(**params)
            return response.choices[0].message.content
            
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Rate limit - wait longer
            if "rate_limit" in error_str or "429" in str(e):
                wait_time = RETRY_DELAY * (attempt + 1) * 2
                print(f"   ⚠️ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                # Other errors - standard retry
                if attempt < MAX_RETRIES - 1:
                    print(f"   ⚠️ API error (attempt {attempt + 1}): {e}")
                    time.sleep(RETRY_DELAY * (attempt + 1))
    
    raise RuntimeError(f"OpenAI API failed after {MAX_RETRIES} retries: {last_error}")


def call_llm_with_file(
    prompt_file: str,
    output_file: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    Read prompt from file, call LLM, save response to file.
    
    Args:
        prompt_file: Path to prompt file
        output_file: Path to save response
        system_prompt: Optional system message
        **kwargs: Additional arguments for call_llm
        
    Returns:
        The response text
    """
    # Read prompt
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    # Call LLM
    response = call_llm(prompt, system_prompt=system_prompt, **kwargs)
    
    # Save response
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(response)
    
    return response


def process_prompt_batch(
    input_dir: str,
    output_dir: str,
    system_prompt: Optional[str] = None,
    pattern: str = "*.txt",
    **kwargs
) -> Dict[str, Any]:
    """
    Process all prompt files in a directory.
    
    Args:
        input_dir: Directory with prompt files
        output_dir: Directory to save responses
        system_prompt: Optional system message for all prompts
        pattern: Glob pattern for input files
        **kwargs: Additional arguments for call_llm
        
    Returns:
        Summary dict with counts and results
    """
    from pathlib import Path
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    files = sorted(input_path.glob(pattern))
    
    if not files:
        return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
    
    results = {
        "total": len(files),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "files": []
    }
    
    for i, input_file in enumerate(files, 1):
        output_file = output_path / input_file.name
        
        # Skip if output exists
        if output_file.exists():
            print(f"   ⏭️ [{i}/{len(files)}] Skipping: {input_file.name} (exists)")
            results["skipped"] += 1
            results["files"].append({"name": input_file.name, "status": "skipped"})
            continue
        
        print(f"   🔄 [{i}/{len(files)}] Processing: {input_file.name}")
        
        try:
            response = call_llm_with_file(
                str(input_file),
                str(output_file),
                system_prompt=system_prompt,
                **kwargs
            )
            
            results["success"] += 1
            results["files"].append({
                "name": input_file.name,
                "status": "success",
                "response_length": len(response)
            })
            print(f"   ✅ [{i}/{len(files)}] Completed: {input_file.name} ({len(response)} chars)")
            
        except Exception as e:
            results["failed"] += 1
            results["files"].append({
                "name": input_file.name,
                "status": "failed",
                "error": str(e)
            })
            print(f"   ❌ [{i}/{len(files)}] Failed: {input_file.name} - {e}")
    
    return results


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count (4 chars per token approximation).
    For accurate counts, use tiktoken library.
    """
    return len(text) // 4


def estimate_cost(input_tokens: int, output_tokens: int, model: str = None) -> float:
    """
    Estimate API cost based on token counts.
    
    Pricing (as of 2024, GPT-4o):
    - Input: $5 / 1M tokens
    - Output: $15 / 1M tokens
    """
    model = model or OPENAI_MODEL
    
    # GPT-4o pricing
    if "gpt-4o" in model:
        input_cost = (input_tokens / 1_000_000) * 5
        output_cost = (output_tokens / 1_000_000) * 15
    # GPT-4 pricing
    elif "gpt-4" in model:
        input_cost = (input_tokens / 1_000_000) * 30
        output_cost = (output_tokens / 1_000_000) * 60
    # GPT-3.5 pricing
    else:
        input_cost = (input_tokens / 1_000_000) * 0.5
        output_cost = (output_tokens / 1_000_000) * 1.5
    
    return input_cost + output_cost
