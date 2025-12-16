#!/usr/bin/env python3
"""
Orakulum Pipeline Runner

Automated end-to-end career-plan generation pipeline:
1. Fetches flagged leads from Supabase
2. Processes each lead through all pipeline steps
3. Uploads final content to client_learning_pages

Usage:
    python3 run_pipeline.py                    # Process all flagged leads
    python3 run_pipeline.py --client CLIENT_ID # Process specific client
    python3 run_pipeline.py --dry-run          # Preview without processing
    python3 run_pipeline.py --resume CLIENT_ID # Resume failed processing
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from pipeline.db import (
    fetch_flagged_leads,
    fetch_lead_by_id,
    mark_status,
    mark_failure,
    unblock_lead,
    STATUS_FLAGGED,
    STATUS_PROCESSING,
    STATUS_UPLOADED,
    STATUS_BLOCKED,
)
from pipeline.steps import (
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
from pipeline.logger import PipelineLogger, setup_run_directory
from processors.uploader import delete_client_pages


MAX_RETRIES = 3


def process_client(lead: dict, run_dir: Path = None) -> bool:
    """
    Process a single client through all pipeline steps.
    
    Args:
        lead: Lead dictionary with id, description, etc.
        run_dir: Optional existing run directory (for resume)
    
    Returns:
        True if successful, False if failed
    """
    client_id = lead["id"]
    
    # Setup run directory if not provided
    if run_dir is None:
        run_dir = setup_run_directory(client_id)
    
    logger = PipelineLogger(run_dir, client_id)
    
    try:
        # Mark as processing
        mark_status(client_id, STATUS_PROCESSING)
        logger.log_info(f"Starting pipeline for client {client_id}")
        logger.log_info(f"Run directory: {run_dir}")
        
        # Step 2: Input transform
        run_input_transform(lead, run_dir, logger)
        
        # Step 3: Plan synthesis
        run_plan_prompt(lead, run_dir, logger)
        
        # Step 4: Generate block prompts
        generate_blocks(lead, run_dir, logger)
        
        # Step 5: Stage 2 - ChatGPT processing
        run_stage2(lead, run_dir, logger)
        
        # Step 6: Prepare HTML prompts
        prep_html(lead, run_dir, logger)
        
        # Step 7: Stage 3 - ChatGPT HTML generation
        run_stage3(lead, run_dir, logger)
        
        # Step 8: HTML to JSON
        html_to_json_step(lead, run_dir, logger)
        
        # Step 9: Clean and upload
        clean_json(lead, run_dir, logger)
        upload_pages(lead, run_dir, logger)
        
        # Mark as completed
        mark_status(client_id, STATUS_UPLOADED)
        logger.finalize("completed")
        
        return True
        
    except Exception as exc:
        logger.log_step_error("pipeline", exc)
        mark_failure(client_id, exc, block=True)
        logger.finalize("failed")
        
        print(f"\n❌ Pipeline failed for client {client_id}")
        print(f"   Error: {exc}")
        print(f"   Run directory: {run_dir}")
        print(f"   Status set to: {STATUS_BLOCKED}")
        
        return False


def process_all_flagged() -> dict:
    """
    Process all leads with status='FLAGGED'.
    
    Returns:
        Summary dict with counts of processed, succeeded, failed
    """
    leads = fetch_flagged_leads()
    
    if not leads:
        print("📭 No flagged leads to process")
        return {"total": 0, "succeeded": 0, "failed": 0}
    
    print(f"\n🚀 Found {len(leads)} flagged lead(s) to process")
    print("=" * 60)
    
    results = {"total": len(leads), "succeeded": 0, "failed": 0, "clients": []}
    
    for i, lead in enumerate(leads, 1):
        print(f"\n[{i}/{len(leads)}] Processing: {lead['id']}")
        print(f"    Name: {lead.get('name', 'N/A')}")
        print(f"    Description: {lead.get('description', '')[:100]}...")
        print("-" * 60)
        
        success = process_client(lead)
        
        if success:
            results["succeeded"] += 1
            results["clients"].append({"id": lead["id"], "status": "succeeded"})
        else:
            results["failed"] += 1
            results["clients"].append({"id": lead["id"], "status": "failed"})
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE SUMMARY")
    print("=" * 60)
    print(f"   Total processed: {results['total']}")
    print(f"   ✅ Succeeded: {results['succeeded']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    return results


def dry_run() -> None:
    """Show what would be processed without actually processing."""
    leads = fetch_flagged_leads()
    
    if not leads:
        print("📭 No flagged leads to process")
        return
    
    print(f"\n📋 DRY RUN - Would process {len(leads)} lead(s):")
    print("=" * 60)
    
    for i, lead in enumerate(leads, 1):
        print(f"\n{i}. {lead['id']}")
        print(f"   Name: {lead.get('name', 'N/A')}")
        print(f"   Email: {lead.get('email', 'N/A')}")
        print(f"   Description: {lead.get('description', '')[:80]}...")


def resume_client(client_id: str) -> bool:
    """
    Resume processing for a specific client.
    Finds the latest run directory and continues from where it left off.
    """
    lead = fetch_lead_by_id(client_id)
    
    if not lead:
        print(f"❌ Client not found: {client_id}")
        return False
    
    # Find latest run directory
    runs_base = Path("runs") / client_id
    if runs_base.exists():
        run_dirs = sorted(runs_base.iterdir(), reverse=True)
        if run_dirs:
            run_dir = run_dirs[0]
            print(f"📂 Resuming from: {run_dir}")
            return process_client(lead, run_dir)
    
    # No existing run, start fresh
    print(f"📂 No existing run found, starting fresh")
    return process_client(lead)


def delete_client(client_id: str, reset_status: bool = False) -> bool:
    """
    Delete all pages for a client and optionally reset their status.
    
    Args:
        client_id: Client UUID
        reset_status: If True, also reset status to FLAGGED for reprocessing
        
    Returns:
        True if successful
    """
    lead = fetch_lead_by_id(client_id)
    
    if not lead:
        print(f"❌ Client not found: {client_id}")
        return False
    
    print(f"\n🗑️  Deleting data for client: {client_id}")
    print(f"   Name: {lead.get('name', 'N/A')}")
    
    # Delete pages from client_learning_pages
    deleted_count = delete_client_pages(client_id)
    
    # Optionally reset status
    if reset_status:
        unblock_lead(client_id)
        print(f"   ✅ Status reset to FLAGGED")
    
    print(f"\n✨ Deleted {deleted_count} pages for client {client_id}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Orakulum Pipeline Runner - Automated career plan generation"
    )
    parser.add_argument(
        "--client", "-c",
        help="Process specific client by ID"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview what would be processed without running"
    )
    parser.add_argument(
        "--resume", "-r",
        help="Resume processing for a specific client"
    )
    parser.add_argument(
        "--delete", "-d",
        help="Delete all pages for a client (client ID)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="When used with --delete, also reset client status to FLAGGED"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔮 ORAKULUM PIPELINE RUNNER")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        if args.delete:
            success = delete_client(args.delete, reset_status=args.reset)
            sys.exit(0 if success else 1)
        elif args.dry_run:
            dry_run()
        elif args.resume:
            success = resume_client(args.resume)
            sys.exit(0 if success else 1)
        elif args.client:
            lead = fetch_lead_by_id(args.client)
            if not lead:
                print(f"❌ Client not found: {args.client}")
                sys.exit(1)
            success = process_client(lead)
            sys.exit(0 if success else 1)
        else:
            results = process_all_flagged()
            sys.exit(0 if results["failed"] == 0 else 1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as exc:
        print(f"\n❌ Pipeline error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()

