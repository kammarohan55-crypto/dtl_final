# QUICK REFERENCE - EXACT CODE CHANGES

## Summary

Three frontend files modified to call progress API after quiz submission and display progress in module header.

---

## FILE 1: frontend/js/quiz.js

### Change 1.1 (Line ~40)
**Location:** In `loadQuiz()` function, after `renderQuiz(currentQuiz);`

```javascript
// Track quiz start time for duration calculation
window.quizStartTime = Date.now();
```

---

### Change 1.2 (Line ~167)
**Location:** In `submitQuiz()` function, after `const percentage = Math.round(...)`

```javascript
// Save progress to backend
saveProgressToBackend(score);
```

Replace `score` with `percentage` if variable name differs in your version.

---

### Change 1.3 (Lines ~248-389)
**Location:** End of file, after `resetQuiz()` function

```javascript
// ============================================================================
// PROGRESS TRACKING - Backend Integration
// ============================================================================

/**
 * Save progress to backend API with fallback to localStorage
 * Calls POST /api/progress/save with score and module metadata
 */
async function saveProgressToBackend(score) {
    const currentModule = window.moduleState.getCurrentModule();
    
    if (!currentModule) {
        console.warn("Module not loaded, skipping backend progress save");
        return;
    }
    
    const progressPayload = {
        module_id: currentModule.module_id,
        score: score,
        subject: currentModule.subject,
        level: currentModule.level,
        time_taken: calculateQuizDuration()  // in seconds
    };
    
    try {
        const response = await fetch('/api/progress/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(progressPayload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Progress saved to backend:', data);
            // Update UI with backend response
            updateProgressUI(data);
            // Clear fallback localStorage if exists
            clearFallbackProgress(currentModule.module_id);
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Backend save failed, using fallback:', error);
        // Fallback: save to localStorage for later sync
        saveFallbackProgress(progressPayload);
    }
}

/**
 * Update UI with progress data from backend
 */
function updateProgressUI(progressData) {
    const statusDiv = document.getElementById('progressionMessage');
    
    if (progressData.status === 'completed') {
        // Add completed badge
        const completedBadge = document.createElement('div');
        completedBadge.style.cssText = `
            background: #10b981; 
            color: white; 
            padding: 12px 16px; 
            border-radius: 8px; 
            margin-bottom: 12px; 
            font-weight: 600;
            text-align: center;
        `;
        completedBadge.innerHTML = `
            <i class="fas fa-check-circle"></i> Module Completed! 
            Best Score: ${progressData.best_score}% (${progressData.attempts} attempt${progressData.attempts > 1 ? 's' : ''})
        `;
        
        if (statusDiv.firstChild) {
            statusDiv.insertBefore(completedBadge, statusDiv.firstChild);
        } else {
            statusDiv.appendChild(completedBadge);
        }
    } else if (progressData.status === 'in_progress') {
        // Show progress badge
        const inProgressBadge = document.createElement('div');
        inProgressBadge.style.cssText = `
            background: #f59e0b; 
            color: white; 
            padding: 12px 16px; 
            border-radius: 8px; 
            margin-bottom: 12px; 
            font-weight: 600;
            text-align: center;
        `;
        inProgressBadge.innerHTML = `
            <i class="fas fa-hourglass-half"></i> In Progress — 
            Best Score: ${progressData.best_score}% (${progressData.attempts} attempt${progressData.attempts > 1 ? 's' : ''})
        `;
        
        if (statusDiv.firstChild) {
            statusDiv.insertBefore(inProgressBadge, statusDiv.firstChild);
        } else {
            statusDiv.appendChild(inProgressBadge);
        }
    }
}

/**
 * Save progress to localStorage as fallback when backend is unavailable
 */
function saveFallbackProgress(progressPayload) {
    let fallback = JSON.parse(localStorage.getItem('fallback_progress') || '{}');
    
    fallback[progressPayload.module_id] = {
        ...progressPayload,
        timestamp: new Date().toISOString(),
        synced: false
    };
    
    localStorage.setItem('fallback_progress', JSON.stringify(fallback));
    console.log('Progress saved to fallback localStorage');
}

/**
 * Clear fallback progress after successful backend sync
 */
function clearFallbackProgress(moduleId) {
    let fallback = JSON.parse(localStorage.getItem('fallback_progress') || '{}');
    delete fallback[moduleId];
    localStorage.setItem('fallback_progress', JSON.stringify(fallback));
}

/**
 * Calculate quiz duration in seconds
 * Tracks from quiz start (window.quizStartTime) to submission
 */
function calculateQuizDuration() {
    const startTime = window.quizStartTime || Date.now();
    return Math.round((Date.now() - startTime) / 1000);
}
```

---

## FILE 2: frontend/module.html

### Change 2.1 (After Line 46)
**Location:** In `<header class="topic-header">` section, after `<p id="moduleMotivation">` line

