// Quiz Logic - Works with NEW JSON schema
// Reads quiz from module data directly (not separate quiz files)

let currentQuiz = null;

document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startQuizBtn');
    if (startBtn) {
        startBtn.addEventListener('click', loadQuiz);
    }

    document.getElementById('submitQuizBtn').addEventListener('click', submitQuiz);
    document.getElementById('retryQuizBtn').addEventListener('click', resetQuiz);
});

async function loadQuiz() {
    const moduleState = window.moduleState;
    if (!moduleState) {
        alert("Module not loaded yet. Please wait...");
        return;
    }

    const currentModule = moduleState.getCurrentModule();
    if (!currentModule || !currentModule.data) {
        alert("Please load a module first.");
        return;
    }

    // Get quiz from module data
    const quizData = currentModule.data.quiz;

    if (!quizData || quizData.length === 0) {
        alert("No quiz available for this module.");
        return;
    }

    // Show loading UI
    document.getElementById('startQuizBtn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';

    // Transform quiz format
    currentQuiz = {
        questions: quizData.map(q => ({
            question: q.question,
            options: q.options,
            correct: q.correct_answer,  // Index 0-3
            explanation: q.explanation,
            difficulty: 'General'  // Could add difficulty field to JSON schema if needed
        }))
    };

    renderQuiz(currentQuiz);

    // Track quiz start time for duration calculation
    window.quizStartTime = Date.now();

    // Hide start button, show quiz container
    document.querySelector('.quiz-hero').style.display = 'none';
    document.getElementById('quizContainer').style.display = 'block';
}

function renderQuiz(quiz) {
    const container = document.getElementById('quizQuestions');
    container.innerHTML = '';

    document.getElementById('quizScore').textContent = '';
    document.getElementById('submitQuizBtn').style.display = 'inline-block';
    document.getElementById('retryQuizBtn').style.display = 'none';
    document.getElementById('progressionMessage').style.display = 'none';

    quiz.questions.forEach((q, index) => {
        const card = document.createElement('div');
        card.className = 'question-card';
        card.dataset.id = index;

        // Difficulty Badge Colors
        let diffColor = '#6b7280'; // Default gray
        if (q.difficulty === 'Easy') diffColor = '#10b981';
        if (q.difficulty === 'Medium') diffColor = '#f59e0b';
        if (q.difficulty === 'Hard') diffColor = '#ef4444';

        const diffBadge = `<span style="background:${diffColor}; color:white; padding:2px 8px; border-radius:12px; font-size:0.75rem; margin-left:10px; font-weight:bold;">${q.difficulty || 'General'}</span>`;

        let optionsHtml = '';
        q.options.forEach((opt, optIndex) => {
            optionsHtml += `
                <label class="option-label">
                    <input type="radio" name="q${index}" value="${optIndex}" class="option-input">
                    ${opt}
                </label>
            `;
        });

        card.innerHTML = `
            <div class="question-header" style="margin-bottom:15px;">
                <span class="q-num">Q${index + 1}</span> ${diffBadge}
            </div>
            <div class="question-text">${q.question}</div>
            <div class="options-group">${optionsHtml}</div>
            <div class="feedback" style="display:none; margin-top:15px;"></div>
        `;

        container.appendChild(card);
    });

    // Re-render LaTeX if present in questions
    if (window.MathJax) {
        window.MathJax.typesetPromise();
    }
}

function submitQuiz() {
    if (!currentQuiz) return;

    let score = 0;
    let total = currentQuiz.questions.length;
    let unanswered = 0;

    // Grade each question
    currentQuiz.questions.forEach((q, index) => {
        const card = document.querySelector(`.question-card[data-id="${index}"]`);
        const selected = card.querySelector(`input[name="q${index}"]:checked`);
        const feedback = card.querySelector('.feedback');

        if (!selected) {
            unanswered++;
            return;
        }

        const userAns = parseInt(selected.value);
        feedback.style.display = 'block';

        // Disable inputs
        card.querySelectorAll('input').forEach(inp => inp.disabled = true);

        if (userAns === q.correct) {
            score++;
            card.querySelector(`input[value="${userAns}"]`).parentElement.classList.add('correct-answer');
            feedback.innerHTML = `
                <div class="explanation success-exp">
                    <strong><i class="fas fa-check"></i> Correct!</strong><br>
                    ${q.explanation || 'Great job!'}
                </div>`;
        } else {
            card.querySelector(`input[value="${userAns}"]`).parentElement.classList.add('wrong-answer');
            card.querySelector(`input[value="${q.correct}"]`).parentElement.classList.add('correct-answer');
            feedback.innerHTML = `
                <div class="explanation error-exp">
                    <strong><i class="fas fa-times"></i> Incorrect.</strong><br>
                    ${q.explanation || 'Review the topic concepts.'}
                </div>`;
        }
    });

    if (unanswered > 0) {
        alert(`Please answer all questions! (${unanswered} remaining)`);
        // Re-enable inputs
        currentQuiz.questions.forEach((q, index) => {
            const card = document.querySelector(`.question-card[data-id="${index}"]`);
            card.querySelectorAll('input').forEach(inp => inp.disabled = false);
        });
        return;
    }

    // Calculate final score
    const percentage = Math.round((score / total) * 100);
    document.getElementById('quizScore').textContent = `Score: ${percentage}%`;

    // UI Updates
    document.getElementById('submitQuizBtn').style.display = 'none';
    document.getElementById('retryQuizBtn').style.display = 'inline-block';

    // Handle Progression
    handleProgression(percentage);

    // Re-render MathJax in explanations
    if (window.MathJax) {
        window.MathJax.typesetPromise();
    }
}

async function handleProgression(score) {
    const currentModule = window.moduleState.getCurrentModule();
    const subject = currentModule.subject;
    const level = currentModule.level;
    const moduleId = currentModule.module_id;

    // Save Score
    let progress = JSON.parse(localStorage.getItem('userProgress') || '{}');
    if (!progress[subject]) progress[subject] = {};
    if (!progress[subject][level]) progress[subject][level] = {};
    const oldScore = progress[subject][level][moduleId] || 0;
    progress[subject][level][moduleId] = Math.max(oldScore, score);
    localStorage.setItem('userProgress', JSON.stringify(progress));

    // Save progress to backend
    saveProgressToBackend(score);

    // Message
    const msgDiv = document.getElementById('progressionMessage');
    msgDiv.style.display = 'block';

    if (score < 75) {
        msgDiv.className = 'progression-banner progression-review';
        msgDiv.innerHTML = `
            <h3><i class="fas fa-exclamation-triangle"></i> Review Needed</h3> 
            <p>You scored ${score}%. We recommend reviewing the <strong>Theory</strong> and <strong>Worked Examples</strong> sections before moving on.</p>
        `;
    } else {
        msgDiv.className = 'progression-banner progression-success';
        msgDiv.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Checking Level Completion...`;

        try {
            // Check Level Completion
            const response = await fetch(`${subject}_curriculum.json`);
            const data = await response.json();
            const modules = data.levels[level].modules;
            const userScores = progress[subject][level];

            const allPassed = modules.every(m => (userScores[m.module_id] || 0) >= 75);

            if (allPassed) {
                msgDiv.innerHTML = `
                    <h3><i class="fas fa-trophy"></i> LEVEL COMPLETE!</h3>
                    <p>You have mastered all modules in <strong>${level}</strong>!</p>
                    <a href="roadmap.html" class="premium-btn" style="display:inline-block; margin-top:10px; color:white; text-decoration:none;">Unlock Next Level</a>
                `;
            } else {
                msgDiv.innerHTML = `
                    <h3><i class="fas fa-check-circle"></i> Module Passed!</h3>
                    <p>Great work! You've mastered this concept.</p>
                    <a href="roadmap.html" class="premium-btn" style="display:inline-block; margin-top:10px; color:white; text-decoration:none;">Return to Roadmap</a>
                `;
            }
        } catch (e) {
            msgDiv.innerHTML = `
                <h3><i class="fas fa-check-circle"></i> Module Passed!</h3>
            `;
        }
    }
}

function resetQuiz() {
    document.querySelector('.quiz-hero').style.display = 'block';
    document.getElementById('quizContainer').style.display = 'none';
    document.getElementById('startQuizBtn').innerHTML = 'Start Interactive Quiz';
}

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
