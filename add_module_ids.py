"""
Add module_id field to all modules in curriculum files
Converts module titles to snake_case module_ids for proper linking
"""

import json
import re
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent / "frontend"

def title_to_id(title):
    """Convert module title to snake_case id"""
    # Remove special characters and convert to lowercase
    id_str = title.lower()
    # Replace spaces and special chars with underscores
    id_str = re.sub(r'[^\w\s-]', '', id_str)
    id_str = re.sub(r'[-\s]+', '_', id_str)
    return id_str

def add_module_ids(subject):
    """Add module_id to all modules in a curriculum"""
    filepath = FRONTEND_DIR / f"{subject}_curriculum.json"
    
    print(f"\nProcessing {subject}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for level in ["beginner", "intermediate", "advanced"]:
        modules = data["levels"][level]["modules"]
        
        for module in modules:
            # Get title from module_header or module_name
            title = module.get("module_header", {}).get("module_title") or module.get("module_name", "")
            
            # Generate module_id if not present
            if "module_id" not in module:
                module_id = title_to_id(title)
                module["module_id"] = module_id
                print(f"  Added: {title} -> {module_id}")
            else:
                print(f"  Exists: {module['module_id']}")
    
    # Save back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✓ Updated {subject}_curriculum.json")

def main():
    print("="*60)
    print("Adding module_id fields to curriculum files")
    print("="*60)
    
    subjects = ["mathematics", "programming_c", "aiml"]
    
    for subject in subjects:
        add_module_ids(subject)
    
    print("\n" + "="*60)
    print("✓ All curricula updated with module_id fields")
    print("="*60)

if __name__ == "__main__":
    main()
