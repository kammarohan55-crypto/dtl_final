import json
import os

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, "modules")

# Define structure
SUBJECTS = {
    "mathematics": "mathematics_curriculum.json",
    "aiml": "aiml_curriculum.json",
    "programming_c": "programming_c_curriculum.json"
}

LEVELS = ["beginner", "intermediate", "advanced"]

def compile_curriculum():
    print("Starting curriculum compilation...")
    
    total_modules = 0
    
    for subject, output_file in SUBJECTS.items():
        print(f"Processing {subject}...")
        
        # Initialize curriculum structure
        curriculum = {
            "subject": subject,
            "levels": {
                "beginner": {"modules": []},
                "intermediate": {"modules": []},
                "advanced": {"modules": []}
            }
        }
        
        subject_dir = os.path.join(MODULES_DIR, subject)
        if not os.path.exists(subject_dir):
            print(f"Warning: Directory {subject_dir} does not exist. Skipping.")
            continue
            
        for level in LEVELS:
            level_dir = os.path.join(subject_dir, level)
            if not os.path.exists(level_dir):
                continue
                
            # Read all JSON files in the level directory
            files = [f for f in os.listdir(level_dir) if f.endswith('.json')]
            print(f"  - {level}: found {len(files)} modules")
            
            for file in files:
                file_path = os.path.join(level_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        module_data = json.load(f)
                        
                        # Inject module_id if missing (derive from filename)
                        if 'module_id' not in module_data:
                            module_id = os.path.splitext(file)[0]
                            module_data['module_id'] = module_id
                            
                        curriculum["levels"][level]["modules"].append(module_data)
                        total_modules += 1
                except Exception as e:
                    print(f"    Error reading {file}: {e}")
                    
        # Write the aggregate curriculum file
        output_path = os.path.join(BASE_DIR, 'frontend', output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(curriculum, f, indent=4, ensure_ascii=False)
        print(f"  -> Saved to {output_file}")

    print("=" * 50)
    print(f"COMPILATION COMPLETE")
    print(f"Total modules processed: {total_modules}")
    print("=" * 50)

if __name__ == "__main__":
    compile_curriculum()
