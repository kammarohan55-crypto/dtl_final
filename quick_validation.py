"""
Quick Validation Check
"""
import json
from pathlib import Path

BASE = Path(__file__).parent / "frontend"

def quick_check():
    subjects = {
        "mathematics": {"b": 6, "i": 6, "a": 5},
        "programming_c": {"b": 7, "i": 7, "a": 6},
        "aiml": {"b": 5, "i": 5, "a": 5}
    }
    
    print("QUICK VALIDATION CHECK")
    print("=" * 60)
    
    all_good = True
    total_modules = 0
    total_formulas = 0
    total_quiz_q = 0
    
    for subj, expected in subjects.items():
        print(f"\n{subj.upper()}:")
        
        # Load curriculum
        curr = json.load(open(BASE / f"{subj}_curriculum.json", encoding="utf-8"))
        
        # Check module counts
        for level, count in [("beginner", expected["b"]), ("intermediate", expected["i"]), ("advanced", expected["a"])]:
            modules = curr["levels"][level]["modules"]
            actual = len(modules)
            total_modules += actual
            
            status = "✅" if actual == count else "❌"
            print(f"  {level}: {actual}/{count} modules {status}")
            
            if actual != count:
                all_good = False
            
            # Check first module has all components
            if modules:
                m = modules[0]
                has_theory = bool(m.get("theory"))
                has_formula = bool(m.get("mathematical_formulation"))
                has_quiz = bool(m.get("quiz"))
                has_ai = bool(m.get("ai_summary"))
                
                # Count formulas and quizTotal_formulas += len(m.get("mathematical_formulation", []))
                total_quiz_q += len(m.get("quiz", []))
                
                if all([has_theory, has_formula, has_quiz, has_ai]):
                    print(f"    Sample module: ✅ (theory, formulas, quiz, AI summary)")
                else:
                    print(f"    Sample module: ❌ Missing components")
                    all_good = False
    
    # Roadmap check
    print(f"\nROADMAPS:")
    for subj in subjects:
        road = json.load(open(BASE / "roadmaps" / f"{subj}_roadmap.json", encoding="utf-8"))
        curr = json.load(open(BASE / f"{subj}_curriculum.json", encoding="utf-8"))
        
        match = True
        for level in ["beginner", "intermediate", "advanced"]:
            curr_names = [m.get("module_header", {}).get("module_title") or m.get("module_name") 
                         for m in curr["levels"][level]["modules"]]
            road_names = road["levels"][level]["modules"]
            
            if set(curr_names) != set(road_names):
                match = False
                break
        
        status = "✅" if match else "❌"
        print(f"  {subj}: {status}")
        if not match:
            all_good = False
    
    print(f"\n{'=' * 60}")
    print(f"Total Modules: {total_modules}/52")
    print(f"Total Math Formulas: {total_formulas}+")
    print(f"Total Quiz Questions: {total_quiz_q}+")
    
    print(f"\n{'=' * 60}")
    if all_good:
        print("✅ VALIDATION PASSED - READY FOR SUBMISSION")
    else:
        print("❌ VALIDATION FAILED - REVIEW NEEDED")
    print(f"{'=' * 60}\n")
    
    return all_good

if __name__ == "__main__":
    success = quick_check()
    exit(0 if success else 1)
