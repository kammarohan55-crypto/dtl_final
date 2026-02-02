# Progress Tracking System - Complete Test Guide

**Date**: January 23, 2026  
**Project**: Educational Platform with Progress Persistence  
**Status**: Ready for Testing

---

## PART 1: SETUP & VERIFICATION

### 1.1 Verify Files Exist

```powershell
# Check user_progress.json
Test-Path c:\Users\Rohan\Desktop\dtl_2\user_progress.json

# Check backend/app.py
Test-Path c:\Users\Rohan\Desktop\dtl_2\backend\app.py
```

**Expected**: Both return `True`

---

### 1.2 Create Initial user_progress.json (if needed)

If the file doesn't exist, create it:

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
@'
{"modules": {}}
'@ | Out-File user_progress.json -Encoding UTF8
```

**Verify**:
```powershell
Get-Content user_progress.json
```

Expected output:
```json
{"modules": {}}
```

---

### 1.3 Start Flask Backend

**Terminal 1** (Keep this running):
```powershell
cd c:\Users\Rohan\Desktop\dtl_2
python backend\app.py
```

**Expected output** (you should see):
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

⚠️  WARNING: This is a development server. Do not use it in production.
    Use a production WSGI server instead.
⚠️  WARNING: Debugger is active!
Press CTRL+C to quit
```

If you see this, the backend is ready. **Do not close this terminal.**

---

### 1.4 Test Server Connectivity

**Terminal 2** (New terminal for testing):
```powershell
curl -X GET http://localhost:5000/api/health
```

**Expected response**:
```json
{"status": "ok"}
```

If this works, proceed to Part 2.

---

## PART 2: CURL API TESTS

### 2.1 Test POST /api/progress/save - First Attempt (FAIL)

