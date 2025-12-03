import os
from pathlib import Path

# Paths
INPUT_DIR = "stage_2_generated_parts"
OUTPUT_DIR = "stage_2_prepared_html"
TEMPLATE_PATH = "prompts/html_transform.txt"
PLACEHOLDER = "[PASTETEXTHERE]"


def load_template(template_path: str) -> str:
    """Load the HTML transform prompt template."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def prepare_prompt(template: str, content: str) -> str:
    """Replace placeholder in template with actual content."""
    return template.replace(PLACEHOLDER, content)


def process_all_parts():
    """
    Process all files from stage_2_generated_parts,
    fill the template, and save to stage_2_prepared_html.
    """
    # Load template
    template = load_template(TEMPLATE_PATH)
    print(f"📄 Loaded template from {TEMPLATE_PATH}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get all .txt files from input directory
    input_path = Path(INPUT_DIR)
    txt_files = sorted(input_path.glob("*.txt"))
    
    if not txt_files:
        print(f"❌ No .txt files found in {INPUT_DIR}")
        return
    
    print(f"📁 Found {len(txt_files)} files in {INPUT_DIR}")
    
    # Process each file
    for txt_file in txt_files:
        # Read content
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fill template
        filled_prompt = prepare_prompt(template, content)
        
        # Save to output directory with same filename
        output_file = Path(OUTPUT_DIR) / txt_file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(filled_prompt)
        
        print(f"   ✅ {txt_file.name} → {output_file}")
    
    print(f"\n✨ Done! {len(txt_files)} prompts ready in {OUTPUT_DIR}/")


if __name__ == "__main__":
    process_all_parts()

