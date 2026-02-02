// Roadmap Tree Logic
// Reads directly from curriculum JSONs to ensure 100% sync with content

let currentSubject = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupSubjectSelection();
    setupBackButton();
    loadProgressData();  // Load progress from backend
});

function setupSubjectSelection() {
    const cards = document.querySelectorAll('.subject-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const subject = card.getAttribute('data-subject');
            loadSubjectTree(subject);
        });
    });
}

function setupBackButton() {
    document.getElementById('backBtn').addEventListener('click', () => {
        document.getElementById('roadmapDisplay').style.display = 'none';
        document.getElementById('subjectSelection').style.display = 'grid';
        document.querySelector('.main-header').scrollIntoView({ behavior: 'smooth' });
    });
}

// ============================================================================
// PROGRESS TRACKING - Roadmap Indicators
// ============================================================================

/**
 * Load progress data from backend and update UI for ALL subjects
 */
async function loadProgressData() {
    let progressByModule = {};

    // 1. Try to load from Backend
    try {
        const response = await fetch('/api/progress');
        if (response.ok) {
            const data = await response.json();
            progressByModule = data.modules || {};
        }
    } catch (error) {
        console.log('Could not load backend progress:', error);
    }

    // 2. Load from LocalStorage (Fallback/Sync)
    // Structure: { subject: { level: { moduleId: score } } }
    try {
        const localProgress = JSON.parse(localStorage.getItem('userProgress') || '{}');

        // Iterate through all subjects, levels, and modules in local storage
        Object.keys(localProgress).forEach(subject => {
            const levels = localProgress[subject];
            Object.keys(levels).forEach(level => {
                const modules = levels[level];
                Object.keys(modules).forEach(moduleId => {
                    const score = modules[moduleId];

                    // Determine status based on score
                    // If backend already has data, we only overwrite if local score is better (optional strategy)
                    // For now, we'll assume local is latest if backend is missing or if we want to ensure visibility

                    if (!progressByModule[moduleId]) {
                        progressByModule[moduleId] = {
                            status: score >= 75 ? 'completed' : 'in_progress',
                            best_score: score,
                            subject: subject
                        };
                    } else {
                        // If backend exists, ensure we reflect completion if local says so
                        if (score >= 75 && progressByModule[moduleId].status !== 'completed') {
                            progressByModule[moduleId].status = 'completed';
                            progressByModule[moduleId].best_score = Math.max(progressByModule[moduleId].best_score || 0, score);
                        }
                    }
                });
            });
        });

    } catch (e) {
        console.error("Error parsing local progress:", e);
    }

    // Store for use when rendering tree
    window.progressData = progressByModule;

    // Calculate and display progress for ALL subjects upfront
    await updateAllSubjectProgressBars();
}

/**
 * Calculate total modules for all subjects and update progress bars
 * This runs on page load so progress bars show correct data immediately
 */
async function updateAllSubjectProgressBars() {
    const subjects = ['mathematics', 'aiml', 'programming_c'];

    for (const subject of subjects) {
        try {
            // Fetch curriculum to get total module count
            const response = await fetch(`${subject}_curriculum.json`);
            if (!response.ok) continue;

            const curriculum = await response.json();

            // Count total modules for this subject
            let totalModules = 0;
            Object.values(curriculum.levels).forEach(level => {
                if (level.modules) totalModules += level.modules.length;
            });

            // Update progress bar with correct percentages
            updateSubjectPercentage(subject, totalModules);

        } catch (error) {
            console.log(`Failed to load progress for ${subject}:`, error);
        }
    }
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

function goToModule(moduleId, level) {
    // Save state so module.html knows what to load
    localStorage.setItem('selectedSubject', currentSubject);
    localStorage.setItem('selectedLevel', level);
    localStorage.setItem('selectedModuleId', moduleId);

    // Redirect
    window.location.href = 'module.html';
}

function formatSubjectName(slug) {
    if (slug === 'aiml') return 'AI & Machine Learning';
    if (slug === 'programming_c') return 'C Programming';
    return slug.charAt(0).toUpperCase() + slug.slice(1);
}