**Command**:
```powershell
$body = @{
    module_id = "linear_equations"
    score = 65
    subject = "mathematics"
    level = "beginner"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected response** (HTTP 200):
```json
{
  "success": true,
  "module_id": "linear_equations",
  "status": "in_progress",
  "attempts": 1,
  "best_score": 65,
  "last_score": 65,
  "last_attempted_at": "2026-01-23T14:35:22.123456Z",
  "message": "Progress saved: score 65 -> status in_progress"
}
```

**What to verify**:
- ✅ `status` = "in_progress" (because 65 < 70)
- ✅ `attempts` = 1 (first submission)
- ✅ `best_score` = 65 (only attempt)
- ✅ `last_score` = 65

---

### 2.2 Test POST /api/progress/save - Second Attempt (PASS)

**Command**:
```powershell
$body = @{
    module_id = "linear_equations"
    score = 85
    subject = "mathematics"
    level = "beginner"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected response** (HTTP 200):
```json
{
  "success": true,
  "module_id": "linear_equations",
  "status": "completed",
  "attempts": 2,
  "best_score": 85,
  "last_score": 85,
  "last_attempted_at": "2026-01-23T14:36:15.654321Z",
  "message": "Progress saved: score 85 -> status completed (best score improved)"
}
```

**What to verify**:
- ✅ `status` = "completed" (because 85 ≥ 70)
- ✅ `attempts` = 2 (incremented from 1)
- ✅ `best_score` = 85 (improved from 65)
- ✅ `last_score` = 85

---

### 2.3 Test GET /api/progress (All Progress)

**Command**:
```powershell
curl -X GET http://localhost:5000/api/progress
```

**Expected response** (HTTP 200):
```json
{
  "success": true,
  "total_modules_attempted": 1,
  "completed_count": 1,
  "in_progress_count": 0,
  "modules": {
    "linear_equations": {
      "subject": "mathematics",
      "level": "beginner",
      "status": "completed",
      "attempts": 2,
      "best_score": 85,
      "last_score": 85,
      "last_attempted_at": "2026-01-23T14:36:15.654321Z",
      "history": [
        {
          "score": 65,
          "attempted_at": "2026-01-23T14:35:22.123456Z",
          "time_taken": null
        },
        {
          "score": 85,
          "attempted_at": "2026-01-23T14:36:15.654321Z",
          "time_taken": null
        }
      ]
    }
  }
}
```

**What to verify**:
- ✅ `total_modules_attempted` = 1
- ✅ `completed_count` = 1
- ✅ `in_progress_count` = 0
- ✅ `history` array has 2 entries
- ✅ Both scores (65, 85) are in history

---

### 2.4 Test GET /api/progress/<module_id> (Specific Module)

**Command**:
```powershell
curl -X GET http://localhost:5000/api/progress/linear_equations
```

**Expected response** (HTTP 200):
```json
{
  "success": true,
  "module_id": "linear_equations",
  "data": {
    "subject": "mathematics",
    "level": "beginner",
    "status": "completed",
    "attempts": 2,
    "best_score": 85,
    "last_score": 85,
    "last_attempted_at": "2026-01-23T14:36:15.654321Z",
    "history": [
      {
        "score": 65,
        "attempted_at": "2026-01-23T14:35:22.123456Z",
        "time_taken": null
      },
      {
        "score": 85,
        "attempted_at": "2026-01-23T14:36:15.654321Z",
        "time_taken": null
      }
    ]
  }
}
```

**What to verify**:
- ✅ Matches the module data from /api/progress
- ✅ `history` has both attempts
- ✅ `best_score` = 85 (not 65)

---

### 2.5 Test GET /api/progress/<module_id> (Non-existent Module)

**Command**:
```powershell
curl -X GET http://localhost:5000/api/progress/does_not_exist
```

**Expected response** (HTTP 404):
```json
{
  "success": false,
  "error": "No progress record found for module: does_not_exist"
}
```

**What to verify**:
- ✅ Returns HTTP 404 status
- ✅ Error message is descriptive

---

### 2.6 Test POST with Invalid Data - Missing Fields

**Command**:
```powershell
$body = @{
    score = 85
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected response** (HTTP 400):
```json
{
  "success": false,
  "error": "module_id is required and must be a string"
}
```

**What to verify**:
- ✅ Returns HTTP 400 status
- ✅ Clear error message

---

### 2.7 Test POST with Invalid Score (Out of Range)

**Command**:
```powershell
$body = @{
    module_id = "test_module"
    score = 150
    subject = "mathematics"
    level = "beginner"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected response** (HTTP 400):
```json
{
  "success": false,
  "error": "score must be between 0 and 100"
}
```

**What to verify**:
- ✅ Returns HTTP 400 status
- ✅ Rejects invalid scores

---

### 2.8 Test POST with Invalid Score (Negative)

**Command**:
```powershell
$body = @{
    module_id = "test_module"
    score = -5
    subject = "mathematics"
    level = "beginner"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected response** (HTTP 400):
```json
{
  "success": false,
  "error": "score must be between 0 and 100"
}
```

---

## PART 3: VERIFY FILE PERSISTENCE

### 3.1 Check user_progress.json Contents

**Command**:
```powershell
Get-Content c:\Users\Rohan\Desktop\dtl_2\user_progress.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Expected**: Should show:
```json
{
  "modules": {
    "linear_equations": {
      "subject": "mathematics",
      "level": "beginner",
      "status": "completed",
      "attempts": 2,
      "best_score": 85,
      "last_score": 85,
      "last_attempted_at": "2026-01-23T14:36:15.654321Z",
      "history": [
        {
          "score": 65,
          "attempted_at": "2026-01-23T14:35:22.123456Z",
          "time_taken": null
        },
        {
          "score": 85,
          "attempted_at": "2026-01-23T14:36:15.654321Z",
          "time_taken": null
        }
      ]
    }
  }
}
```

**What to verify**:
- ✅ File exists and is valid JSON
- ✅ Data matches what was POSTed
- ✅ Both attempts are preserved

---

### 3.2 Verify Persistence After Restart

**Command** (in Terminal 1 where Flask is running):
```
Press Ctrl+C to stop the server
```

Then restart:
```powershell
python backend\app.py
```

**Command** (in Terminal 2):
```powershell
curl -X GET http://localhost:5000/api/progress
```

**Expected**: Same data as before restart
- ✅ Progress data persists across server restarts
- ✅ No data loss on restart

---

## PART 4: BROWSER MANUAL TEST

### 4.1 Navigate to Module Page

1. Open browser: `http://localhost/module.html?module_id=linear_equations&subject=mathematics&level=beginner`
2. **Expected**: Module content loads
3. **Look for**: Blue progress status bar in module header
4. **Expected badge**: "✓ Completed! Best: 85% (2 attempts)"

---

### 4.2 Take Another Quiz (Test Non-Downgrade)

1. Click "Take Quiz" button
2. Answer questions (aim for score < 85, e.g., 75)
3. Submit quiz
4. **Expected badge update**: "✓ Completed! Best: 85% (3 attempts)"
   - Note: best_score stays 85 (not downgraded to 75)
   - Note: attempts increments to 3

---

### 4.3 Navigate to Roadmap

1. Open browser: `http://localhost/roadmap.html`
2. **Expected**: Three subject cards visible
3. **Check Mathematics card**:
   - Progress bar should show: `100%` (1/1 modules completed)
   - Module chip "linear_equations" should have green background + ✓ checkmark

---

### 4.4 Test Multiple Modules

Create progress for more modules (in Terminal 2):

```powershell
# Module 2 - In Progress
$body = @{
    module_id = "quadratic_equations"
    score = 55
    subject = "mathematics"
    level = "intermediate"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body

# Module 3 - Completed
$body = @{
    module_id = "calculus_basics"
    score = 92
    subject = "mathematics"
    level = "advanced"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Refresh Roadmap** (`http://localhost/roadmap.html`):
- Click "Mathematics"
- **Expected progress bar**: ~66% (2/3 modules completed)
- **Expected checkmarks**:
  - ✓ linear_equations (green)
  - ✓ calculus_basics (green)
  - ○ quadratic_equations (gray)

---

## PART 5: EDGE CASE TESTS

### 5.1 Re-Submit Lower Score After Completed (NO DOWNGRADE)

**Current state**: linear_equations has status "completed", best_score 85

**Command**:
```powershell
$body = @{
    module_id = "linear_equations"
    score = 50
    subject = "mathematics"
    level = "beginner"
} | ConvertTo-Json

curl -X POST http://localhost:5000/api/progress/save `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected response** (HTTP 200):
```json
{
  "success": true,
  "module_id": "linear_equations",
  "status": "completed",
  "attempts": 4,
  "best_score": 85,
  "last_score": 50,
  "last_attempted_at": "2026-01-23T14:37:30.123456Z",
  "message": "Progress saved: score 50 -> already completed, not downgraded"
}
```

**What to verify**:
- ✅ `status` REMAINS "completed" (not downgraded to in_progress)
- ✅ `attempts` incremented to 4
- ✅ `best_score` REMAINS 85 (not changed to 50)
- ✅ `last_score` = 50 (most recent)
- ✅ Message indicates "not downgraded"

---

### 5.2 Test Concurrent Writes (Two Quick POSTs)

**Purpose**: Verify no data loss with simultaneous requests

**Command** (run both in rapid succession):
```powershell
# POST 1 - Module A
$body1 = @{
    module_id = "module_a"
    score = 80
    subject = "mathematics"
    level = "beginner"
} | ConvertTo-Json

# POST 2 - Module B
$body2 = @{
    module_id = "module_b"
    score = 75
    subject = "mathematics"
    level = "intermediate"
} | ConvertTo-Json

# Send both quickly
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body1 &
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body2 &
Wait-Job
```

**Expected**: Both requests succeed, both modules appear in /api/progress

**Verify**:
```powershell
curl -X GET http://localhost:5000/api/progress
```

**Expected response**:
```json
{
  "success": true,
  "total_modules_attempted": 5,
  "completed_count": 3,
  "in_progress_count": 2,
  "modules": {
    "linear_equations": { ... },
    "quadratic_equations": { ... },
    "calculus_basics": { ... },
    "module_a": { ... },
    "module_b": { ... }
  }
}
```

**What to verify**:
- ✅ All 5 modules are present
- ✅ No data was lost
- ✅ `total_modules_attempted` = 5 (not 4, not 3)
- ✅ PROGRESS_LOCK prevented file corruption

---

### 5.3 Status Transitions (Truth Table)

Create a test module and verify status transitions:

| Current Score | Current Status | New Score | Expected New Status | Expected best_score |
|---|---|---|---|---|
| — | — | 50 | in_progress | 50 |
| 50 | in_progress | 60 | in_progress | 60 |
| 60 | in_progress | 70 | completed | 70 |
| 70 | completed | 75 | completed | 75 |
| 75 | completed | 50 | completed | 75 |
| 75 | completed | 85 | completed | 85 |

**Test all transitions**:

```powershell
# Row 1: Score 50
$body = @{module_id = "transition_test"; score = 50; subject = "mathematics"; level = "beginner"} | ConvertTo-Json
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body

# Row 2: Score 60
$body = @{module_id = "transition_test"; score = 60; subject = "mathematics"; level = "beginner"} | ConvertTo-Json
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body

# Row 3: Score 70 (PASS!)
$body = @{module_id = "transition_test"; score = 70; subject = "mathematics"; level = "beginner"} | ConvertTo-Json
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body

# Row 4: Score 75
$body = @{module_id = "transition_test"; score = 75; subject = "mathematics"; level = "beginner"} | ConvertTo-Json
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body

# Row 5: Score 50 (should NOT downgrade)
$body = @{module_id = "transition_test"; score = 50; subject = "mathematics"; level = "beginner"} | ConvertTo-Json
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body

# Row 6: Score 85
$body = @{module_id = "transition_test"; score = 85; subject = "mathematics"; level = "beginner"} | ConvertTo-Json
curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d $body
```

**Verify final state**:
```powershell
curl -X GET http://localhost:5000/api/progress/transition_test
```

**Expected final**:
- status = "completed"
- best_score = 85
- attempts = 6
- history has all 6 scores in order

---

## PART 6: SUMMARY CHECKLIST

### API Tests
- [ ] POST /api/progress/save with score < 70 → in_progress
- [ ] POST /api/progress/save with score ≥ 70 → completed
- [ ] GET /api/progress returns all modules
- [ ] GET /api/progress/<id> returns specific module
- [ ] GET /api/progress/<id> 404s for non-existent
- [ ] POST with missing field → 400
- [ ] POST with invalid score → 400
- [ ] Attempts increment correctly
- [ ] best_score never downgrades after completed
- [ ] history array has all attempts

### File Persistence
- [ ] user_progress.json exists and is valid JSON
- [ ] Data matches POSTed values
- [ ] Persistence survives server restart
- [ ] File is in c:\Users\Rohan\Desktop\dtl_2\

### Browser Integration
- [ ] Module page shows progress badge
- [ ] Quiz submission POSTs to /api/progress/save
- [ ] Progress badge updates after quiz
- [ ] Roadmap shows progress bars
- [ ] Roadmap shows checkmarks on completed modules
- [ ] Roadmap shows completion percentage

### Edge Cases
- [ ] Lower score after completed doesn't downgrade status
- [ ] Concurrent writes don't lose data
- [ ] Status transitions follow truth table
- [ ] PASS_THRESHOLD = 70 is enforced

---

## Troubleshooting

### "Port 5000 already in use"
```powershell
netstat -ano | findstr :5000
taskkill /PID {PID} /F
```

### "user_progress.json not found"
- Backend looks for it in `c:\Users\Rohan\Desktop\dtl_2\`
- Ensure you're running `python backend\app.py` from the repo root
- Or create it manually (see 1.2 above)

### "Connection refused"
- Flask backend not running in Terminal 1
- Restart: `python backend\app.py`
- Verify with: `curl http://localhost:5000/api/health`

### "Invalid JSON in curl"
- Make sure to use backticks for line continuation in PowerShell
- Or save JSON to file and use `@file`:
  ```powershell
  @'{"module_id": "test", "score": 85}
  '@ > body.json
  curl -X POST http://localhost:5000/api/progress/save -H "Content-Type: application/json" -d @body.json
  ```

### "CORS error in browser"
- Frontend must be on same origin (localhost) or use http://localhost:5000 in API calls
- Check `frontend/js/quiz.js` and `roadmap.js` for correct URL

---

## Success Criteria

✅ All curl tests return expected JSON responses  
✅ HTTP status codes are correct (200, 400, 404)  
✅ user_progress.json is created and updated  
✅ Browser shows progress badges and roadmap indicators  
✅ No data loss on concurrent writes  
✅ Status never downgrades from completed to in_progress  
✅ Persistence survives server restart  

**If all checks pass, the progress tracking system is production-ready!**

