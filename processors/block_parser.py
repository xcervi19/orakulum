"""
Block Parser

Parses the career plan into individual blocks and generates expand prompts.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def parse_plan_blocks(plan_text: str) -> List[Tuple[int, str]]:
    """
    Parse plan text and extract blocks between <blok-n> and <end-blok-n> tags.
    
    Args:
        plan_text: The full plan text with block tags
        
    Returns:
        List of tuples (block_number, block_content)
    """
    pattern = re.compile(r'<blok-(\d+)>(.*?)<end-blok-\1>', re.DOTALL)
    matches = pattern.findall(plan_text)
    return [(int(n), block.strip()) for n, block in matches]


def load_expand_template(template_path: str = "prompts/expand.txt") -> str:
    """Load the expand template from file."""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def fill_expand_template(
    template: str,
    block_content: str,
    obor: Optional[str] = None,
    seniorita: Optional[str] = None,
    hlavni_cil: Optional[str] = None
) -> str:
    """
    Fill the expand template with block content and client parameters.
    
    Args:
        template: The expand template text
        block_content: The block content to insert
        obor: Client's field/domain
        seniorita: Client's seniority level
        hlavni_cil: Client's main goal
        
    Returns:
        Filled template ready for LLM
    """
    result = template.replace('[INSERT BLOCK]', block_content.strip())
    
    # Replace client parameters
    result = result.replace('[obor]', obor or 'nezadáno')
    result = result.replace('[úroveň]', seniorita or 'nezadáno')
    result = result.replace('[např. uspět u pohovoru]', hlavni_cil or 'nezadáno')
    
    return result


def generate_expand_prompts(
    plan_path: str,
    output_dir: str,
    template_path: str = "prompts/expand.txt",
    obor: Optional[str] = None,
    seniorita: Optional[str] = None,
    hlavni_cil: Optional[str] = None
) -> List[str]:
    """
    Generate expand prompts from a plan file.
    
    Args:
        plan_path: Path to the plan text file
        output_dir: Directory to save generated prompts
        template_path: Path to expand template
        obor: Client's field/domain
        seniorita: Client's seniority level
        hlavni_cil: Client's main goal
        
    Returns:
        List of generated prompt file paths
    """
    # Read plan
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_text = f.read()
    
    # Parse blocks
    blocks = parse_plan_blocks(plan_text)
    
    if not blocks:
        print("❌ No blocks found in plan")
        return []
    
    # Load template
    template = load_expand_template(template_path)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate prompts
    generated_files = []
    
    for block_number, block_content in blocks:
        filled = fill_expand_template(
            template=template,
            block_content=block_content,
            obor=obor,
            seniorita=seniorita,
            hlavni_cil=hlavni_cil
        )
        
        output_path = os.path.join(output_dir, f"prompt_block_{block_number}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(filled)
        
        generated_files.append(output_path)
        print(f"   ✅ Block {block_number}: {output_path}")
    
    print(f"\n✨ Generated {len(generated_files)} expand prompts")
    return generated_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse plan blocks and generate expand prompts")
    parser.add_argument("--input", "-i", required=True, help="Input plan file")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    parser.add_argument("--template", "-t", default="prompts/expand.txt", help="Expand template")
    parser.add_argument("--obor", help="Client's field/domain")
    parser.add_argument("--seniorita", help="Client's seniority level")
    parser.add_argument("--cil", help="Client's main goal")
    
    args = parser.parse_args()
    
    generate_expand_prompts(
        plan_path=args.input,
        output_dir=args.output,
        template_path=args.template,
        obor=args.obor,
        seniorita=args.seniorita,
        hlavni_cil=args.cil
    )
