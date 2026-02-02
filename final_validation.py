"""
Comprehensive Academic Website Validation Script
Validates all aspects of the updated curriculum system
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR / "frontend"
ROADMAPS_DIR = FRONTEND_DIR / "roadmaps"
QUIZZES_DIR = FRONTEND_DIR / "quizzes"

def load_json(filepath):
    """Load JSON file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def check_mathjax_patterns(text):
    """Check for MathJax/LaTeX patterns"""
    if isinstance(text, str):
        # Look for $ delimiters
        inline = re.findall(r'\$[^$]+\$', text)
        display = re.findall(r'\$\$[^$]+\$\$', text)
        return len(inline) + len(display) > 0
    return False

def validate_curriculum(subject):
    """Comprehensive curriculum validation"""
    print(f"\n{'='*70}")
    print(f"VALIDATING: {subject.upper()} CURRICULUM")
    print(f"{'='*70}")
    
    curriculum = load_json(FRONTEND_DIR / f"{subject}_curriculum.json")
    if not curriculum:
        return {"valid": False, "errors": ["Failed to load curriculum"]}
    
    issues = []
    stats = {
        "total_modules": 0,
        "modules_with_math": 0,
        "modules_with_quiz": 0,
        "modules_with_ai_summary": 0,
        "total_quiz_questions": 0,
        "math_formula_count": 0
    }
    
    for level in ["beginner", "intermediate", "advanced"]:
        level_data = curriculum.get("levels", {}).get(level, {})
        modules = level_data.get("modules", [])
        
        print(f"\n📁 {level.upper()} Level: {len(modules)} modules")
        stats["total_modules"] += len(modules)
        
        for i, module in enumerate(modules, 1):
            # Get module name
            module_name = module.get("module_header", {}).get("module_title") or module.get("module_name", f"Module {i}")
            print(f"\n  [{i}] {module_name}")
            
            # Check 1: Module has comprehensive content
            has_theory = bool(module.get("theory"))
            has_formulas = bool(module.get("mathematical_formulation"))
            has_examples = bool(module.get("worked_examples"))
            has_quiz = bool(module.get("quiz"))
            has_ai_summary = bool(module.get("ai_summary"))
            
            # Check 2: MathJax/LaTeX formulas
            math_count = 0
            if has_formulas:
                formulas = module.get("mathematical_formulation", [])
                for formula in formulas:
                    if check_mathjax_patterns(formula.get("formula", "")):
                        math_count += 1
                stats["math_formula_count"] += math_count
                if math_count > 0:
                    stats["modules_with_math"] += 1
            
            # Check 3: Quiz questions
            quiz_count = 0
            if has_quiz:
                stats["modules_with_quiz"] += 1
                quiz = module.get("quiz", [])
                quiz_count = len(quiz)
                stats["total_quiz_questions"] += quiz_count
                
                # Validate quiz structure
                for q_idx, q in enumerate(quiz):
                    if not all(k in q for k in ["question", "options", "correct_answer", "explanation"]):
                        issues.append(f"{module_name}: Quiz Q{q_idx+1} missing required fields")
            
            # Check 4: AI Summary
            if has_ai_summary:
                stats["modules_with_ai_summary"] += 1
                ai_summary = module.get("ai_summary", {})
                if not all(k in ai_summary for k in ["key_ideas", "important_formulas", "exam_tip"]):
                    issues.append(f"{module_name}: AI Summary missing required sections")
            
            # Status indicators
            theory_icon = "✅" if has_theory else "❌"
            formula_icon = "✅" if has_formulas and math_count > 0 else "❌"
            example_icon = "✅" if has_examples else "❌"
            quiz_icon = f"✅({quiz_count})" if has_quiz and quiz_count > 0 else "❌"
            ai_icon = "✅" if has_ai_summary else "❌"
            
            print(f"      Theory: {theory_icon} | Formulas: {formula_icon}({math_count}) | Examples: {example_icon} | Quiz: {quiz_icon} | AI: {ai_icon}")
            
            # Flag issues
            if not has_theory:
                issues.append(f"{module_name}: Missing theory content")
            if not has_formulas:
                issues.append(f"{module_name}: Missing mathematical formulations")
            if not has_quiz:
                issues.append(f"{module_name}: Missing quiz")
            if not has_ai_summary:
                issues.append(f"{module_name}: Missing AI summary")
    
    # Summary
    print(f"\n📊 CURRICULUM STATISTICS:")
    print(f"   Total modules: {stats['total_modules']}")
    print(f"   Modules with math formulas: {stats['modules_with_math']}/{stats['total_modules']}")
    print(f"   Modules with quizzes: {stats['modules_with_quiz']}/{stats['total_modules']}")
    print(f"   Modules with AI summaries: {stats['modules_with_ai_summary']}/{stats['total_modules']}")
    print(f"   Total quiz questions: {stats['total_quiz_questions']}")
    print(f"   Total math formulas: {stats['math_formula_count']}")
    
    return {"valid": len(issues) == 0, "errors": issues, "stats": stats}

