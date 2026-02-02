# How to Run the Complete Project - Copy & Paste Commands

**Date**: January 23, 2026  
**Project Path**: `c:\Users\Rohan\Desktop\dtl_2`

---

## QUICK START (4 Steps)

### Step 1: Open PowerShell Terminal #1 (Backend Server)

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
python backend\app.py
```

**Wait for this output** (takes 2-3 seconds):
```
============================================================
Module Summarization API Starting...
============================================================
✓ MATHEMATICS curriculum found
✓ AIML curriculum found
✓ PROGRAMMING_C curriculum found

API Endpoints:
  POST /api/summarize
  GET  /api/modules
  GET  /api/health
  POST /api/progress/save
  GET  /api/progress
  GET  /api/progress/<id>

Progress File: c:\Users\Rohan\Desktop\dtl_2\user_progress.json
Pass Threshold: 70%

⚠️  WARNING: This is a development server.
Press CTRL+C to quit
 * Running on http://localhost:5000
```

**✅ Keep this terminal open.** Do NOT close it.

---

### Step 2: Open PowerShell Terminal #2 (Frontend Server)

In a **NEW PowerShell window**, run:

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
python serve_frontend.py
```

**Wait for this output** (takes 1-2 seconds):
```
Serving files from: c:\Users\Rohan\Desktop\dtl_2\frontend
Starting HTTP server on http://localhost:80
Press Ctrl+C to stop.
```

**✅ Keep this terminal open too.**

---

### Step 3: Open Web Browser

Click the link or copy-paste this URL:

```
http://localhost/roadmap.html
```

**Expected**: You see the 3 subjects:
- 📐 Mathematics
- 🧠 AI & Machine Learning
- 💻 System Programming (C)

---

### Step 4: Take a Quiz and See Progress Track

1. Click on **Mathematics**
2. Click on **Beginner**
3. Click on a module (e.g., "Linear Equations")
4. Click **"Take Quiz"**
5. Answer questions
6. Submit
7. **You'll see**: Progress badge showing "In Progress..." or "Completed!"
8. Go back to Roadmap (back button)
9. **You'll see**: Progress bars updating, checkmarks on completed modules

---

## DETAILED SETUP

### Requirements Check

**Python installed?**
```powershell
python --version
```

Should show: `Python 3.x.x` (3.8+)

**pip installed?**
```powershell
pip --version
```

Should show: `pip x.x.x from ...`

---

### Full Fresh Start (Clean Installation)

If something is broken, start from scratch:

#### 1. Install Dependencies

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
pip install flask flask-cors
```

**Expected output**:
```
Successfully installed flask-3.0.0 flask-cors-4.0.0
```

---

#### 2. Create user_progress.json (if it doesn't exist)

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
@'{"modules": {}}
'@ | Out-File user_progress.json -Encoding UTF8 -Force
```

**Verify it was created**:
```powershell
Get-Content user_progress.json
```

Should show: `{"modules": {}}`

---

#### 3. Start Backend Server (Terminal #1)

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
python backend\app.py
```

---

#### 4. Start Frontend Server (Terminal #2, NEW window)

```powershell
cd c:\Users\Rohan\Desktop\dtl_2
python serve_frontend.py
```

---

#### 5. Open Browser

```
http://localhost/roadmap.html
```

---

## FOLDER STRUCTURE REFERENCE

```
c:\Users\Rohan\Desktop\dtl_2\
├── backend\
│   ├── app.py              ← Flask server (run this)
│   └── requirements.txt
├── frontend\
│   ├── roadmap.html        ← Start here
│   ├── module.html
│   ├── quiz.html
│   ├── js\
│   │   ├── roadmap.js
│   │   ├── module.js
│   │   └── quiz.js
│   ├── css\
│   │   └── (styles)
│   └── (curriculum JSON files)
├── modules\
│   ├── mathematics\
│   ├── aiml\
│   └── programming_c\
├── serve_frontend.py       ← Frontend server (run this)
├── user_progress.json      ← Auto-created by backend
└── (other files)
```

---

## COMMON ISSUES & FIXES

### Issue: "Port 5000 already in use" or "Port 80 already in use"

#### For Port 5000 (Backend)

```powershell
netstat -ano | findstr :5000
```

You'll see something like:
```
TCP    127.0.0.1:5000    0.0.0.0:0    LISTENING    12345
```

Kill the process (replace 12345 with actual PID):
```powershell
taskkill /PID 12345 /F
```

Then try again:
```powershell
python backend\app.py
```

---

#### For Port 80 (Frontend)

```powershell
netstat -ano | findstr :80
```

Kill the process:
```powershell
taskkill /PID {PID} /F
```

Then:
```powershell
python serve_frontend.py
```

---

### Issue: "Module not found: flask"

```powershell
pip install flask flask-cors
```

---

### Issue: "user_progress.json not found"

Create it:
```powershell
cd c:\Users\Rohan\Desktop\dtl_2
@'{"modules": {}}
'@ | Out-File user_progress.json -Encoding UTF8 -Force
```

---

### Issue: "Cannot access http://localhost/roadmap.html"

1. Check Terminal #2 is running: `python serve_frontend.py`
2. Check the output shows: `Starting HTTP server on http://localhost:80`
3. Try: `http://127.0.0.1/roadmap.html` instead
4. Or try without the trailing `/roadmap.html`: `http://localhost`

---

### Issue: "Quiz button does nothing" or "No progress saved"

1. Check Terminal #1 (Backend) is running
2. Check Terminal #1 shows: `Running on http://localhost:5000`
3. Check the browser console (F12 → Console tab) for errors
4. Try refreshing the page

