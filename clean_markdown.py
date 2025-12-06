import json
import re
from pathlib import Path
from typing import Any, Dict, List, Union

# Default directory for transformed JSON files
TRANSFORMED_DIR = "transformed"


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
        # Recursively process all items
        return [clean_node(item) for item in node]
    
    else:
        # Return primitive values as-is
        return node


def clean_json_file(file_path: Path) -> bool:
    """
    Clean markdown artifacts from a single JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        # Load JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clean all text nodes
        cleaned_data = clean_node(data)
        
        # Save back to same file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error processing {file_path.name}: {e}")
        return False


def clean_directory(directory: str = TRANSFORMED_DIR) -> int:
    """
    Clean all JSON files in a directory.
    Returns count of successfully cleaned files.
    """
    dir_path = Path(directory)
    json_files = sorted(dir_path.glob("*.json"))
    
    if not json_files:
        print(f"❌ No JSON files found in {directory}")
        return 0
    
    print(f"📁 Found {len(json_files)} JSON files in {directory}")
    
    cleaned_count = 0
    for json_file in json_files:
        if clean_json_file(json_file):
            print(f"   ✅ Cleaned {json_file.name}")
            cleaned_count += 1
    
    print(f"\n✨ Done! Cleaned {cleaned_count}/{len(json_files)} files")
    return cleaned_count


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean markdown artifacts from JSON files")
    parser.add_argument("--directory", "-d", default=TRANSFORMED_DIR,
                        help=f"Directory with JSON files (default: {TRANSFORMED_DIR})")
    
    args = parser.parse_args()
    clean_directory(args.directory)

