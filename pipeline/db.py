"""
Database operations for the pipeline.
Handles all Supabase interactions for junior_leads processing.
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import dotenv
from supabase import create_client, Client

dotenv.load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Status constants
STATUS_FLAGGED = "FLAGGED"
STATUS_PROCESSING = "PROCESSING"
STATUS_PLAN_READY = "PLAN_READY"
STATUS_HTML_READY = "HTML_READY"
STATUS_UPLOADED = "UPLOADED"
STATUS_ARCHIVED = "ARCHIVED"
STATUS_BLOCKED = "BLOCKED"


def get_client() -> Client:
    """Create Supabase client."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables"
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def fetch_flagged_leads() -> List[Dict]:
    """
    Fetch all leads with status='FLAGGED' ready for processing.
    Returns list of lead dictionaries with id, description, name, email.
    """
    supabase = get_client()
    
    result = (
        supabase.table("junior_leads")
        .select("id, name, email, description, status, input_transform, plan")
        .eq("status", STATUS_FLAGGED)
        .execute()
    )
    
    return result.data if result.data else []


def fetch_lead_by_id(lead_id: str) -> Optional[Dict]:
    """Fetch a single lead by ID."""
    supabase = get_client()
    
    result = (
        supabase.table("junior_leads")
        .select("*")
        .eq("id", lead_id)
        .single()
        .execute()
    )
    
    return result.data if result.data else None


def mark_status(lead_id: str, status: str) -> Dict:
    """
    Update lead status and set appropriate timestamps.
    """
    supabase = get_client()
    
    update_data = {"status": status}
    
    # Set timestamps based on status
    if status == STATUS_PROCESSING:
        update_data["processing_started_at"] = datetime.utcnow().isoformat()
    elif status in [STATUS_UPLOADED, STATUS_ARCHIVED]:
        update_data["processing_completed_at"] = datetime.utcnow().isoformat()
    
    # Clear error when starting fresh
    if status == STATUS_PROCESSING:
        update_data["last_error"] = None
    
    result = (
        supabase.table("junior_leads")
        .update(update_data)
        .eq("id", lead_id)
        .execute()
    )
    
    return result.data[0] if result.data else {}


def mark_failure(lead_id: str, error: Exception, block: bool = False) -> Dict:
    """
    Mark a lead as failed with error message.
    If block=True, sets status to BLOCKED for manual intervention.
    """
    supabase = get_client()
    
    error_msg = f"{type(error).__name__}: {str(error)}"
    
    update_data = {
        "last_error": error_msg,
    }
    
    if block:
        update_data["status"] = STATUS_BLOCKED
    
    result = (
        supabase.table("junior_leads")
        .update(update_data)
        .eq("id", lead_id)
        .execute()
    )
    
    return result.data[0] if result.data else {}


def update_lead_field(lead_id: str, field: str, value: Any) -> Dict:
    """
    Update a specific field on a lead.
    Used for storing input_transform JSON and plan text.
    """
    supabase = get_client()
    
    result = (
        supabase.table("junior_leads")
        .update({field: value})
        .eq("id", lead_id)
        .execute()
    )
    
    return result.data[0] if result.data else {}


def get_leads_by_status(status: str) -> List[Dict]:
    """Get all leads with a specific status."""
    supabase = get_client()
    
    result = (
        supabase.table("junior_leads")
        .select("*")
        .eq("status", status)
        .execute()
    )
    
    return result.data if result.data else []


def unblock_lead(lead_id: str) -> Dict:
    """
    Reset a blocked lead back to FLAGGED status for reprocessing.
    """
    return mark_status(lead_id, STATUS_FLAGGED)

