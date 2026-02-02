"""
Content Replacement Script
This script replaces all old module content in curriculum JSON files with finalized module content.
"""

import json
import os
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent
MODULES_DIR = BASE_DIR / "modules"
FRONTEND_DIR = BASE_DIR / "frontend"

# Subject configuration with module lists
SUBJECTS = {
    "mathematics": {
        "beginner": [
            "linear_equations", "quadratic_equations", "polynomials",
            "matrices", "determinants", "system_of_linear_equations"
        ],
        "intermediate": [
            "limits", "continuity", "differentiation",
            "applications_of_derivatives", "integration", "applications_of_integration"
        ],
        "advanced": [
            "probability_basics", "random_variables", "probability_distributions",
            "mean_variance_standard_deviation", "correlation_and_regression"
        ]
    },
    "programming_c": {
        "beginner": [
            "introduction_to_c", "structure_of_c_program", "variables_and_data_types",
            "constants_in_c", "operators_in_c", "control_statements", "loops_in_c"
        ],
        "intermediate": [
            "functions_in_c", "arrays_in_c", "strings_in_c",
            "pointers_basics", "structures", "unions", "file_handling_in_c"
        ],
        "advanced": [
            "dynamic_memory_allocation", "advanced_pointers", "preprocessor_directives",
            "multi_file_programs", "bit_manipulation", "error_handling_in_c"
        ]
    },
    "aiml": {
        "beginner": [
            "introduction_to_artificial_intelligence", "intelligent_agents",
            "problem_solving_in_ai", "introduction_to_machine_learning",
            "types_of_machine_learning"
        ],
        "intermediate": [
            "supervised_learning", "unsupervised_learning",
            "linear_regression_conceptual", "classification_concepts",
            "clustering_concepts"
        ],
        "advanced": [
            "model_evaluation_metrics", "overfitting_and_underfitting",
            "bias_and_variance", "applications_of_ai",
            "limitations_and_ethical_issues_in_ai"
        ]
    }
}

def convert_module_to_curriculum_format(module_data):
    """Convert individual module JSON format to curriculum module format."""
    
    # Extract header information
    header = module_data.get("module_header", {})
    
    # Build curriculum module structure
    curriculum_module = {
        "module_id": "",  # Will be set from filename
        "module_name": header.get("module_title", ""),
        "level": header.get("level", "").lower(),
        "subject": header.get("subject", "").lower(),
        "learning_objectives": header.get("learning_outcomes", []),
        "content_cards": {
            "motivation": {
                "title": "Real World Application",
                "content": module_data.get("applications", [""])[0] if module_data.get("applications") else ""
            },
            "concept_overview": {
                "title": "Conceptual Framework",
                "points": module_data.get("concept_overview", [])[:3]
            },
            "intuition": {
                "title": "Deep Dive & Analysis",
                "content": " ".join(module_data.get("theory", [])[:2]) if isinstance(module_data.get("theory"), list) else module_data.get("theory", "")
            },
            "math_derivation": {
                "title": "Technical Formulation",
                "content": module_data.get("mathematical_formulation", [{}])[0].get("formula", "") if module_data.get("mathematical_formulation") else ""
            },
            "worked_example": {
                "title": "Applied Scenario",
                "problem": "",
                "solution": ""
            },
            "key_takeaways": {
                "title": "Exam Notes",
                "points": module_data.get("key_takeaways", [])[:3]
            }
        },
        "core_content": {
            "theory": " ".join(module_data.get("theory", [])) if isinstance(module_data.get("theory"), list) else module_data.get("theory", ""),
            "intuition": "See Rich Content Card."
        }
    }
    
    # Add worked example if available
    if module_data.get("worked_examples"):
        first_example = module_data["worked_examples"][0]
        curriculum_module["content_cards"]["worked_example"]["problem"] = first_example.get("problem", "")
        solution_steps = first_example.get("solution_steps", [])
        curriculum_module["content_cards"]["worked_example"]["solution"] = "\\n\\n".join(solution_steps)
    
    return curriculum_module

def load_module_file(subject, level, module_id):
    """Load a module JSON file."""
    module_path = MODULES_DIR / subject / level / f"{module_id}.json"
    
    if not module_path.exists():
        print(f"❌ Module file not found: {module_path}")
        return None
    
    try:
        with open(module_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {module_path}: {e}")
        return None

def build_curriculum(subject):
    """Build complete curriculum for a subject from individual modules."""
    print(f"\n{'='*60}")
    print(f"Building curriculum for: {subject.upper()}")
    print(f"{'='*60}")
    
    curriculum = {
        "subject": subject,
        "levels": {}
    }
    
    for level, module_ids in SUBJECTS[subject].items():
        print(f"\n📁 Processing {level.upper()} level ({len(module_ids)} modules)...")
        curriculum["levels"][level] = {"modules": []}
        
        for module_id in module_ids:
            print(f"  📄 Loading: {module_id}.json... ", end="")
            
            # Load the finalized module data
            module_data = load_module_file(subject, level, module_id)
            
            if module_data:
                # Simply use the module data as-is since it's already in the correct format
                # Just add the module_id
                module_data["module_id"] = module_id
                curriculum["levels"][level]["modules"].append(module_data)
                print("✅ Done")
            else:
                print("❌ Failed")
    
    return curriculum

def save_curriculum(subject, curriculum):
    """Save the curriculum to frontend directory."""
    output_path = FRONTEND_DIR / f"{subject}_curriculum.json"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(curriculum, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Successfully saved: {output_path}")
        return True
    except Exception as e:
        print(f"\n❌ Error saving {output_path}: {e}")
        return False

def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("CONTENT REPLACEMENT SCRIPT")
    print("Replacing old module content with finalized content")
    print("="*60)
    
    results = {}
    
    for subject in SUBJECTS.keys():
        # Build curriculum from finalized modules
        curriculum = build_curriculum(subject)
        
        # Save to frontend
        success = save_curriculum(subject, curriculum)
        results[subject] = success
    
    # Print summary
    print("\n" + "="*60)
    print("REPLACEMENT SUMMARY")
    print("="*60)
    
    for subject, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{subject.upper()}: {status}")
    
    total_modules = sum(len(modules) for subject_data in SUBJECTS.values() for modules in subject_data.values())
    print(f"\nTotal modules processed: {total_modules}")
    print("\n✅ Content replacement complete!")

if __name__ == "__main__":
    main()
