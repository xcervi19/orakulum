"""
HTML Wrapper

Wraps expanded content with the HTML transform template.
"""

import os
from pathlib import Path
from typing import List


DEFAULT_TEMPLATE_PATH = "prompts/html_transform.txt"
PLACEHOLDER = "[PASTETEXTHERE]"


def load_template(template_path: str = DEFAULT_TEMPLATE_PATH) -> str:
    """Load the HTML transform template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def wrap_with_html_template(content: str, template: str = None) -> str:
    """
    Wrap content with HTML transform template.
    
    Args:
        content: The expanded content to wrap
        template: Optional template string (loads default if not provided)
        
    Returns:
        Content wrapped in HTML template
    """
    if template is None:
        template = load_template()
    
    return template.replace(PLACEHOLDER, content)


def wrap_directory(
    input_dir: str,
    output_dir: str,
    template_path: str = DEFAULT_TEMPLATE_PATH,
    pattern: str = "*.txt"
) -> int:
    """
    Wrap all text files in a directory with HTML template.
    
    Args:
        input_dir: Directory with text files to wrap
        output_dir: Output directory for wrapped files
        template_path: Path to HTML transform template
        pattern: Glob pattern for input files
        
    Returns:
        Number of files processed
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return 0
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return 0
    
    template = load_template(template_path)
    output_path.mkdir(parents=True, exist_ok=True)
    
    txt_files = sorted(input_path.glob(pattern))
    
    if not txt_files:
        print(f"❌ No {pattern} files found in {input_dir}")
        return 0
    
    print(f"📁 Found {len(txt_files)} files in {input_dir}")
    
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        wrapped = wrap_with_html_template(content, template)
        
        output_file = output_path / txt_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(wrapped)
        
        print(f"   ✅ {txt_file.name} → {output_file.name}")
    
    print(f"\n✨ Wrapped {len(txt_files)} files")
    return len(txt_files)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Wrap content with HTML transform template")
    parser.add_argument("--input", "-i", required=True, help="Input directory")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--template", "-t", default=DEFAULT_TEMPLATE_PATH, help="Template file")
    
    args = parser.parse_args()
    
    wrap_directory(args.input, args.output, args.template)
