# ROADMAP PROGRESS INDICATORS - Exact Code to Paste

## Three Files, Three Edits

---

## File 1: frontend/js/roadmap.js

### Edit 1.1: Line 9
Replace:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    setupSubjectSelection();
    setupBackButton();
});
```

With:
```javascript
document.addEventListener('DOMContentLoaded', () => {
    setupSubjectSelection();
    setupBackButton();
    loadProgressData();  // Load progress from backend
});
```

---

### Edit 1.2: After line 26 (after setupBackButton closes)
Add entire block:

```javascript
// ============================================================================
// PROGRESS TRACKING - Roadmap Indicators
// ============================================================================

async function loadProgressData() {
    try {
        const response = await fetch('/api/progress');
        if (!response.ok) return;
        const data = await response.json();
        const progressByModule = data.modules || {};
        updateSubjectProgressBars(progressByModule);
        window.progressData = progressByModule;
    } catch (error) {
        console.log('Could not load progress:', error);
    }
}

function updateSubjectProgressBars(progressByModule) {
    const subjects = ['mathematics', 'aiml', 'programming_c'];
    subjects.forEach(subject => {
        const card = document.querySelector(`.subject-card[data-subject="${subject}"]`);
        if (!card) return;
        const completedCount = Object.values(progressByModule).filter(prog => 
            prog.subject === subject && prog.status === 'completed'
        ).length;
        const fillEl = card.querySelector('.progress-bar .fill');
        if (fillEl) {
            fillEl.dataset.subject = subject;
            fillEl.dataset.completed = completedCount;
        }
    });
}

function updateSubjectPercentage(subject, totalModules) {
    const card = document.querySelector(`.subject-card[data-subject="${subject}"]`);
    if (!card) return;
    const progressByModule = window.progressData || {};
    const completedCount = Object.values(progressByModule).filter(prog => 
        prog.subject === subject && prog.status === 'completed'
    ).length;
    const percentage = totalModules > 0 ? Math.round((completedCount / totalModules) * 100) : 0;
    const fillEl = card.querySelector('.progress-bar .fill');
    if (fillEl) fillEl.style.width = percentage + '%';
    const label = card.querySelector('.progress-label');
    if (label) label.textContent = `${completedCount}/${totalModules} (${percentage}%)`;
}
```

---

### Edit 1.3: Replace loadSubjectTree function
Replace the entire function with:

```javascript
async function loadSubjectTree(subject) {
    currentSubject = subject;
    try {
        const response = await fetch(`${subject}_curriculum.json`);
        if (!response.ok) throw new Error('Failed to load curriculum');
        const data = await response.json();
        
        let totalModules = 0;
        Object.values(data.levels).forEach(level => {
            if (level.modules) totalModules += level.modules.length;
        });
        updateSubjectPercentage(subject, totalModules);
        renderTree(data);

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

### Edit 1.4: Replace renderTree function
Replace the entire function with:

```javascript
function renderTree(data) {
    const levels = ['beginner', 'intermediate', 'advanced'];
    const progressByModule = window.progressData || {};

    levels.forEach(level => {
        const container = document.getElementById(`${level}Nodes`);
        container.innerHTML = '';

        if (data.levels[level] && data.levels[level].modules) {
            data.levels[level].modules.forEach(mod => {
                const node = document.createElement('div');
                node.className = 'node-chip';
                
                const moduleProgress = progressByModule[mod.module_id];
                const isCompleted = moduleProgress && moduleProgress.status === 'completed';
                
                if (isCompleted) {
                    node.classList.add('completed');
                }
                
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

### Edit 2.1: In Subject Cards Section
Find the three `.subject-card` divs and add `<div class="progress-label">` after each `.progress-bar`:

For Mathematics (around line 22):
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
```

For AI & ML (around line 33):
```html
                <div class="subject-card" data-subject="aiml">
                    <div class="card-icon ai-bg"><i class="fas fa-brain"></i></div>
                    <h3>AI & Machine Learning</h3>
                    <p>From Intuition to Cost Functions. Build intelligence.</p>
                    <div class="progress-bar">
                        <div class="fill" style="width: 0%"></div>
                    </div>
                    <div class="progress-label">0/0 (0%)</div>
                </div>
```

For Programming C (around line 44):
```html
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

## File 3: frontend/css/roadmap.css

### Edit 3.1: At end of file
Add this CSS block:

```css
/* ============================================================================
   PROGRESS TRACKING - Roadmap Indicators
   ============================================================================ */

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

.progress-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-align: center;
    font-weight: 500;
}

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

.node-chip.completed {
    background: #dcfce7;
    border-color: #22c55e;
    color: #166534;
}

.node-chip.completed:hover {
    background: #bbf7d0;
    border-color: #16a34a;
}

.node-chip .completed-badge {
    color: #22c55e;
    font-size: 1.1rem;
}

.node-chip i.fas.fa-circle {
    font-size: 0.6rem;
    color: #9ca3af;
}

.node-chip.completed i.fas.fa-circle {
    display: none;
}
```

---

## Summary

| File | Lines | Changes |
|------|-------|---------|
| roadmap.js | 197 | 4 edits, +101 lines |
| roadmap.html | Updated | +3 divs (progress-label) |
| roadmap.css | 323 | +67 lines CSS |

---

## Test

```powershell
# Backend running
python backend/app.py

# Browser
# http://localhost/roadmap.html

# Expected:
# - Progress bars visible on subjects
# - Click subject → bars update with %
# - Completed modules: green + ✓
# - Incomplete modules: gray + ○
```

---

