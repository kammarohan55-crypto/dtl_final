// Module Loading Logic - Works with NEW JSON schema
// Loads full module content from modules/{subject}/{level}/{module_id}.json

let currentModuleData = null;

document.addEventListener('DOMContentLoaded', () => {
    initModule();
});

async function initModule() {
    // 1. Check LocalStorage for module selection
    const subject = localStorage.getItem('selectedSubject');
    const level = localStorage.getItem('selectedLevel');
    const moduleId = localStorage.getItem('selectedModuleId');

    if (!subject || !level || !moduleId) {
        alert("No module selected. Redirecting to Roadmap.");
        window.location.href = 'roadmap.html';
        return;
    }

    // 2. Load from CURRICULUM JSON file (not individual module files)
    try {
        const curriculumPath = `${subject}_curriculum.json?v=${new Date().getTime()}`;
        const response = await fetch(curriculumPath);

        if (!response.ok) throw new Error(`Failed to load curriculum from ${curriculumPath}`);

        const curriculum = await response.json();

        // 3. Find the specific module in the curriculum
        const modules = curriculum.levels[level].modules;
        const moduleData = modules.find(m => m.module_id === moduleId);

        if (!moduleData) {
            throw new Error(`Module ${moduleId} not found in ${subject} ${level} level`);
        }

        currentModuleData = { ...moduleData, subject, level, module_id: moduleId };

        // 4. Render Module Content
        renderModule(currentModuleData);

    } catch (err) {
        console.error(err);
        document.getElementById('moduleName').textContent = "Error Loading Module";
        document.getElementById('moduleContent').innerHTML = `<p class="error">Failed to load content: ${err.message}. <a href="roadmap.html">Back</a></p>`;
        document.getElementById('moduleContent').style.display = 'block';
    }
}

function renderModule(data) {
    console.log('[DEBUG] renderModule called with:', data);
    window.debugModuleData = data;
    // Module Header
    const header = data.module_header;
    document.getElementById('moduleName').textContent = header.module_title;
    document.getElementById('moduleLevelBadge').textContent = header.level;

    // Definition as motivation
    document.getElementById('moduleMotivation').textContent = data.definition || "Master this fundamental concept.";

    // 1. Concept Overview (array of strings)
    const conceptDiv = document.getElementById('conceptContent');
    const concepts = data.concept_overview || [];
    conceptDiv.innerHTML = `<ul>${concepts.map(c => `<li>${c}</li>`).join('')}</ul>`;

    // 2. Intuition - Use THEORY section (comprehensive content)
    const theoryText = Array.isArray(data.theory) ? data.theory.join('\n\n') : data.theory || "";
    document.getElementById('intuitionContent').innerHTML = formatText(theoryText);

    // 2.5. Visual Learning Resources (YouTube Videos)
    const visualDiv = document.getElementById('visualContent');
    const visualSection = document.getElementById('visualResourcesSection');

    if (data.visual_learning_resources && data.visual_learning_resources.length > 0) {
        let videoHtml = '';
        data.visual_learning_resources.forEach(video => {
            videoHtml += `
                <div class="video-item">
                    <div class="video-icon"><i class="fab fa-youtube"></i></div>
                    <div class="video-info">
                        <h4><a href="${video.youtube_url}" target="_blank">${video.video_title} <i class="fas fa-external-link-alt" style="font-size: 0.8em; opacity: 0.7;"></i></a></h4>
                        <span class="channel-tag">${video.channel_name}</span>
                        <div class="video-reason">${video.short_reason}</div>
                    </div>
                </div>
            `;
        });
        visualDiv.innerHTML = videoHtml;
        visualSection.style.display = 'block';
    } else {
        visualSection.style.display = 'none';
    }

    // 3. Mathematical Formulation
    const mathDiv = document.getElementById('mathContent');
    if (data.mathematical_formulation && data.mathematical_formulation.length > 0) {
        let mathHtml = '';
        data.mathematical_formulation.forEach(item => {
            mathHtml += `
                <div class="formula-block">
                    <div class="formula">${item.formula}</div>
                    <div class="formula-explanation">${item.explanation}</div>
                </div>
            `;
        });
        mathDiv.innerHTML = mathHtml;
    } else {
        mathDiv.innerHTML = "<p>No mathematical formulation required for this topic.</p>";
    }

    // 4. Worked Examples
    const exDiv = document.getElementById('exampleContent');
    if (data.worked_examples && data.worked_examples.length > 0) {
        let exHtml = '';
        data.worked_examples.forEach((ex, idx) => {
            const steps = Array.isArray(ex.solution_steps) ? ex.solution_steps.join('<br>') : ex.solution_steps || "";
            exHtml += `
                <div class="example-block">
                    <div class="example-header">
                        <span class="difficulty-badge" style="background: ${getDifficultyColor(ex.difficulty)}">${ex.difficulty || 'General'}</span>
                        <strong>Example ${idx + 1}</strong>
                    </div>
                    <div class="problem"><strong>Problem:</strong> ${ex.problem}</div>
                    <div class="solution">
                        <strong>Solution:</strong><br>
                        ${formatText(steps)}
                    </div>
                    ${ex.final_answer ? `<div class="final-answer"><strong>Answer:</strong> ${ex.final_answer}</div>` : ''}
                </div>
            `;
        });
        exDiv.innerHTML = exHtml;
    } else {
        exDiv.innerHTML = "<p>No worked examples for this module.</p>";
    }

    // 5. Key Takeaways
    const takeDiv = document.getElementById('takeawaysContent');
    const takeaways = data.key_takeaways || [];
    takeDiv.innerHTML = `<ul>${takeaways.map(t => `<li>${t}</li>`).join('')}</ul>`;

    // Show Content
    document.getElementById('moduleContent').style.display = 'block';

    // TRIGGER MATHJAX rendering
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        window.MathJax.typesetPromise().catch(err => console.error('MathJax error:', err));
    }

    // Load and display progress from backend
    loadAndDisplayProgress(data.module_id);
}

function formatText(text) {
    if (!text) return '';

    // Convert arrays to text
    if (Array.isArray(text)) {
        text = text.join('\n\n');
    }

    // Basic formatting: newlines to <br>, bold markdown to <strong>
    let html = text
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Handle code blocks
    if (html.includes('```')) {
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    }

    return html;
}

function getDifficultyColor(difficulty) {
    if (!difficulty) return '#6b7280';
    if (difficulty.toLowerCase().includes('basic') || difficulty.toLowerCase().includes('easy')) return '#10b981';
    if (difficulty.toLowerCase().includes('intermediate') || difficulty.toLowerCase().includes('medium')) return '#f59e0b';
    if (difficulty.toLowerCase().includes('advanced') || difficulty.toLowerCase().includes('hard')) return '#ef4444';
    return '#6b7280';
}

// Export state for quiz and summary
window.moduleState = {
    getCurrentModule: () => {
        if (!currentModuleData) return null;
        return {
            subject: currentModuleData.subject,
            level: currentModuleData.level,
            module_id: currentModuleData.module_id,
            module_name: currentModuleData.module_header?.module_title || 'Unknown',
            data: currentModuleData  // Full module data for quiz/summary
        };
    }
};

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