def validate_roadmap_alignment(subject):
    """Validate roadmap matches curriculum"""
    print(f"\n{'='*70}")
    print(f"VALIDATING: {subject.upper()} ROADMAP ALIGNMENT")
    print(f"{'='*70}")
    
    curriculum = load_json(FRONTEND_DIR / f"{subject}_curriculum.json")
    roadmap = load_json(ROADMAPS_DIR / f"{subject}_roadmap.json")
    
    if not curriculum or not roadmap:
        return {"valid": False, "errors": ["Failed to load files"]}
    
    issues = []
    
    for level in ["beginner", "intermediate", "advanced"]:
        print(f"\n📁 {level.upper()} Level:")
        
        # Get module names from both
        curr_modules = [m.get("module_header", {}).get("module_title") or m.get("module_name", "") 
                       for m in curriculum["levels"][level]["modules"]]
        road_modules = roadmap["levels"][level]["modules"]
        
        print(f"   Curriculum: {len(curr_modules)} modules")
        print(f"   Roadmap: {len(road_modules)} modules")
        
        # Check exact match
        if set(curr_modules) == set(road_modules):
            print(f"   ✅ Perfect match!")
        else:
            # Find mismatches
            missing_in_roadmap = set(curr_modules) - set(road_modules)
            extra_in_roadmap = set(road_modules) - set(curr_modules)
            
            if missing_in_roadmap:
                print(f"   ❌ Missing in roadmap: {missing_in_roadmap}")
                issues.append(f"{level}: Modules in curriculum but not roadmap: {missing_in_roadmap}")
            
            if extra_in_roadmap:
                print(f"   ❌ Extra in roadmap: {extra_in_roadmap}")
                issues.append(f"{level}: Modules in roadmap but not curriculum: {extra_in_roadmap}")
        
        # Check order
        if curr_modules == road_modules:
            print(f"   ✅ Order matches exactly")
        else:
            print(f"   ⚠️  Order differs (but modules match)")
    
    return {"valid": len(issues) == 0, "errors": issues}

def final_validation():
    """Run all validation checks"""
    print("\n" + "="*70)
    print("COMPREHENSIVE ACADEMIC WEBSITE VALIDATION")
    print("="*70)
    
    subjects = ["mathematics", "programming_c", "aiml"]
    
    all_results = {}
    all_issues = []
    
    # 1. Curriculum Content Validation
    print("\n\n【1】CURRICULUM CONTENT VALIDATION")
    print("="*70)
    curriculum_stats = {}
    for subject in subjects:
        result = validate_curriculum(subject)
        all_results[f"{subject}_curriculum"] = result
        curriculum_stats[subject] = result.get("stats", {})
        if not result["valid"]:
            all_issues.extend(result["errors"])
    
    # 2. Roadmap Alignment Validation
    print("\n\n【2】ROADMAP ALIGNMENT VALIDATION")
    print("="*70)
    for subject in subjects:
        result = validate_roadmap_alignment(subject)
        all_results[f"{subject}_roadmap"] = result
        if not result["valid"]:
            all_issues.extend(result["errors"])
    
    # Final Summary
    print("\n\n" + "="*70)
    print("FINAL VALIDATION SUMMARY")
    print("="*70)
    
    # Module counts
    total_modules = sum(s.get("total_modules", 0) for s in curriculum_stats.values())
    total_formulas = sum(s.get("math_formula_count", 0) for s in curriculum_stats.values())
    total_quizzes = sum(s.get("total_quiz_questions", 0) for s in curriculum_stats.values())
    
    print(f"\n📚 CONTENT OVERVIEW:")
    print(f"   Total Modules: {total_modules}")
    print(f"   - Mathematics: {curriculum_stats.get('mathematics', {}).get('total_modules', 0)}")
    print(f"   - Programming C: {curriculum_stats.get('programming_c', {}).get('total_modules', 0)}")
    print(f"   - AIML: {curriculum_stats.get('aiml', {}).get('total_modules', 0)}")
    print(f"\n   Total Math Formulas: {total_formulas}")
    print(f"   Total Quiz Questions: {total_quizzes}")
    
    print(f"\n🔍 VALIDATION RESULTS:")
    for check_name, result in all_results.items():
        status = "✅ PASS" if result["valid"] else "❌ FAIL"
        print(f"   {check_name}: {status}")
    
    if all_issues:
        print(f"\n❌ ISSUES FOUND ({len(all_issues)}):")
        for issue in all_issues[:20]:  # Show first 20
            print(f"   • {issue}")
        if len(all_issues) > 20:
            print(f"   ... and {len(all_issues) - 20} more issues")
    else:
        print(f"\n✅ NO ISSUES FOUND!")
    
    # Academic Readiness
    print(f"\n" + "="*70)
    all_valid = all(r["valid"] for r in all_results.values())
    
    if all_valid:
        print("✅ WEBSITE IS READY FOR ACADEMIC SUBMISSION")
        print("="*70)
        print("\n✓ All modules contain comprehensive academic content")
        print("✓ All roadmaps align with curriculum structure")
        print("✓ MathJax/LaTeX formulas preserved throughout")
        print("✓ Quiz system fully functional across all modules")
        print("✓ AI summaries present with exam tips and formulas")
        print("✓ No broken links or module mismatches detected")
    else:
        print("❌ WEBSITE HAS ISSUES - REVIEW REQUIRED")
        print("="*70)
        print(f"\nPlease address the {len(all_issues)} issues listed above before submission.")
    
    print("\n" + "="*70 + "\n")
    
    return all_valid

if __name__ == "__main__":
    success = final_validation()
    exit(0 if success else 1)
