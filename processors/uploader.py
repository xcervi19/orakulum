"""
Uploader

Uploads processed JSON content to Supabase.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import dotenv
from supabase import create_client, Client

dotenv.load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Table name
TABLE_NAME = "client_learning_pages"


def get_supabase_client() -> Client:
    """Create Supabase client."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables"
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def extract_page_index(filename: str) -> Optional[int]:
    """
    Extract page index number from filename.
    
    Examples:
        page_0.json -> 0
        prompt_block_1.json -> 1
        parthtml12.json -> 12
    """
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else None


def upload_single_page(
    client_id: str,
    page_index: int,
    content: Union[List, Dict],
    supabase: Optional[Client] = None
) -> Dict:
    """
    Upload a single page for a client.
    Uses UPSERT - inserts new or updates existing.
    
    Returns the inserted/updated row data.
    """
    if supabase is None:
        supabase = get_supabase_client()
    
    data = {
        "client_id": client_id,
        "page_index": page_index,
        "content": content,
    }
    
    result = (
        supabase.table(TABLE_NAME)
        .upsert(data, on_conflict="client_id,page_index")
        .execute()
    )
    
    return result.data[0] if result.data else {}


def upload_client_pages(client_id: str, pages: List[Union[Dict, List]]) -> List[Dict]:
    """
    Upload multiple pages for a client.
    Each item becomes one page (page_index = list index).
    
    Returns list of inserted/updated row data.
    """
    supabase = get_supabase_client()
    results = []
    
    for page_index, content in enumerate(pages):
        row = upload_single_page(client_id, page_index, content, supabase)
        results.append(row)
        row_id = row.get("id", "?")
        print(f"   ✅ Page {page_index} uploaded (id: {row_id})")
    
    return results


def upload_from_directory(client_id: str, directory: str) -> Dict[str, Any]:
    """
    Upload all JSON files from a directory.
    Page index is extracted from filename numbers.
    
    Args:
        client_id: Client UUID
        directory: Directory with JSON files
        
    Returns:
        Summary dict with results
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"❌ Directory not found: {directory}")
        return {"total": 0, "success": 0, "failed": 0}
    
    json_files = sorted(dir_path.glob("*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found in {directory}")
        return {"total": 0, "success": 0, "failed": 0}
    
    supabase = get_supabase_client()
    print(f"📁 Found {len(json_files)} JSON files in {directory}")
    
    results = {"total": len(json_files), "success": 0, "failed": 0, "pages": []}
    
    for json_file in json_files:
        page_index = extract_page_index(json_file.name)
        
        if page_index is None:
            print(f"   ⚠️ Skipping {json_file.name} - no number in filename")
            continue
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            row = upload_single_page(client_id, page_index, content, supabase)
            results["success"] += 1
            results["pages"].append({"file": json_file.name, "page_index": page_index})
            
            row_id = row.get("id", "?")
            print(f"   ✅ {json_file.name} → page_index={page_index} (id: {row_id})")
            
        except Exception as e:
            results["failed"] += 1
            print(f"   ❌ {json_file.name} failed: {e}")
    
    print(f"\n✨ Uploaded {results['success']}/{results['total']} pages for client {client_id}")
    return results


def delete_client_pages(client_id: str) -> int:
    """
    Delete all pages for a client.
    
    Returns number of deleted rows.
    """
    supabase = get_supabase_client()
    
    result = (
        supabase.table(TABLE_NAME)
        .delete()
        .eq("client_id", client_id)
        .execute()
    )
    
    deleted = len(result.data) if result.data else 0
    print(f"🗑️ Deleted {deleted} pages for client {client_id}")
    return deleted


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload learning content to Supabase")
    parser.add_argument("client_id", help="Client UUID")
    parser.add_argument("--directory", "-d", required=True, help="Directory with JSON files")
    parser.add_argument("--delete", action="store_true", help="Delete all pages for client")
    
    args = parser.parse_args()
    
    if args.delete:
        delete_client_pages(args.client_id)
    else:
        upload_from_directory(args.client_id, args.directory)
