"""
JSON Cleaner

Removes markdown artifacts from JSON text nodes.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Union


def clean_text(text: str) -> str:
    """
    Clean markdown artifacts from text.
    
    Removes:
    - **bold** markers
    - *italic* markers
    - ``` and ```` code block markers
    - Leading bullet markers (* ) at line start
    """
    # Remove bold: **text** -> text
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # Remove italic: *text* -> text (but not ** which is bold)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    
    # Remove code block markers (``` and ````)
    text = re.sub(r'````?', '', text)
    
    # Remove leading bullet markers at line start: "* text" -> "text"
    text = re.sub(r'^(\s*)\* ', r'\1', text, flags=re.MULTILINE)
    
    # Clean up excessive whitespace/newlines left behind
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip() if text.strip() == '' and text != '' else text


def clean_node(node: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Recursively traverse JSON structure and clean text nodes.
    """
    if isinstance(node, dict):
        # Check if this is a text node
        if node.get("type") == "text" and "text" in node:
            node["text"] = clean_text(node["text"])
        
        # Recursively process all values
        for key, value in node.items():
            node[key] = clean_node(value)
        
        return node
    
    elif isinstance(node, list):
        return [clean_node(item) for item in node]
    
    else:
        return node


def clean_markdown_artifacts(data: Union[Dict, List]) -> Union[Dict, List]:
    """
    Clean markdown artifacts from JSON data.
    
    Args:
        data: JSON data (dict or list)
        
    Returns:
        Cleaned JSON data
    """
    return clean_node(data)


def clean_json_file(file_path: str) -> bool:
    """
    Clean a single JSON file in place.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        True if successful
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cleaned = clean_markdown_artifacts(data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"   ❌ Error cleaning {file_path}: {e}")
        return False


def clean_json_directory(directory: str, pattern: str = "*.json") -> Dict[str, Any]:
    """
    Clean all JSON files in a directory.
    
    Args:
        directory: Directory with JSON files
        pattern: Glob pattern for files
        
    Returns:
        Summary dict with counts
    """
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"❌ Directory not found: {directory}")
        return {"total": 0, "success": 0, "failed": 0}
    
    json_files = sorted(dir_path.glob(pattern))
    
    if not json_files:
        print(f"❌ No {pattern} files found in {directory}")
        return {"total": 0, "success": 0, "failed": 0}
    
    print(f"📁 Found {len(json_files)} JSON files in {directory}")
    
    results = {"total": len(json_files), "success": 0, "failed": 0}
    
    for json_file in json_files:
        if clean_json_file(str(json_file)):
            results["success"] += 1
            print(f"   ✅ Cleaned {json_file.name}")
        else:
            results["failed"] += 1
    
    print(f"\n✨ Cleaned {results['success']}/{results['total']} files")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean markdown artifacts from JSON")
    parser.add_argument("--directory", "-d", required=True, help="Directory with JSON files")
    
    args = parser.parse_args()
    clean_json_directory(args.directory)
