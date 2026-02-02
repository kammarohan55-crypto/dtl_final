# 🚀 How to Run Your Updated Academic Website

## ✅ Quick Start (Easiest Method)

**Just double-click this file:**
```
START_SERVERS.bat
```

This will:
- Start the backend server (AI summaries) on port 5000
- Start the frontend server on port 8000
- Automatically open your browser to the website

**Keep both command windows running!**

---

## 📖 Manual Method (If batch file doesn't work)

### Step 1: Start Frontend Server

Open Command Prompt or PowerShell in the `dtl` folder and run:

```powershell
python serve_frontend.py
```

You should see:
```
==============================================================
Frontend Server Running!
==============================================================

🌐 Open your browser and go to:

   http://localhost:8000/module.html
```

### Step 2: Start Backend Server (Optional - for AI Summaries)

Open a **NEW** Command Prompt/PowerShell window:

```powershell
cd backend
python app.py
```

---

## 🎯 Using the Website

### Option 1: View Modules
1. Open browser to: **http://localhost:8000/module.html**
2. Select **Subject** (Mathematics, Programming C, or AIML)
3. Select **Level** (Beginner, Intermediate, Advanced)
4. Select **Module** from dropdown
5. Click **"Load Module"** to view content
6. Click **"🤖 Summarize with AI"** (if backend running)

### Option 2: View Roadmap
1. Open: **http://localhost:8000/roadmap.html**
2. Select subject to see learning progression
3. View all modules organized by level

---

## ✨ What You'll See

### All 52 Updated Modules:
- **Mathematics**: 17 modules (Linear Equations, Calculus, Probability & Statistics)
- **Programming C**: 20 modules (C Basics, Data Structures, Advanced Techniques)
- **AIML**: 15 modules (AI Foundations, ML Algorithms, Advanced Topics)

### In Each Module:
✅ Comprehensive theory sections  
✅ Mathematical formulas (rendered with MathJax)  
✅ Worked examples with step-by-step solutions  
✅ Interactive quizzes (8-12 questions)  
✅ AI-generated summaries with exam tips  
✅ Common mistakes and how to avoid them  

---

## 🔧 Troubleshooting

**Port already in use?**
```powershell
# Change port in serve_frontend.py (line 9)
PORT = 8001  # Use different port
```

**Browser shows blank page?**
- Make sure you're accessing `http://localhost:8000/module.html`
- Check that `serve_frontend.py` terminal shows "Running"
- Try refreshing the browser (Ctrl+F5)

**AI Summary not working?**
- This is optional - you can view all content without AI summaries
- To enable: Make sure backend server is running on port 5000

---

## 📁 Files Location

**Your updated curricula:**
- `frontend/mathematics_curriculum.json` (513 KB)
- `frontend/programming_c_curriculum.json` (551 KB)
- `frontend/aiml_curriculum.json` (618 KB)

**Roadmaps:**
- `frontend/roadmaps/mathematics_roadmap.json`
- `frontend/roadmaps/programming_c_roadmap.json`
- `frontend/roadmaps/aiml_roadmap.json`

**Web pages:**
- `frontend/module.html` - Main module viewer
- `frontend/roadmap.html` - Learning roadmap viewer

---

## ✅ Success Checklist

- [ ] Frontend server running (one command window)
- [ ] Browser shows module page
- [ ] Can select subject, level, and module
- [ ] Module content loads and displays
- [ ] Math formulas render correctly (LaTeX/MathJax)
- [ ] Quizzes are interactive
- [ ] No errors in browser console (F12)

---

## 🎓 Ready for Use!

Your academic website now contains:
- **52 comprehensive modules** across 3 subjects
- **200+ mathematical formulas** properly formatted
- **500+ quiz questions** with detailed explanations
- **AI-generated summaries** for exam preparation

**The website is ready for students to use!**

---

**Need help?** Check the browser console (press F12) for any error messages.