```html
            <!-- Progress Status Display -->
            <div id="moduleProgressStatus" style="
                margin-top: 16px; 
                padding: 12px 16px; 
                border-radius: 8px; 
                background: #f0f9ff; 
                border-left: 4px solid #3b82f6;
                display: none;
                font-size: 14px;
            ">
                <span id="progressStatusText"></span>
            </div>
```

**Full section should look like:**
```html
        <header class="topic-header">
            <div id="moduleLevelBadge" class="level-pill">...</div>
            <h1 id="moduleName">Topic Loading...</h1>
            <p id="moduleMotivation" class="motivation-text">Loading motivation...</p>
            
            <!-- Progress Status Display -->
            <div id="moduleProgressStatus" style="
                margin-top: 16px; 
                padding: 12px 16px; 
                border-radius: 8px; 
                background: #f0f9ff; 
                border-left: 4px solid #3b82f6;
                display: none;
                font-size: 14px;
            ">
                <span id="progressStatusText"></span>
            </div>
        </header>
```

---

## FILE 3: frontend/js/module.js

### Change 3.1 (End of renderModule() function)
**Location:** In `renderModule()` function, after `window.MathJax.typesetPromise()` block

Add this line:
```javascript
    // Load and display progress from backend
    loadAndDisplayProgress(data.module_id);
}
```

---

### Change 3.2 (End of file, after moduleState object)
**Location:** After `window.moduleState = { ... };` closes

```javascript
// ============================================================================
// PROGRESS TRACKING - Load and Display Progress
// ============================================================================

/**
 * Load module progress from backend and display status in module header
 */
async function loadAndDisplayProgress(moduleId) {
    const progressDiv = document.getElementById('moduleProgressStatus');
    
    try {
        const response = await fetch(`/api/progress/${moduleId}`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.module_id) {
                const status = data.status;
                const attempts = data.attempts;
                const bestScore = data.best_score;
                const lastScore = data.last_score;
                
                let statusText = '';
                let bgColor = '';
                let borderColor = '';
                
                if (status === 'completed') {
                    bgColor = '#dcfce7';  // light green
                    borderColor = '#22c55e';  // green
                    statusText = `
                        <i class="fas fa-check-circle" style="color: #16a34a;"></i>
                        <strong>Completed!</strong> Best Score: ${bestScore}% 
                        <span style="font-size: 13px; color: #666;">(${attempts} attempt${attempts > 1 ? 's' : ''})</span>
                    `;
                } else if (status === 'in_progress') {
                    bgColor = '#fef3c7';  // light amber
                    borderColor = '#f59e0b';  // amber
                    statusText = `
                        <i class="fas fa-hourglass-half" style="color: #d97706;"></i>
                        <strong>In Progress</strong> — Last Score: ${lastScore}% 
                        <span style="font-size: 13px; color: #666;">(${attempts} attempt${attempts > 1 ? 's' : ''})</span>
                    `;
                } else {
                    // Not attempted yet
                    progressDiv.style.display = 'none';
                    return;
                }
                
                // Update UI
                progressDiv.style.display = 'block';
                progressDiv.style.background = bgColor;
                progressDiv.style.borderLeftColor = borderColor;
                document.getElementById('progressStatusText').innerHTML = statusText;
            }
        }
    } catch (error) {
        console.log('Progress not available:', error);
        // Don't show error - progress is optional
    }
}
```

---

## Changes Summary

| File | Location | Change Type | Lines |
|------|----------|-------------|-------|
| quiz.js | Line ~40 | Insert | 1 |
| quiz.js | Line ~167 | Insert | 1 |
| quiz.js | Line ~248-389 | Insert | 145 |
| module.html | After line 46 | Insert | 12 |
| module.js | Line ~115 | Insert | 1 |
| module.js | Line ~153-230 | Insert | 78 |

**Total: ~240 lines added, 0 deleted**

---

## Verification

After making changes:

1. **Check quiz.js has `saveProgressToBackend()` function**
   - Ctrl+F in editor: `saveProgressToBackend`
   - Should find the function definition

2. **Check module.html has progress div**
   - Ctrl+F: `moduleProgressStatus`
   - Should find one `<div id="moduleProgressStatus" ...>`

3. **Check module.js has `loadAndDisplayProgress()` function**
   - Ctrl+F: `loadAndDisplayProgress`
   - Should find function definition and function call

---

## Testing After Changes

```powershell
# 1. Start backend
python backend/app.py

# 2. Open module page in browser
# http://localhost:8000/frontend/roadmap.html (or file:/// path)

# 3. Select module → take quiz → submit

# 4. Check browser console (F12)
# Should see: "Progress saved to backend: {...}"

# 5. Verify progress badge displays above progression message

# 6. Reload module page
# Progress should still display (loaded from backend)
```

---