---

### Issue: "curl: (7) Failed to connect"

Make sure backend is running in Terminal #1:
```powershell
python backend\app.py
```

Then test:
```powershell
curl http://localhost:5000/api/health
```

Should see: `{"status":"ok"}`

---

## QUICK TEST (Verify Everything Works)

### Test Backend API

```powershell
curl -X GET http://localhost:5000/api/health
```

**Expected**: `{"status":"ok"}`

---

### Test Frontend Server

```powershell
curl -X GET http://localhost/roadmap.html
```

**Expected**: HTML content (starts with `<!DOCTYPE html>`)

---

### Test Progress Saving

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

**Expected**: JSON response with `"status": "completed"`

---

## WORKING WITH THE FRONTEND

### URLs to Access

| Page | URL |
|------|-----|
| Roadmap (Start here) | `http://localhost/roadmap.html` |
| Module View | `http://localhost/module.html?module_id=linear_equations&subject=mathematics&level=beginner` |
| Debug/Test | `http://localhost/debug.html` |

---

### How to Use the Application

**1. View Roadmap**
```
http://localhost/roadmap.html
```
- Shows 3 subjects
- Shows progress bars
- Shows checkmarks on completed modules

**2. Select a Subject**
- Click on Mathematics, AI & ML, or Programming C

**3. Select a Level**
- Click Beginner, Intermediate, or Advanced

**4. Enter a Module**
- Click on a module name
- Module content loads

**5. Take a Quiz**
- Click "Take Quiz" button
- Answer the questions
- Submit
- See your score and progress badge

**6. Progress Tracking**
- Progress badge shows in module header
- Roadmap updates with checkmarks and progress %
- Progress persists on page reload (saved in user_progress.json)

---

## DATA LOCATION

### Progress Data
```
c:\Users\Rohan\Desktop\dtl_2\user_progress.json
```

View it:
```powershell
Get-Content c:\Users\Rohan\Desktop\dtl_2\user_progress.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

### Curriculum Data
```
c:\Users\Rohan\Desktop\dtl_2\frontend\mathematics_curriculum.json
c:\Users\Rohan\Desktop\dtl_2\frontend\aiml_curriculum.json
c:\Users\Rohan\Desktop\dtl_2\frontend\programming_c_curriculum.json
```

---

### Module Files
```
c:\Users\Rohan\Desktop\dtl_2\modules\mathematics\beginner\
c:\Users\Rohan\Desktop\dtl_2\modules\mathematics\intermediate\
c:\Users\Rohan\Desktop\dtl_2\modules\mathematics\advanced\
(same for aiml and programming_c)
```

---

## TERMINAL COMMANDS REFERENCE

### Start Everything

**Terminal 1:**
```powershell
cd c:\Users\Rohan\Desktop\dtl_2 && python backend\app.py
```

**Terminal 2:**
```powershell
cd c:\Users\Rohan\Desktop\dtl_2 && python serve_frontend.py
```

---

### Stop Everything

Press `Ctrl+C` in both terminals.

---

### Reset Progress Data

```powershell
@'{"modules": {}}
'@ | Out-File c:\Users\Rohan\Desktop\dtl_2\user_progress.json -Encoding UTF8 -Force
```

---

### View All Progress

```powershell
curl -X GET http://localhost:5000/api/progress
```

---

### Clear Cache (if UI not updating)

In browser DevTools (F12):
- Application → Local Storage → Clear All
- Refresh page with Ctrl+Shift+R (hard refresh)

---

## SUCCESS CHECKLIST

✅ Backend Terminal #1 shows "Running on http://localhost:5000"  
✅ Frontend Terminal #2 shows "Starting HTTP server on http://localhost:80"  
✅ Browser can access `http://localhost/roadmap.html`  
✅ Can click subjects and see modules  
✅ Can take a quiz and see score  
✅ Progress badge appears in module header  
✅ Roadmap shows progress bars and checkmarks  
✅ user_progress.json exists and contains data  

---

## NEXT STEPS

1. **Test the System**: Follow PROGRESS_TRACKING_TEST_GUIDE.md
2. **Run Full Tests**: Use curl commands from PROGRESS_TRACKING_TEST_GUIDE.md
3. **Deploy**: Modify serve_frontend.py and backend/app.py for production

---

## HELP

If something doesn't work:

1. **Check both terminals are running** (Ctrl+C to stop, re-run)
2. **Check ports are free**: 
   ```powershell
   netstat -ano | findstr ":80 \|:5000"
   ```
3. **Check files exist**:
   ```powershell
   dir c:\Users\Rohan\Desktop\dtl_2\backend\app.py
   dir c:\Users\Rohan\Desktop\dtl_2\frontend\roadmap.html
   ```
4. **Check Python version**:
   ```powershell
   python --version
   ```
5. **Reinstall dependencies**:
   ```powershell
   pip install --upgrade flask flask-cors
   ```

---

## COMPLETE SINGLE-COPY-PASTE SETUP

If you want to do everything in one go, copy this entire block:

```powershell
# Setup
cd c:\Users\Rohan\Desktop\dtl_2
pip install flask flask-cors
@'{"modules": {}}
'@ | Out-File user_progress.json -Encoding UTF8 -Force

# Backend (Terminal 1) - RUN THIS FIRST
python backend\app.py

# After backend is running, open NEW terminal (Terminal 2) and run:
# cd c:\Users\Rohan\Desktop\dtl_2
# python serve_frontend.py

# Then open browser:
# http://localhost/roadmap.html
```

**Note**: You need to run backend FIRST (Terminal 1), then frontend (Terminal 2 in new window).

