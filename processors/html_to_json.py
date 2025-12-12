"""
HTML to JSON Converter

Transforms HTML with data-ui attributes into structured JSON.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from bs4 import BeautifulSoup, NavigableString


def node_to_dict(node) -> Optional[Dict[str, Any]]:
    """
    Convert a BeautifulSoup node to a dictionary.
    
    Args:
        node: BeautifulSoup node
        
    Returns:
        Dictionary representation or None if empty
    """
    if isinstance(node, NavigableString):
        text = str(node)
        if not text.strip():
            return None
        return {"type": "text", "text": text}

    if not hasattr(node, "name"):
        return None

    data = {
        "type": "element",
        "tag": node.name,
    }

    # Extract data-ui attribute
    ui = node.attrs.pop("data-ui", None)
    if ui is not None:
        data["ui"] = ui

    # Keep remaining attributes
    if node.attrs:
        data["attrs"] = node.attrs

    # Process children recursively
    children = []
    for child in node.children:
        child_dict = node_to_dict(child)
        if child_dict is not None:
            children.append(child_dict)
    
    if children:
        data["children"] = children

    return data


def transform_html_to_json(html_content: str) -> List[Dict[str, Any]]:
    """
    Transform HTML content to structured JSON.
    
    Args:
        html_content: HTML string with data-ui attributes
        
    Returns:
        List of element dictionaries
    """
    soup = BeautifulSoup(html_content, "html.parser")
    root = soup.body if soup.body is not None else soup

    result = []
    for child in root.children:
        d = node_to_dict(child)
        if d is not None:
            result.append(d)

    return result


def transform_file(input_path: str, output_path: str) -> bool:
    """
    Transform a single HTML file to JSON.
    
    Args:
        input_path: Path to HTML file
        output_path: Path to save JSON output
        
    Returns:
        True if successful
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            html = f.read()

        result = transform_html_to_json(html)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"   ❌ Error transforming {input_path}: {e}")
        return False


def transform_html_directory(
    input_dir: str,
    output_dir: str,
    pattern: str = "*.txt"
) -> Dict[str, Any]:
    """
    Transform all HTML files in a directory to JSON.
    
    Args:
        input_dir: Directory with HTML files
        output_dir: Directory to save JSON files
        pattern: Glob pattern for input files
        
    Returns:
        Summary dict with counts
    """
    import re
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return {"total": 0, "success": 0, "failed": 0}
    
    html_files = sorted(input_path.glob(pattern))
    
    if not html_files:
        print(f"❌ No {pattern} files found in {input_dir}")
        return {"total": 0, "success": 0, "failed": 0}
    
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Found {len(html_files)} files in {input_dir}")
    
    results = {"total": len(html_files), "success": 0, "failed": 0}
    
    for html_file in html_files:
        # Extract number from filename for output naming
        match = re.search(r'(\d+)', html_file.name)
        if match:
            output_file = output_path / f"page_{match.group(1)}.json"
        else:
            output_file = output_path / (html_file.stem + ".json")
        
        if transform_file(str(html_file), str(output_file)):
            results["success"] += 1
            print(f"   ✅ {html_file.name} → {output_file.name}")
        else:
            results["failed"] += 1
    
    print(f"\n✨ Transformed {results['success']}/{results['total']} files")
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transform HTML to JSON")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", required=True, help="Output file or directory")
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        transform_html_directory(args.input, args.output)
    else:
        transform_file(args.input, args.output)
        print(f"✅ Transformed {args.input} → {args.output}")
