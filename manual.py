import os
import json

def load_client_input(json_path):
    """
    Load client input JSON and extract values with defensive programming.
    Returns a dict with obor, level, and target values.
    If values are empty, returns None to keep placeholders in template.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️  JSON file not found: {json_path}")
        return {
            'obor': None,
            'level': None,
            'target': None
        }
    except json.JSONDecodeError as e:
        print(f"⚠️  Invalid JSON in {json_path}: {e}")
        return {
            'obor': None,
            'level': None,
            'target': None
        }
    
    # Extract values with defensive checks - handle missing keys gracefully
    domain_obj = data.get('domain', {})
    seniority_obj = data.get('seniority', {})
    main_goal_obj = data.get('main_goal', {})
    
    # Get values, strip whitespace, return None if empty
    domain_value = domain_obj.get('value', '').strip() if isinstance(domain_obj, dict) else ''
    seniority_value = seniority_obj.get('value', '').strip() if isinstance(seniority_obj, dict) else ''
    main_goal_value = main_goal_obj.get('value', '').strip() if isinstance(main_goal_obj, dict) else ''
    
    # Return None for empty values (will keep placeholder in template)
    obor = domain_value if domain_value else None
    level = seniority_value if seniority_value else None
    target = main_goal_value if main_goal_value else None
    
    # Warn if values are missing
    if not domain_value:
        print("⚠️  Domain value is empty, keeping placeholder [obor]")
    if not seniority_value:
        print("⚠️  Seniority value is empty, keeping placeholder [úroveň]")
    if not main_goal_value:
        print("⚠️  Main goal value is empty, keeping placeholder [např. uspět u pohovoru]")
    
    return {
        'obor': obor,
        'level': level,
        'target': target
    }

def replace_placeholders(template, values):
    """
    Replace placeholders in template with values from JSON.
    Placeholders: [obor], [úroveň], [např. uspět u pohovoru]
    If value is None, keeps the original placeholder (defensive programming).
    """
    result = template
    
    # Only replace if value is not None (not empty)
    if values['obor'] is not None:
        result = result.replace('[obor]', values['obor'])
    else:
        print("   → Keeping placeholder [obor] (value not provided)")
    
    if values['level'] is not None:
        result = result.replace('[úroveň]', values['level'])
    else:
        result = result.replace('[úroveň]', 'nezadanáo')
        print("   → Keeping placeholder [úroveň] (value not provided)")
    
    if values['target'] is not None:
        result = result.replace('[např. uspět u pohovoru]', values['target'])
    else:
        result = result.replace('[např. uspět u pohovoru]', 'nezadanáo')
        print("   → Keeping placeholder [např. uspět u pohovoru] (value not provided)")
    
    return result

def parse_blocks(input_text):
    """
    Parses input_text and extracts blocks formatted between <blok-n> and <end-blok-n> 
    (including any block number n), returning a list of strings (each block).
    """
    import re
    pattern = re.compile(r'<blok-(\d+)>(.*?)<end-blok-\1>', re.DOTALL)
    matches = pattern.findall(input_text)
    return [(int(n), block.strip()) for n, block in matches]

def read_expand_template(template_path):
    with open(template_path, encoding='utf-8') as f:
        return f.read()

def fill_template(template, block_content):
    """
    Replace [INSERT BLOCK] in the template with the given parsed block_content.
    """
    return template.replace('[INSERT BLOCK]', block_content.strip())

def save_filled_prompt(output_dir, block_number, content):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"prompt_block_{block_number}.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return path

def main(input_path: str = None, json_path: str = None, output_dir: str = None, 
         template_path: str = None):
    """
    Main function with configurable paths for pipeline integration.
    
    Args:
        input_path: Path to plan/tutorial text file with <blok-n> tags
        json_path: Path to client input JSON file
        output_dir: Directory to save generated prompts
        template_path: Path to expand template
    """
    # Default paths
    input_path = input_path or os.path.join("manual_input", "tutorial.txt")
    template_path = template_path or os.path.join("prompts", "expand.txt")
    json_path = json_path or os.path.join("manual_input", "client_input.json")
    output_dir = output_dir or "parsed_parts"

    # STEP 1: Load client input JSON and extract values (BEFORE generation blocks)
    print("📋 Loading client input data from JSON...")
    client_values = load_client_input(json_path)
    
    # Display loaded values
    print("\n📊 Extracted values:")
    print(f"   [obor] → {client_values['obor'] if client_values['obor'] else '[obor] (placeholder kept)'}")
    print(f"   [úroveň] → {client_values['level'] if client_values['level'] else '[úroveň] (placeholder kept)'}")
    print(f"   [např. uspět u pohovoru] → {client_values['target'] if client_values['target'] else '[např. uspět u pohovoru] (placeholder kept)'}")
    
    # STEP 2: Read expand template
    if not os.path.exists(template_path):
        print(f"❌ Soubor šablony pro expand nebyl nalezen: {template_path}")
        return 1
    template = read_expand_template(template_path)
    
    # STEP 3: Replace placeholders in template with values from JSON (BEFORE generation blocks)
    print("\n🔄 Replacing placeholders in expand template...")
    template = replace_placeholders(template, client_values)
    
    # STEP 4: Read input tutorial and parse blocks
    print(f"\n📖 Reading input from {input_path}...")
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        return 1
        
    with open(input_path, encoding='utf-8') as f:
        input_text = f.read()
    
    blocks = parse_blocks(input_text)
    if not blocks:
        print("❌ Nebyly nalezeny žádné bloky ve vstupním textu.")
        return 1
    
    print(f"✅ Nalezeno {len(blocks)} blok(ů)")
    
    # STEP 5: For each parsed block, fill the template and save
    print(f"\n📝 Generating prompts to {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)
    
    for block_number, block_content in blocks:
        filled = fill_template(template, block_content)
        out_path = save_filled_prompt(output_dir, block_number, filled)
        print(f"   ✅ Blok {block_number}: {out_path}")
    
    print(f"\n✨ Hotovo! Vygenerováno {len(blocks)} prompt(ů).")
    return 0
    
    
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse plan blocks and generate prompts")
    parser.add_argument("--input", "-i", 
                        default="manual_input/tutorial.txt",
                        help="Input file with <blok-n> tags (default: manual_input/tutorial.txt)")
    parser.add_argument("--json", "-j",
                        default="manual_input/client_input.json", 
                        help="Client input JSON file (default: manual_input/client_input.json)")
    parser.add_argument("--output", "-o",
                        default="parsed_parts",
                        help="Output directory for prompts (default: parsed_parts)")
    parser.add_argument("--template", "-t",
                        default="prompts/expand.txt",
                        help="Expand template file (default: prompts/expand.txt)")
    
    args = parser.parse_args()
    
    exit_code = main(
        input_path=args.input,
        json_path=args.json,
        output_dir=args.output,
        template_path=args.template
    )
    exit(exit_code or 0)
