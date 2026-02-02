import os
import json

def extract_questions(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.json'):
                full_path = os.path.join(dirpath, filename)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    module_title = data.get('module_header', {}).get('module_title', filename)
                    quizzes = data.get('quiz', [])
                    
                    if quizzes:
                        print(f"--- Module: {module_title} ---")
                        for i, q in enumerate(quizzes, 1):
                            question = q.get('question', 'No question text')
                            options = q.get('options', [])
                            correct_idx = q.get('correct_answer', -1)
                            
                            print(f"Q{i}: {question}")
                            for idx, opt in enumerate(options):
                                marker = "[x]" if idx == correct_idx else "[ ]"
                                print(f"  {marker} {opt}")
                            print("")
                except Exception as e:
                    print(f"Error reading {full_path}: {e}")

if __name__ == "__main__":
    import sys
    # Redirect stdout to a file with utf-8 encoding
    with open(r"c:\Users\Rohan\Desktop\dtl\all_quizzes_utf8.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        extract_questions(r"c:\Users\Rohan\Desktop\dtl\modules")

