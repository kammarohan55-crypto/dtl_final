"""
AI Module Summarization Backend Server
Flask API for generating module summaries from curriculum JSON
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime, timezone
from threading import Lock

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Progress Tracking Constants
PASS_THRESHOLD = 70
PROGRESS_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'user_progress.json')
PROGRESS_LOCK = Lock()  # Thread-safe file access

# Map subjects to curriculum files
CURRICULUM_FILES = {
    'mathematics': 'mathematics_curriculum.json',
    'aiml': 'aiml_curriculum.json',
    'programming_c': 'programming_c_curriculum.json'
}

CURRICULUM_CACHE = {}

# ============================================================================
# PROGRESS TRACKING HELPERS
# ============================================================================

def load_progress():
    """
    Load progress data from user_progress.json with thread safety.
    
    Returns:
        dict: Progress data with 'modules' key, or empty structure if file missing
    """
    try:
        if os.path.exists(PROGRESS_FILE_PATH):
            with open(PROGRESS_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load progress file: {str(e)}")
    
    # Return default structure if file doesn't exist
    return {"modules": {}}


def save_progress(progress_data):
    """
    Save progress data to user_progress.json with atomic write and thread safety.
    
    Args:
        progress_data (dict): Progress data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    with PROGRESS_LOCK:
        try:
            # Write to temporary file first (atomic operation)
            temp_path = PROGRESS_FILE_PATH + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)
            
            # Atomically rename temp file to actual file
            if os.name == 'nt':  # Windows
                if os.path.exists(PROGRESS_FILE_PATH):
                    os.remove(PROGRESS_FILE_PATH)
                os.rename(temp_path, PROGRESS_FILE_PATH)
            else:  # Unix/Linux/Mac
                os.replace(temp_path, PROGRESS_FILE_PATH)
            
            return True
        except Exception as e:
            print(f"Error: Failed to save progress file: {str(e)}")
            # Clean up temp file if it exists
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
            return False


def get_current_timestamp():
    """Return ISO 8601 formatted timestamp in UTC"""
    return datetime.now(timezone.utc).isoformat()


