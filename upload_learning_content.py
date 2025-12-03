import json
import re
from pathlib import Path
import os
from typing import Union, Optional, List, Dict
import dotenv
from supabase import create_client, Client

dotenv.load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Default directory for transformed JSON files
TRANSFORMED_DIR = "transformed"

def get_client() -> Client:
    """Create Supabase client."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables"
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def upload_single_page(
    client_id: str,
    page_index: int,
    content: Union[List, Dict],
    supabase: Optional[Client] = None
) -> Dict:
    """
    Upload a single JSON page for a client.
    Uses UPSERT - inserts new or updates existing.
    
    Returns the inserted/updated row data.
    """
    if supabase is None:
        supabase = get_client()
    
    data = {
        "client_id": client_id,
        "page_index": page_index,
        "content": content,
    }
    
    result = (
        supabase.table("client_learning_pages")
        .upsert(data, on_conflict="client_id,page_index")
        .execute()
    )
    
    return result.data[0] if result.data else {}


def upload_client_pages(client_id: str, pages: List[Union[Dict, List]]) -> List[Dict]:
    """
    Upload multiple pages for a client.
    Each item in pages list becomes one page (page_index = list index).
    
    Returns list of inserted/updated row data.
    """
    supabase = get_client()
    results = []
    
    for page_index, content in enumerate(pages):
        row = upload_single_page(client_id, page_index, content, supabase)
        results.append(row)
        row_id = row.get("id", "?")
        print(f"✅ Uploaded page {page_index} for client {client_id} (id: {row_id})")
    
    return results


def upload_from_json_file(client_id: str, file_path: str, page_index: int = 0) -> Dict:
    """
    Upload content from a JSON file as a single page.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    row = upload_single_page(client_id, page_index, content)
    print(f"✅ Uploaded {file_path} as page {page_index} for client {client_id}")
    return row


def extract_page_index(filename: str) -> Optional[int]:
    """
    Extract page index number from filename.
    Examples:
        parthtml0.json -> 0
        parthtml12.json -> 12
        page_5.json -> 5
    Returns None if no number found.
    """
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else None


def upload_from_directory(client_id: str, directory: str = TRANSFORMED_DIR) -> List[Dict]:
    """
    Upload all JSON files from a directory as pages.
    Page index is extracted from the number in the filename.
    
    Example directory structure:
        /transformed/
            parthtml0.json  -> page_index 0
            parthtml1.json  -> page_index 1
            parthtml6.json  -> page_index 6
    """
    dir_path = Path(directory)
    json_files = sorted(dir_path.glob("*.json"))
    
    if not json_files:
        raise ValueError(f"No JSON files found in {directory}")
    
    supabase = get_client()
    results = []
    
    print(f"📁 Found {len(json_files)} JSON files in {directory}")
    
    for json_file in json_files:
        # Extract page_index from filename
        page_index = extract_page_index(json_file.name)
        
        if page_index is None:
            print(f"   ⚠️  Skipping {json_file.name} - no number in filename")
            continue
        
        # Load JSON content
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Upload to database
        row = upload_single_page(client_id, page_index, content, supabase)
        results.append(row)
        row_id = row.get("id", "?")
        print(f"   ✅ {json_file.name} → page_index={page_index} (id: {row_id})")
    
    print(f"\n✨ Done! Uploaded {len(results)} pages for client {client_id}")
    return results


def delete_client_pages(client_id: str) -> int:
    """
    Delete all pages for a client.
    Returns number of deleted rows.
    """
    supabase = get_client()
    
    result = (
        supabase.table("client_learning_pages")
        .delete()
        .eq("client_id", client_id)
        .execute()
    )
    
    deleted = len(result.data) if result.data else 0
    print(f"🗑️  Deleted {deleted} pages for client {client_id}")
    return deleted


def upload_transformed_output(client_id: str, page_index: int = 0) -> Dict:
    """
    Convenience function to upload the transformed/output.json file.
    """
    output_path = Path(__file__).parent / "transformed" / "output.json"
    return upload_from_json_file(client_id, str(output_path), page_index)


# =============================================================================
# Usage Examples
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload learning content to Supabase")
    parser.add_argument("client_id", help="Client ID")
    parser.add_argument("--directory", "-d", default=TRANSFORMED_DIR, 
                        help=f"Directory with JSON files (default: {TRANSFORMED_DIR})")
    parser.add_argument("--file", "-f", help="Upload single JSON file instead of directory")
    parser.add_argument("--page-index", "-p", type=int, default=0, 
                        help="Page index for single file upload (default: 0)")
    parser.add_argument("--delete", action="store_true", help="Delete all pages for client")
    
    args = parser.parse_args()
    
    if args.delete:
        delete_client_pages(args.client_id)
    elif args.file:
        upload_from_json_file(args.client_id, args.file, args.page_index)
    else:
        # Default: upload all JSON files from transformed/ directory
        upload_from_directory(args.client_id, args.directory)
