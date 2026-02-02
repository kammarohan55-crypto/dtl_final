"""
Roadmap Validation Script
Verifies that roadmap module names match curriculum module names exactly
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
ROADMAPS_DIR = FRONTEND_DIR / "roadmaps"

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_roadmap(subject):
    """Validate roadmap matches curriculum"""
    print(f"\n{'='*60}")
    print(f"VALIDATING: {subject.upper()}")
    print(f"{'='*60}")
    
    # Load files
    curriculum = load_json(FRONTEND_DIR / f"{subject}_curriculum.json")
    roadmap = load_json(ROADMAPS_DIR / f"{subject}_roadmap.json")
    
    issues = []
    total_modules = 0
    
    for level in ["beginner", "intermediate", "advanced"]:
        print(f"\n📁 {level.upper()} Level:")
        
        # Get roadmap module names
        roadmap_modules = roadmap["levels"][level]["modules"]
        print(f"   Roadmap modules: {len(roadmap_modules)}")
        
        # Get curriculum module names
        curriculum_modules = [m.get("module_name") or m.get("module_header", {}).get("module_title") 
                             for m in curriculum["levels"][level]["modules"]]
        print(f"   Curriculum modules: {len(curriculum_modules)}")
        
        total_modules += len(roadmap_modules)
        
        # Check each roadmap module exists in curriculum
        for rm in roadmap_modules:
            if rm in curriculum_modules:
                print(f"   ✅ {rm}")
            else:
                print(f"   ❌ MISSING: {rm}")
                issues.append(f"{level}: Roadmap module '{rm}' not found in curriculum")
        
        # Check for extra modules in curriculum not in roadmap
        for cm in curriculum_modules:
            if cm not in roadmap_modules:
                print(f"   ⚠️  EXTRA in curriculum: {cm}")
                issues.append(f"{level}: Curriculum module '{cm}' not in roadmap")
    
    print(f"\n📊 Summary:")
    print(f"   Total roadmap modules: {total_modules}")
    
    if issues:
        print(f"\n❌ ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"\n✅ All roadmap modules match curriculum!")
        return True

def main():
    """Main validation"""
    print("\n" + "="*60)
    print("ROADMAP-CURRICULUM VALIDATION")
    print("="*60)
    
    subjects = ["mathematics", "programming_c", "aiml"]
    results = {}
    
    for subject in subjects:
        try:
            results[subject] = validate_roadmap(subject)
        except Exception as e:
            print(f"\n❌ Error validating {subject}: {e}")
            results[subject] = False
    
    # Final summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for subject, valid in results.items():
        status = "✅ VALID" if valid else "❌ INVALID"
        print(f"{subject.upper()}: {status}")
    
    all_valid = all(results.values())
    print("\n" + "="*60)
    if all_valid:
        print("✅ ALL ROADMAPS VALIDATED SUCCESSFULLY!")
    else:
        print("❌ SOME ROADMAPS HAVE ISSUES - SEE DETAILS ABOVE")
    print("="*60 + "\n")
    
    return all_valid

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