def validate_progress_input(data):
    """
    Validate progress save request data.
    
    Args:
        data (dict): Request data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not data:
        return False, "No data provided"
    
    module_id = data.get('module_id')
    score = data.get('score')
    
    if not module_id or not isinstance(module_id, str):
        return False, "module_id is required and must be a string"
    
    if score is None or not isinstance(score, (int, float)):
        return False, "score is required and must be a number"
    
    if not (0 <= score <= 100):
        return False, "score must be between 0 and 100"
    
    return True, None


# ============================================================================
# EXISTING CURRICULUM FUNCTIONS
# ============================================================================

def load_curriculum(subject='mathematics'):
    """Load curriculum for specified subject"""
    if subject in CURRICULUM_CACHE:
        return CURRICULUM_CACHE[subject]
    
    if subject not in CURRICULUM_FILES:
        return None
    
    curriculum_path = os.path.join(os.path.dirname(__file__), '..', CURRICULUM_FILES[subject])
    try:
        with open(curriculum_path, 'r', encoding='utf-8') as f:
            curriculum = json.load(f)
            CURRICULUM_CACHE[subject] = curriculum
            return curriculum
    except FileNotFoundError:
        print(f"Error: Curriculum file not found: {curriculum_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in curriculum file: {curriculum_path}")
        return None

def format_summary(module_data):
    """
    Format module content according to AI chatbot summarization template
    
    Args:
        module_data: Dictionary containing module information
        
    Returns:
        Dictionary with formatted summary sections
    """
    core = module_data.get('core_content', {})
    exam = module_data.get('exam_orientation', {})
    
    summary = {
        'module_name': module_data.get('module_name', 'Unknown Module'),
        'level': module_data.get('level', 'Unknown'),
        'module_summary': extract_module_summary(core.get('theory', '')),
        'key_concepts': extract_key_concepts(core.get('theory', '')),
        'intuition': core.get('intuition', 'Understanding gained through practice and application.'),
        'worked_examples': core.get('worked_examples', []),
        'common_mistakes': core.get('common_mistakes', []),
        'exam_takeaways': exam.get('tips', []),
        'real_world_applications': core.get('real_world_applications', [])
    }
    
    return summary

def extract_module_summary(theory_text):
    """Extract 2-3 sentence summary from theory text"""
    if not theory_text:
        return "No summary available."
    
    # Take first 200-300 characters as summary
    sentences = theory_text.split('. ')
    summary_sentences = []
    char_count = 0
    
    for sentence in sentences[:3]:
        if char_count + len(sentence) < 300:
            summary_sentences.append(sentence)
            char_count += len(sentence)
        else:
            break
    
    return '. '.join(summary_sentences) + '.' if summary_sentences else theory_text[:300] + '...'

def extract_key_concepts(theory_text):
    """Extract key concepts from theory text"""
    # Simple extraction - look for definitions and key statements
    concepts = []
    
    if 'is a' in theory_text or 'are' in theory_text:
        sentences = theory_text.split('. ')
        for sentence in sentences[:10]:  # First 10 sentences likely contain key concepts
            if any(keyword in sentence.lower() for keyword in ['is a', 'is an', 'are', 'means', 'represents']):
                if len(sentence) < 200:  # Keep it concise
                    concepts.append(sentence.strip())
            if len(concepts) >= 6:  # Limit to 6 key concepts
                break
    
    # Fallback: generic concepts
    if not concepts:
        concepts = [
            "Core concepts covered in this module",
            "Fundamental principles and definitions",
            "Key techniques and methods",
            "Important formulas and relationships"
        ]
    
    return concepts

# ============================================================================
# PROGRESS TRACKING ENDPOINTS
# ============================================================================

@app.route('/api/progress/save', methods=['POST'])
def save_progress_endpoint():
    """
    Save quiz result and update progress tracking.
    
    Request JSON format:
    {
        "module_id": "linear_equations",
        "score": 85,
        "subject": "mathematics",
        "level": "beginner",
        "time_taken": 1200  [optional, in seconds]
    }
    
    Response format:
    {
        "success": true,
        "status": "completed",  [or "in_progress"]
        "module_id": "linear_equations",
        "attempts": 2,
        "best_score": 85,
        "last_score": 85,
        "last_attempted_at": "2026-01-23T10:30:00Z"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_msg = validate_progress_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        module_id = data.get('module_id')
        score = int(data.get('score'))
        subject = data.get('subject', 'unknown')
        level = data.get('level', 'unknown')
        time_taken = data.get('time_taken', None)  # Optional, in seconds
        
        # Load current progress
        progress = load_progress()
        
        # Determine new status
        new_status = "completed" if score >= PASS_THRESHOLD else "in_progress"
        
        # Get or create module record
        if module_id not in progress['modules']:
            # New module
            progress['modules'][module_id] = {
                'subject': subject,
                'level': level,
                'status': new_status,
                'attempts': 1,
                'best_score': score,
                'last_score': score,
                'last_attempted_at': get_current_timestamp(),
                'history': [
                    {
                        'score': score,
                        'attempted_at': get_current_timestamp(),
                        'time_taken': time_taken
                    }
                ]
            }
        else:
            # Existing module - update progress
            module_record = progress['modules'][module_id]
            module_record['attempts'] += 1
            module_record['last_score'] = score
            module_record['last_attempted_at'] = get_current_timestamp()
            
            # Update best score if new score is higher
            if score > module_record['best_score']:
                module_record['best_score'] = score
            
            # Once completed, don't downgrade status
            if new_status == "completed":
                module_record['status'] = "completed"
            elif module_record['status'] != "completed":
                module_record['status'] = new_status
            
            # Add to history
            module_record['history'].append({
                'score': score,
                'attempted_at': get_current_timestamp(),
                'time_taken': time_taken
            })
        
        # Save to file
        if not save_progress(progress):
            return jsonify({
                'success': False,
                'error': 'Failed to save progress'
            }), 500
        
        # Return updated record
        result = progress['modules'][module_id]
        return jsonify({
            'success': True,
            'module_id': module_id,
            'status': result['status'],
            'attempts': result['attempts'],
            'best_score': result['best_score'],
            'last_score': result['last_score'],
            'last_attempted_at': result['last_attempted_at']
        }), 200
    
    except Exception as e:
        print(f"Error in save_progress_endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/progress', methods=['GET'])
def get_all_progress():
    """
    Get all progress data across all modules.
    
    Response format:
    {
        "success": true,
        "total_modules_attempted": 5,
        "completed_count": 3,
        "modules": {
            "module_id": { ... full record ... },
            ...
        }
    }
    """
    try:
        progress = load_progress()
        modules = progress.get('modules', {})
        
        completed_count = sum(
            1 for m in modules.values() 
            if m.get('status') == 'completed'
        )
        
        return jsonify({
            'success': True,
            'total_modules_attempted': len(modules),
            'completed_count': completed_count,
            'modules': modules
        }), 200
    
    except Exception as e:
        print(f"Error in get_all_progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/progress/<module_id>', methods=['GET'])
def get_module_progress(module_id):
    """
    Get progress for a specific module.
    
    Response format:
    {
        "success": true,
        "module_id": "linear_equations",
        "status": "completed",
        "attempts": 2,
        "best_score": 85,
        "last_score": 85,
        "last_attempted_at": "2026-01-23T10:30:00Z",
        "history": [ ... ]
    }
    
    Returns 404 if module has no progress record yet.
    """
    try:
        progress = load_progress()
        modules = progress.get('modules', {})
        
        if module_id not in modules:
            return jsonify({
                'success': False,
                'error': f'No progress record found for module: {module_id}'
            }), 404
        
        result = modules[module_id]
        return jsonify({
            'success': True,
            'module_id': module_id,
            'status': result.get('status'),
            'attempts': result.get('attempts'),
            'best_score': result.get('best_score'),
            'last_score': result.get('last_score'),
            'last_attempted_at': result.get('last_attempted_at'),
            'history': result.get('history', [])
        }), 200
    
    except Exception as e:
        print(f"Error in get_module_progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# ============================================================================
# EXISTING ENDPOINTS
# ============================================================================

@app.route('/api/summarize', methods=['POST'])
def summarize_module():
    """
    API endpoint to generate module summary
    
    Request JSON format:
    {
        "subject": "mathematics",  # or "aiml" or "programming_c"
        "module_id": "linear_equations",
        "level": "beginner"
    }
    
    Response JSON format:
    {
        "success": true,
        "summary": { ... formatted summary ... }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        subject = data.get('subject', 'mathematics')  # Default to mathematics
        module_id = data.get('module_id')
        level = data.get('level')
        
        if not module_id or not level:
            return jsonify({
                'success': False,
                'error': 'module_id and level are required'
            }), 400
        
        # Load curriculum for subject
        curriculum = load_curriculum(subject)
        if not curriculum:
            return jsonify({
                'success': False,
                'error': f'Failed to load curriculum for subject: {subject}'
            }), 500
        
        # Find the requested module
        modules = curriculum.get('levels', {}).get(level, {}).get('modules', [])
        module = None
        
        for m in modules:
            if m.get('module_id') == module_id:
                module = m
                break
        
        if not module:
            return jsonify({
                'success': False,
                'error': f'Module {module_id} not found at {level} level in {subject}'
            }), 404
        
        # Generate summary
        summary = format_summary(module)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'module-summarization-api'
    })

@app.route('/api/subjects', methods=['GET'])
def list_subjects():
    """List all available subjects"""
    subjects = [
        {'id': 'mathematics', 'name': 'Mathematics'},
        {'id': 'aiml', 'name': 'AI & Machine Learning'},
        {'id': 'programming_c', 'name': 'Programming in C'}
    ]
    return jsonify({
        'success': True,
        'subjects': subjects
    })

@app.route('/api/modules', methods=['GET'])
def list_modules():
    """List all available modules for a subject"""
    subject = request.args.get('subject', 'mathematics')
    
    try:
        curriculum = load_curriculum(subject)
        if not curriculum:
            return jsonify({
                'success': False,
                'error': f'Failed to load curriculum for subject: {subject}'
            }), 500
        
        modules_list = []
        for level_name, level_data in curriculum.get('levels', {}).items():
            for module in level_data.get('modules', []):
                modules_list.append({
                    'module_id': module.get('module_id'),
                    'module_name': module.get('module_name'),
                    'level': level_name,
                    'subject': subject
                })
        
        return jsonify({
            'success': True,
            'subject': subject,
            'modules': modules_list,
            'total': len(modules_list)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Module Summarization API Starting...")
    print("=" * 60)
    
    # Verify curriculum files exist
    base_path = os.path.dirname(__file__)
    for subject, filename in CURRICULUM_FILES.items():
        filepath = os.path.join(base_path, '..', filename)
        if os.path.exists(filepath):
            print(f"✓ {subject.upper()} curriculum found")
        else:
            print(f"✗ WARNING: {subject.upper()} curriculum not found at {filepath}")
    
    print("\nAPI Endpoints:")
    print("  POST /api/summarize       - Generate module summary")
    print("  GET  /api/modules         - List all modules")
    print("  GET  /api/health          - Health check")
    print("  POST /api/progress/save   - Save quiz result & track progress")
    print("  GET  /api/progress        - Get all progress data")
    print("  GET  /api/progress/<id>   - Get specific module progress")
    print("\nProgress File: " + PROGRESS_FILE_PATH)
    print(f"Pass Threshold: {PASS_THRESHOLD}%")
    print("\nStarting server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
