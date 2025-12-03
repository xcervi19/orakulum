import os
import json
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

# Single file mode (legacy)
INPUT_PATH = "manual_input/html_in.txt"
OUTPUT_PATH = "transformed/output.json"

# Folder mode
INPUT_DIR = "stage_3_generated_html"
OUTPUT_DIR = "transformed"


def node_to_dict(node):
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

    ui = node.attrs.pop("data-ui", None)
    if ui is not None:
        data["ui"] = ui

    if node.attrs:
        data["attrs"] = node.attrs

    children = []
    for child in node.children:
        child_dict = node_to_dict(child)
        if child_dict is not None:
            children.append(child_dict)
    if children:
        data["children"] = children

    return data


def transform_html_to_json(input_path: str, output_path: str) -> list:
    """Transform a single HTML file to JSON."""
    with open(input_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    root = soup.body if soup.body is not None else soup

    result = []
    for child in root.children:
        d = node_to_dict(child)
        if d is not None:
            result.append(d)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


def transform_folder(input_dir: str = INPUT_DIR, output_dir: str = OUTPUT_DIR) -> list[str]:
    """
    Transform all HTML files from input_dir to JSON files in output_dir.
    Returns list of created output files.
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Find all .txt files (HTML content)
    html_files = sorted(input_path.glob("*.txt"))
    
    if not html_files:
        print(f"❌ No .txt files found in {input_dir}")
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Found {len(html_files)} files in {input_dir}")
    
    created_files = []
    for html_file in html_files:
        # Change extension from .txt to .json
        output_file = output_path / (html_file.stem + ".json")
        
        try:
            transform_html_to_json(str(html_file), str(output_file))
            print(f"   ✅ {html_file.name} → {output_file.name}")
            created_files.append(str(output_file))
        except Exception as e:
            print(f"   ❌ {html_file.name} failed: {e}")
    
    print(f"\n✨ Done! {len(created_files)} JSON files created in {output_dir}/")
    return created_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transform HTML to JSON")
    parser.add_argument("--single", "-s", action="store_true", 
                        help="Single file mode (manual_input/html_in.txt)")
    parser.add_argument("--input", "-i", help="Input file or directory")
    parser.add_argument("--output", "-o", help="Output file or directory")
    
    args = parser.parse_args()
    
    if args.single:
        # Single file mode (legacy)
        input_file = args.input or INPUT_PATH
        output_file = args.output or OUTPUT_PATH
        transform_html_to_json(input_file, output_file)
        print(f"✅ Transformed {input_file} → {output_file}")
    else:
        # Folder mode (default)
        input_dir = args.input or INPUT_DIR
        output_dir = args.output or OUTPUT_DIR
        transform_folder(input_dir, output_dir)

