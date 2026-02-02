# QUICK TEST GUIDE - Progress Tracking API

## Step 1: Start the Flask Server

Open PowerShell and run:
```powershell
cd c:\Users\Rohan\Desktop\dtl_2
python backend\app.py
```

Expected output:
```
============================================================
Module Summarization API Starting...
============================================================
✓ MATHEMATICS curriculum found
✓ AIML curriculum found
✓ PROGRAMMING_C curriculum found

API Endpoints:
  POST /api/summarize       - Generate module summary
  GET  /api/modules         - List all modules
  GET  /api/health          - Health check
  POST /api/progress/save   - Save quiz result & track progress
  GET  /api/progress        - Get all progress data
  GET  /api/progress/<id>   - Get specific module progress

Progress File: c:\Users\Rohan\Desktop\dtl_2\user_progress.json
Pass Threshold: 70%

Starting server on http://localhost:5000
============================================================
```

## Step 2: Open Another PowerShell Terminal

Keep the first one running, open a new terminal.

## Step 3: Run a Quick Test

Save an attempt with score < 70 (should be "in_progress"):

```powershell
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "linear_equations", "score": 65, "subject": "mathematics", "level": "beginner"}'
```

Expected response:
```json
{
  "success": true,
  "module_id": "linear_equations",
  "status": "in_progress",
  "attempts": 1,
  "best_score": 65,
  "last_score": 65,
  "last_attempted_at": "2026-01-23T10:30:00.123456Z"
}
```

## Step 4: Save a Passing Score

Score >= 70 (should be "completed"):

```powershell
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "linear_equations", "score": 85, "subject": "mathematics", "level": "beginner"}'
```

Expected response: status = "completed"

## Step 5: Check All Progress

```powershell
curl -X GET http://localhost:5000/api/progress
```

Expected response shows total_modules_attempted=1, completed_count=1

## Step 6: Check Specific Module

```powershell
curl -X GET http://localhost:5000/api/progress/linear_equations
```

Returns all attempts in the history array

## Step 7: Verify File Created

Check that `user_progress.json` exists in the project root:

```powershell
Get-Content c:\Users\Rohan\Desktop\dtl_2\user_progress.json | ConvertFrom-Json | ConvertTo-Json
```

Should show the modules with their records.

---

## Files to Review

1. **backend/app.py** - Modified Flask app with new endpoints
   - Lines 1-27: Imports and constants
   - Lines 30-142: Helper functions (load_progress, save_progress, etc.)
   - Lines 294-521: Three new API endpoints

2. **user_progress.json** - Progress storage file (auto-created)
   - Location: c:\Users\Rohan\Desktop\dtl_2\user_progress.json

3. **PROGRESS_TRACKING_IMPLEMENTATION.md** - Full documentation

4. **PROGRESS_TRACKING_TESTS.txt** - Detailed test commands with examples

---

## Common Issues & Fixes

### Issue: Port 5000 already in use
```powershell
# Find the process using port 5000
netstat -ano | findstr :5000

# Kill it (replace PID with the process ID)
taskkill /PID {PID} /F

# Then restart: python backend\app.py
```

### Issue: File not found error
- Ensure you're in the correct directory: `c:\Users\Rohan\Desktop\dtl_2`
- The server finds `user_progress.json` relative to the `backend/app.py` location

### Issue: JSON parse error
- Make sure you're using backticks for line continuation in PowerShell
- Or write JSON to a file and use `@file` in curl

---

## Detailed Test Scenarios

### Scenario 1: Student Takes Quiz (Fails, then Passes)

```powershell
# First attempt - Score 60
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "number_systems", "score": 60, "subject": "mathematics", "level": "beginner"}'

# Result: status="in_progress", attempts=1, best_score=60

# Second attempt - Score 80
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "number_systems", "score": 80, "subject": "mathematics", "level": "beginner"}'

# Result: status="completed", attempts=2, best_score=80

# Check progress
curl -X GET http://localhost:5000/api/progress/number_systems

# Result: Shows both attempts in history array
```

### Scenario 2: Multiple Modules

```powershell
# Save progress for Module 1
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "module_1", "score": 85, "subject": "mathematics", "level": "beginner"}'

# Save progress for Module 2
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "module_2", "score": 65, "subject": "mathematics", "level": "beginner"}'

# Get all progress
curl -X GET http://localhost:5000/api/progress

# Result: total_modules_attempted=2, completed_count=1 (only module_1)
```

### Scenario 3: Invalid Inputs

```powershell
# Missing module_id
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"score": 85}'

# Result: 400 - "module_id is required and must be a string"

# Score out of range
curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d '{"module_id": "test", "score": 150}'

# Result: 400 - "score must be between 0 and 100"

# Non-existent module in GET
curl -X GET http://localhost:5000/api/progress/does_not_exist

# Result: 404 - "No progress record found for module: does_not_exist"
```

---

## Integration Notes

The progress tracking endpoints are ready for frontend integration:

1. **After Quiz Submission** (in quiz.js):
   - Call POST /api/progress/save with score
   - Check response.status to show "Completed" badge

2. **On Roadmap Load** (in roadmap.js):
   - Call GET /api/progress
   - Mark module chips as "completed" visually

3. **Module Info** (in module.html):
   - Call GET /api/progress/<module_id>
   - Show previous attempts and best score

See PROGRESS_TRACKING_IMPLEMENTATION.md for code examples.

---

## Data Persistence

✅ Progress is saved to disk in `user_progress.json`  
✅ Persists between server restarts  
✅ Thread-safe with PROGRESS_LOCK  
✅ Atomic file writes prevent corruption  
✅ Works on Windows and Unix systems  

---

