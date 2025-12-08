import os
from datetime import datetime
from typing import Dict, List
import dotenv
import requests
from supabase import create_client, Client

dotenv.load_dotenv()

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Output file
OUTPUT_FILE = "database_schema.sql"


def get_client() -> Client:
    """Create Supabase client."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables"
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_tables(supabase: Client) -> List[Dict]:
    """Get all tables in public schema."""
    result = supabase.rpc('get_tables_info', {}).execute()
    return result.data if result.data else []


def discover_all_tables(supabase: Client) -> List[str]:
    """
    Automatically discover all tables in the public schema.
    Uses HTTP requests to query information_schema via Supabase REST API.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("Missing Supabase credentials")
    
    # Extract the project reference from URL
    base_url = SUPABASE_URL.rstrip('/')
    
    # Query information_schema.tables via REST API
    # Note: This requires the service key for admin access
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try to query information_schema via PostgREST
    # Format: https://xxxxx.supabase.co/rest/v1/information_schema.tables?table_schema=eq.public
    try:
        url = f"{base_url}/rest/v1/information_schema.tables"
        params = {
            "table_schema": "eq.public",
            "table_type": "eq.BASE TABLE",
            "select": "table_name"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                tables = [row['table_name'] for row in data if 'table_name' in row]
                return sorted(tables)
        else:
            print(f"⚠️  Could not query information_schema directly (status {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            print(f"   Falling back to alternative method...")
    except Exception as e:
        print(f"⚠️  Error querying information_schema: {e}")
        print(f"   Falling back to alternative method...")
    
    # Fallback: Try to use Supabase client's introspection capabilities
    # or try common table patterns
    print("⚠️  Using fallback method - trying to discover tables...")
    discovered_tables = []
    
    # Try some common table names (you can extend this list)
    # We'll try a few common patterns
    common_names = ['client_learning_pages', 'junior_leads']
    
    for table_name in common_names:
        try:
            # Try to access the table - if it exists, this won't throw an error
            result = supabase.table(table_name).select("*").limit(0).execute()
            discovered_tables.append(table_name)
        except Exception as e:
            # Table doesn't exist or we can't access it
            pass
    
    if discovered_tables:
        return discovered_tables
    
    # Last resort: return empty list and let user know
    print("❌ Could not automatically discover tables.")
    print("   Please specify tables manually using --tables argument")
    return []


def export_schema_via_rpc(output_file: str = OUTPUT_FILE) -> str:
    """
    Export database schema using Supabase.
    Note: This requires a custom RPC function in Supabase.
    """
    supabase = get_client()
    
    # Query information_schema for tables
    tables_query = """
        SELECT 
            table_name,
            table_type
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """
    
    # Query columns for each table
    columns_query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """
    
    # Since we can't run raw SQL directly via Supabase client,
    # we'll use the REST API to get table info
    
    schema_lines = []
    schema_lines.append(f"-- Database Schema Export")
    schema_lines.append(f"-- Generated: {datetime.now().isoformat()}")
    schema_lines.append(f"-- Supabase URL: {SUPABASE_URL}")
    schema_lines.append("")
    schema_lines.append("-- ============================================")
    schema_lines.append("-- TABLES IN PUBLIC SCHEMA")
    schema_lines.append("-- ============================================")
    schema_lines.append("")
    
    # Get list of tables by querying each known table
    known_tables = ['client_learning_pages']  # Add your tables here
    
    for table_name in known_tables:
        try:
            # Try to get one row to inspect structure
            result = supabase.table(table_name).select("*").limit(0).execute()
            
            schema_lines.append(f"-- Table: {table_name}")
            schema_lines.append(f"-- (Schema details require database function)")
            schema_lines.append("")
            
        except Exception as e:
            schema_lines.append(f"-- Table: {table_name} - Error: {e}")
            schema_lines.append("")
    
    # Write to file
    schema_content = "\n".join(schema_lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(schema_content)
    
    print(f"✅ Schema exported to {output_file}")
    return output_file


def export_schema_simple(output_file: str = OUTPUT_FILE, tables: List[str] = None) -> str:
    """
    Export basic schema info by inspecting table structure.
    Automatically discovers all tables if none are specified.
    Works without needing custom database functions.
    """
    supabase = get_client()
    
    schema_lines = []
    schema_lines.append(f"-- Database Schema Export")
    schema_lines.append(f"-- Generated: {datetime.now().isoformat()}")
    schema_lines.append(f"-- Supabase Project: {SUPABASE_URL}")
    schema_lines.append("")
    
    # Auto-discover tables if not provided
    if tables is None:
        print("🔍 Discovering tables automatically...")
        tables = discover_all_tables(supabase)
        
        if not tables:
            print("❌ No tables discovered. Using fallback list.")
            tables = ['client_learning_pages']  # Fallback
        else:
            print(f"✅ Found {len(tables)} table(s): {', '.join(tables)}")
    
    for table_name in tables:
        schema_lines.append("-- " + "=" * 60)
        schema_lines.append(f"-- TABLE: {table_name}")
        schema_lines.append("-- " + "=" * 60)
        
        try:
            # Get one row to inspect column structure
            result = supabase.table(table_name).select("*").limit(1).execute()
            
            if result.data and len(result.data) > 0:
                row = result.data[0]
                schema_lines.append(f"CREATE TABLE {table_name} (")
                
                columns = []
                for col_name, col_value in row.items():
                    # Infer type from value
                    if col_value is None:
                        col_type = "unknown"
                    elif isinstance(col_value, bool):
                        col_type = "boolean"
                    elif isinstance(col_value, int):
                        col_type = "integer"
                    elif isinstance(col_value, float):
                        col_type = "numeric"
                    elif isinstance(col_value, dict) or isinstance(col_value, list):
                        col_type = "jsonb"
                    else:
                        col_type = "text"
                    
                    columns.append(f"    {col_name} {col_type}")
                
                schema_lines.append(",\n".join(columns))
                schema_lines.append(");")
            else:
                # Empty table - just note it exists
                schema_lines.append(f"-- Table exists but is empty (cannot infer schema)")
            
            # Get row count
            count_result = supabase.table(table_name).select("*", count="exact").limit(0).execute()
            row_count = count_result.count if count_result.count else 0
            schema_lines.append(f"-- Row count: {row_count}")
            
        except Exception as e:
            schema_lines.append(f"-- Error accessing table: {e}")
        
        schema_lines.append("")
    
    # Write to file
    schema_content = "\n".join(schema_lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(schema_content)
    
    print(f"✅ Schema exported to {output_file}")
    print(f"📊 Tables inspected: {len(tables)}")
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export Supabase database schema")
    parser.add_argument("--output", "-o", default=OUTPUT_FILE,
                        help=f"Output file (default: {OUTPUT_FILE})")
    parser.add_argument("--tables", "-t", nargs="+", 
                        default=None,
                        help="Specific tables to inspect (default: auto-discover all tables)")
    
    args = parser.parse_args()
    
    # Use specified tables or auto-discover
    export_schema_simple(args.output, tables=args.tables if args.tables else None)

