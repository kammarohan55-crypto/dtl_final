# Frontend Integration - Exact Code Changes

## File 1: frontend/js/quiz.js

### Change 1: Add Progress Tracking Function (Insert after `handleProgression()` function, around line 193)

**Insert this new function after line 193 (after `handleProgression` closes):**

```javascript
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
 * (Simple implementation - tracks from quiz start to submission)
 */
function calculateQuizDuration() {
    const startTime = window.quizStartTime || Date.now();
    return Math.round((Date.now() - startTime) / 1000);
}
```

---

### Change 2: Track Quiz Start Time (Modify `loadQuiz()` function)

**In the `loadQuiz()` function around line 37-38, add this line after `renderQuiz(currentQuiz);`:**

```javascript
    renderQuiz(currentQuiz);
    
    // Track quiz start time for duration calculation
    window.quizStartTime = Date.now();
    
    // Hide start button, show quiz container
```

---

### Change 3: Call Progress Save in `submitQuiz()` (Modify after line 165)

**In the `submitQuiz()` function, after the line `handleProgression(percentage);` (around line 165), add:**

```javascript
    // Save progress to backend
    saveProgressToBackend(percentage);
    
    // Re-render MathJax in explanations
```

---

## File 2: frontend/module.html

### Change: Add Progress Status Display (Insert after line 44, in the topic header section)

**In the `<header class="topic-header">` section, add this new div after the `<p id="moduleMotivation">` line:**

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

## File 3: frontend/js/module.js

### Change: Load and Display Progress on Module Load (Insert in `renderModule()` function after line 50)

**In the `renderModule()` function, after all the content rendering is done (around line 50-60), add this code:**

```javascript
    // Render Mathematical Formulation
    // ... (existing code)
    
    // After all content is rendered, load and display progress
    loadAndDisplayProgress(data.module_id);
}

/**
 * Load module progress from backend and display status
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

## Summary of Changes

| File | Location | Change Type | Purpose |
|------|----------|-------------|---------|
| quiz.js | After line 193 | Add 4 new functions | Save progress, update UI, fallback mechanism |
| quiz.js | Line 40 (in loadQuiz) | Add 1 line | Track quiz start time |
| quiz.js | After line 165 | Add 1 line | Call backend progress save |
| module.html | After line 46 | Add HTML div | Display progress status |
| module.js | End of renderModule() | Add 1 function call + new function | Load and display progress |

---

## Testing the Integration

After making these changes, test with:

```powershell
# 1. Start backend
python backend/app.py

# 2. Open frontend in browser
# http://localhost:8000/frontend/roadmap.html (or your server)

# 3. Select a module and take a quiz

# 4. Check browser console (F12 → Console tab)
# Should see: "Progress saved to backend: {...}"

# 5. Reload the module page
# Should see progress status displayed in the module header
```

---

## What Each Change Does

### `saveProgressToBackend(score)`
- Prepares progress payload with module_id, score, subject, level, time_taken
- Calls POST /api/progress/save
- On success: updates UI with progress badges, clears fallback localStorage
- On failure: saves to localStorage under 'fallback_progress' key for later sync

### `updateProgressUI(progressData)`
- Displays colored badges based on status (green for completed, amber for in_progress)
- Shows best_score and attempts count
- Inserts badge at top of progression message

### `saveFallbackProgress(progressPayload)` & `clearFallbackProgress(moduleId)`
- Fallback mechanism when backend is unavailable
- Stores in localStorage: `fallback_progress` key
- Clears when successfully synced

### `calculateQuizDuration()`
- Measures time from quiz start (`window.quizStartTime`) to submission
- Returns duration in seconds

### `loadAndDisplayProgress(moduleId)` in module.js
- Calls GET /api/progress/:module_id on module load
- Displays progress status in header (if progress exists)
- Shows: "Completed! Best: X% (Y attempts)" or "In Progress — Last: X% (Y attempts)"

---

