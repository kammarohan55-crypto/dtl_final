# Roadmap Progress Indicators - Exact Code Changes

## Summary

Add progress bars to subject cards and green checkmarks to completed modules on the roadmap page.

---

## File 1: frontend/js/roadmap.js

### Change 1.1: Initialize Progress on Page Load (DOMContentLoaded)

**Replace lines 5-8** in the DOMContentLoaded listener:

```javascript
document.addEventListener('DOMContentLoaded', () => {
    setupSubjectSelection();
    setupBackButton();
    loadProgressData();  // NEW: Load progress from backend
});
```

---

### Change 1.2: Add Progress Loading Function (After setupBackButton)

**Insert after line 26 (after `setupBackButton()` function closes)**:

```javascript
// ============================================================================
// PROGRESS TRACKING - Roadmap Indicators
// ============================================================================

/**
 * Load progress data from backend and update UI
 */
async function loadProgressData() {
    try {
        const response = await fetch('/api/progress');
        
        if (!response.ok) {
            console.log('Progress data not available');
            return;
        }
        
        const data = await response.json();
        const progressByModule = data.modules || {};
        
        // Update progress bars for all subject cards
        updateSubjectProgressBars(progressByModule);
        
        // Store for use when rendering tree
        window.progressData = progressByModule;
        
    } catch (error) {
        console.log('Could not load progress:', error);
        // Continue without progress data
    }
}

/**
 * Update progress bar width and percentage text for each subject
 */
function updateSubjectProgressBars(progressByModule) {
    const subjects = ['mathematics', 'aiml', 'programming_c'];
    
    subjects.forEach(subject => {
        const card = document.querySelector(`.subject-card[data-subject="${subject}"]`);
        if (!card) return;
        
        // Count completed modules for this subject
        const completedCount = Object.values(progressByModule).filter(prog => 
            prog.subject === subject && prog.status === 'completed'
        ).length;
        
        // Need to know total modules (we'll get from curriculum later)
        // For now, we'll calculate percentage when subject is loaded
        
        // Update fill width (placeholder, will be updated in renderTree)
        const fillEl = card.querySelector('.progress-bar .fill');
        if (fillEl) {
            fillEl.dataset.subject = subject;
            fillEl.dataset.completed = completedCount;
        }
    });
}

/**
 * Calculate and display percentage for a specific subject
 */
function updateSubjectPercentage(subject, totalModules) {
    const card = document.querySelector(`.subject-card[data-subject="${subject}"]`);
    if (!card) return;
    
    const progressByModule = window.progressData || {};
    const completedCount = Object.values(progressByModule).filter(prog => 
        prog.subject === subject && prog.status === 'completed'
    ).length;
    
    const percentage = totalModules > 0 ? Math.round((completedCount / totalModules) * 100) : 0;
    
    const fillEl = card.querySelector('.progress-bar .fill');
    if (fillEl) {
        fillEl.style.width = percentage + '%';
    }
    
    const label = card.querySelector('.progress-label');
    if (label) {
        label.textContent = `${completedCount}/${totalModules} (${percentage}%)`;
    }
}
```

---

### Change 1.3: Load Progress When Subject is Selected (in loadSubjectTree)

**Replace the `loadSubjectTree` function (lines 31-49)** with:

```javascript
async function loadSubjectTree(subject) {
    currentSubject = subject;

    try {
        // Fetch the RICH CONTENT curriculum directly
        const response = await fetch(`${subject}_curriculum.json`);
        if (!response.ok) throw new Error('Failed to load curriculum');

        const data = await response.json();
        
        // Calculate total modules
        let totalModules = 0;
        Object.values(data.levels).forEach(level => {
            if (level.modules) totalModules += level.modules.length;
        });
        
        // Update progress bar with percentage
        updateSubjectPercentage(subject, totalModules);
        
        // Render the tree with progress data
        renderTree(data);

        // Switch views
        document.getElementById('subjectSelection').style.display = 'none';
        document.getElementById('roadmapDisplay').style.display = 'block';
        document.getElementById('roadmapTitle').textContent = formatSubjectName(subject) + " Roadmap";

    } catch (error) {
        console.error(error);
        alert("Error loading roadmap data. Ensure servers are running.");
    }
}
```

---

### Change 1.4: Mark Completed Modules (in renderTree)

**Replace the `renderTree` function (lines 51-72)** with:

```javascript
function renderTree(data) {
    const levels = ['beginner', 'intermediate', 'advanced'];
    const progressByModule = window.progressData || {};

    levels.forEach(level => {
        const container = document.getElementById(`${level}Nodes`);
        container.innerHTML = ''; // Clear previous

        if (data.levels[level] && data.levels[level].modules) {
            data.levels[level].modules.forEach(mod => {
                const node = document.createElement('div');
                node.className = 'node-chip';
                
                // Check if module is completed
                const moduleProgress = progressByModule[mod.module_id];
                const isCompleted = moduleProgress && moduleProgress.status === 'completed';
                
                if (isCompleted) {
                    node.classList.add('completed');
                }
                
                // Build inner HTML with conditional checkmark
                const checkmark = isCompleted ? '<i class="fas fa-check-circle completed-badge"></i>' : '<i class="fas fa-circle"></i>';
                node.innerHTML = `${checkmark} ${mod.module_header?.module_title || mod.module_name || 'Module'}`;

                node.addEventListener('click', () => {
                    goToModule(mod.module_id, level);
                });

                container.appendChild(node);
            });
        }
    });
}
```

