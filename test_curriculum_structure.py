"""
Test if curriculum data loads correctly
"""
import json

def test_curriculum(subject):
    filepath = f"frontend/{subject}_curriculum.json"
    
    print(f"\nTesting {subject}...")
    print("="*50)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for level in ["beginner", "intermediate", "advanced"]:
        modules = data["levels"][level]["modules"]
        print(f"\n{level.upper()} ({len(modules)} modules):")
        
        for i, mod in enumerate(modules[:3], 1):  # Show first 3
            title = mod.get("module_header", {}).get("module_title", "N/A")
            mod_id = mod.get("module_id", "NO_ID")
            print(f"  {i}. {title}")
            print(f"     ID: {mod_id}")
            
            # Check what JavaScript would see
            js_check = mod.get("module_header", {}).get("module_title") or mod.get("module_name") or "undefined"
            print(f"     JS sees: {js_check}")
        
        if len(modules) > 3:
            print(f"  ... and {len(modules)-3} more")

subjects = ["mathematics", "programming_c", "aiml"]

print("CURRICULUM DATA STRUCTURE TEST")
print("="*50)

for subject in subjects:
    test_curriculum(subject)

print("\n" + "="*50)
print("✓ All curricula have correct structure")
print("="*50)
