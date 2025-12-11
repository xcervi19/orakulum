import os
from pathlib import Path

# Default paths
DEFAULT_INPUT_DIR = "stage_2_generated_parts"
DEFAULT_OUTPUT_DIR = "stage_2_prepared_html"
DEFAULT_TEMPLATE_PATH = "prompts/html_transform.txt"
PLACEHOLDER = "[PASTETEXTHERE]"


def load_template(template_path: str) -> str:
    """Load the HTML transform prompt template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def prepare_prompt(template: str, content: str) -> str:
    """Replace placeholder in template with actual content."""
    return template.replace(PLACEHOLDER, content)


def process_all_parts(input_dir: str = None, output_dir: str = None, 
                      template_path: str = None) -> int:
    """
    Process all files from input directory,
    fill the template, and save to output directory.
    
    Args:
        input_dir: Directory with text files to process
        output_dir: Directory to save prepared prompts
        template_path: Path to HTML transform template
        
    Returns:
        Number of files processed
    """
    input_dir = input_dir or DEFAULT_INPUT_DIR
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    template_path = template_path or DEFAULT_TEMPLATE_PATH
    
    # Load template
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return 0
        
    template = load_template(template_path)
    print(f"📄 Loaded template from {template_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all .txt files from input directory
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return 0
        
    txt_files = sorted(input_path.glob("*.txt"))
    
    if not txt_files:
        print(f"❌ No .txt files found in {input_dir}")
        return 0
    
    print(f"📁 Found {len(txt_files)} files in {input_dir}")
    
    # Process each file
    for txt_file in txt_files:
        # Read content
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fill template
        filled_prompt = prepare_prompt(template, content)
        
        # Save to output directory with same filename
        output_file = Path(output_dir) / txt_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(filled_prompt)
        
        print(f"   ✅ {txt_file.name} → {output_file}")
    
    print(f"\n✨ Done! {len(txt_files)} prompts ready in {output_dir}/")
    return len(txt_files)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Prepare HTML transform prompts")
    parser.add_argument("--input", "-i", default=DEFAULT_INPUT_DIR,
                        help=f"Input directory with text files (default: {DEFAULT_INPUT_DIR})")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory for prompts (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--template", "-t", default=DEFAULT_TEMPLATE_PATH,
                        help=f"Template file path (default: {DEFAULT_TEMPLATE_PATH})")
    
    args = parser.parse_args()
    
    count = process_all_parts(
        input_dir=args.input,
        output_dir=args.output,
        template_path=args.template
    )
    
    exit(0 if count > 0 else 1)