---

## File 2: frontend/roadmap.html

### Change 2.1: Update Subject Card Structure

**Modify each `.subject-card` div to include progress label**

Find and replace the three subject cards:

```html
                <div class="subject-card" data-subject="mathematics">
                    <div class="card-icon math-bg"><i class="fas fa-square-root-alt"></i></div>
                    <h3>Mathematics</h3>
                    <p>The Language of the Universe. From Calculus to optimization.</p>
                    <div class="progress-bar">
                        <div class="fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-label">0/0 (0%)</div>
                </div>
                
                <div class="subject-card" data-subject="aiml">
                    <div class="card-icon ai-bg"><i class="fas fa-brain"></i></div>
                    <h3>AI & Machine Learning</h3>
                    <p>From Intuition to Cost Functions. Build intelligence.</p>
                    <div class="progress-bar">
                        <div class="fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-label">0/0 (0%)</div>
                </div>
                
                <div class="subject-card" data-subject="programming_c">
                    <div class="card-icon c-bg"><i class="fas fa-code"></i></div>
                    <h3>System Programming (C)</h3>
                    <p>Master the machine. Memory, Pointers, and OS fundamentals.</p>
                    <div class="progress-bar">
                        <div class="fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-label">0/0 (0%)</div>
                </div>
```

---

## File 3: Minimal CSS (roadmap.css)

**Add at the end of `frontend/css/roadmap.css`**:

```css
/* ============================================================================
   PROGRESS TRACKING - Roadmap Indicators
   ============================================================================ */

/* Progress bar styling */
.progress-bar {
    width: 100%;
    height: 8px;
    background: #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
    margin: 12px 0 6px 0;
}

.progress-bar .fill {
    height: 100%;
    background: linear-gradient(90deg, #10b981, #059669);
    border-radius: 4px;
    transition: width 0.3s ease;
    width: 0%;
}

/* Progress percentage label */
.progress-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-align: center;
    font-weight: 500;
}

/* Module chip styling - completed state */
.node-chip {
    position: relative;
    padding: 10px 16px;
    border-radius: 8px;
    background: #f3f4f6;
    border: 2px solid #d1d5db;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    color: #374151;
}

.node-chip:hover {
    background: #e5e7eb;
    border-color: #9ca3af;
}

/* Completed module styling */
.node-chip.completed {
    background: #dcfce7;
    border-color: #22c55e;
    color: #166534;
}

.node-chip.completed:hover {
    background: #bbf7d0;
    border-color: #16a34a;
}

/* Green checkmark icon for completed modules */
.node-chip .completed-badge {
    color: #22c55e;
    font-size: 1.1rem;
}

/* Regular circle icon */
.node-chip i.fas.fa-circle {
    font-size: 0.6rem;
    color: #9ca3af;
}

.node-chip.completed i.fas.fa-circle {
    display: none;
}
```

---

## Summary of Changes

### roadmap.js
- **Line 7:** Added `loadProgressData();` call
- **Lines 28-96:** Added 3 new functions:
  - `loadProgressData()` — Fetch progress from backend
  - `updateSubjectProgressBars()` — Update fill widths
  - `updateSubjectPercentage()` — Calculate and display percentage
- **Lines 98-115:** Modified `loadSubjectTree()` to calculate total modules and update progress
- **Lines 117-150:** Modified `renderTree()` to mark completed modules with checkmarks

### roadmap.html
- **Lines 22, 33, 44:** Added `<div class="progress-label">0/0 (0%)</div>` to each subject card

### roadmap.css (NEW)
- Added 7 CSS rules for progress bars, labels, and completed module styling

---

## What This Does

### On Page Load:
1. `loadProgressData()` fetches GET /api/progress
2. Stores progress in `window.progressData`
3. Updates progress bars on subject cards (empty until subject selected)

### When Subject Selected:
1. `loadSubjectTree()` counts total modules
2. `updateSubjectPercentage()` calculates: completed / total * 100
3. Updates progress bar width and label (e.g., "5/10 (50%)")
4. `renderTree()` marks each completed module with green checkmark

### Visual Indicators:
- **Progress Bar:** Green bar filling up to percentage on subject cards
- **Progress Label:** "X/Y (Z%)" format below progress bar
- **Green Checkmark:** ✓ icon on completed module chips
- **Green Background:** Light green background on completed module chips

---

## Testing

```powershell
# 1. Have backend running with some progress data
python backend/app.py

# 2. Open roadmap page
# Browser: http://localhost:8000/frontend/roadmap.html

# 3. Verify:
# - Progress bars are visible on subject cards (should be 0% initially)
# - Click a subject
# - Progress bar should update with percentage
# - Completed modules should show green checkmark
# - Background should be green for completed modules
```

---

