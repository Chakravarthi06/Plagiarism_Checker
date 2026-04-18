/**
 * Plagiarism Checker Frontend Application
 * Connects to Flask Backend API
 */

const API_BASE_URL = 'http://localhost:5000/api';

class PlagiarismChecker {
    constructor() {
        this.currentMode = 'compare';
        this.analysisResults = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFromStorage();
        this.setupKeyboardShortcuts();
    }

    setupEventListeners() {
        // Mode toggle buttons
        document.getElementById('btnCompare').addEventListener('click', () => this.setMode('compare'));
        document.getElementById('btnSingle').addEventListener('click', () => this.setMode('single'));
    }

    setMode(mode) {
        this.currentMode = mode;
        
        // Update button states
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(mode === 'compare' ? 'btnCompare' : 'btnSingle').classList.add('active');
        
        const box2 = document.getElementById('box2');
        const inputSection = document.getElementById('inputSection');
        const label1 = document.getElementById('label1');
        
        if (mode === 'single') {
            box2.classList.add('hidden');
            InputSection.classList.add('single-mode');
            label1.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Enter Text to Analyze
            `;
        } else {
            box2.classList.remove('hidden');
            InputSection.classList.remove('single-mode');
            Label1.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Original Text
            `;
        }
        
        this.clearResults();
    }

    async handleFileUpload(input, targetId) {
        const file = input.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE_URL}/file-upload`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.content) {
                document.getElementById(targetId).value = data.content;
                this.showToast('File uploaded successfully', 'success');
            } else if (data.error) {
                this.showToast(data.error, 'error');
            } else {
                this.showToast('Error uploading file', 'error');
            }
        } catch (error) {
            this.showToast('Error reading file', 'error');
        }
    }

    clearAll() {
        document.getElementById('text1').value = '';
        document.getElementById('text2').value = '';
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('file1').value = '';
        document.getElementById('file2').value = '';
        this.AnalysisResults = null;
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = document.getElementById('toastIcon');
        
        toast.className = `toast toast-${type}`;
        toastMessage.textContent = message;
        toastIcon.textContent = type === 'success' ? '✓' : '✕';
        
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    updateProgress(percent) {
        document.getElementById('progressBar').style.width = percent + '%';
    }

    async checkPlagiarism() {
        const text1 = document.getElementById('text1').value.trim();
        const text2 = document.getElementById('text2').value.trim();
        
        if (!text1) {
            this.showToast('Please enter text to analyze', 'error');
            return;
        }
        
        if (this.currentMode === 'compare' && !text2) {
            this.showToast('Please enter both texts to compare', 'error');
            return;
        }
        
        // Show loading
        const loader = document.getElementById('loadingOverlay');
        loader.classList.add('active');
        
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            this.updateProgress(progress);
        }, 200);
        
        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text1: text1,
                    text2: this.currentMode === 'single' ? undefined : text2,
                    mode: this.currentMode
                })
            });

            clearInterval(progressInterval);
            this.updateProgress(100);
            
            if (!response.ok) {
                throw new Error('Analysis failed');
            }
            
            const results = await response.json();
            setTimeout(() => {
                loader.classList.remove('active');
                this.displayResults(results, text1, text2 || text1);
            }, 500);
            
        } catch (error) {
            clearInterval(progressInterval);
            loader.classList.remove('active');
            this.showToast('Error: ' + error.message, 'error');
            console.error('Analysis error:', error);
        }
    }

    displayResults(results, text1, text2) {
        this.AnalysisResults = results;
        
        // Update badge
        const badge = document.getElementById('similarityBadge');
        badge.textContent = results.similarity + '% Similar';
        badge.className = 'similarity-badge ' + 
            (results.similarity < 30 ? 'similarity-low' : 
             results.similarity < 70 ? 'similarity-medium' : 'similarity-high');
        
        // Update stats
        document.getElementById('statSimilarity').textContent = results.similarity + '%';
        document.getElementById('statMatches').textContent = results.matches?.length || 0;
        document.getElementById('statUnique').textContent = (100 - results.similarity) + '%';
        document.getElementById('statChars').textContent = results.metadata?.text1_length + results.metadata?.text2_length || 0;
        
        // Update highlighted text
        document.getElementById('highlightedText1').innerHTML = results.highlighted_text1 || this.highlightText(text1, results.matches || [], true);
        document.getElementById('highlightedText2').innerHTML = results.highlighted_text2 || this.highlightText(text2, results.matches || [], false);
        
        // Update matches list
        const matchesList = document.getElementById('matchesList');
        if (!results.matches || results.matches.length === 0) {
            matchesList.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No significant matches found. The texts appear to be original.</div>';
        } else {
            matchesList.innerHTML = results.matches.map((match, index) => `
                <div class="match-item">
                    <div class="match-content">
                        <div class="match-text">"${this.escapeHtml(match.text)}"</div>
                        <div class="match-meta">
                            <span>📏 ${match.length} words</span>
                            <span>🔍 Match #${index + 1}</span>
                        </div>
                    </div>
                    <div class="match-similarity">${match.similarity}%</div>
                </div>
            `).join('');
        }
        
        // Show results
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    highlightText(text, matches, isPrimary) {
        if (!matches || matches.length === 0) return text;
        
        let highlighted = text;
        const colorClass = isPrimary ? 'match-highlight' : 'unique-highlight';
        
        // Sort matches by length (longest first)
        const sortedMatches = [...matches].sort((a, b) => b.text.length - a.text.length);
        
        const usedRanges = [];
        
        sortedMatches.forEach(match => {
            const pattern = match.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(pattern, 'gi');
            let matchResult;
            
            while ((matchResult = regex.exec(highlighted)) !== null) {
                const start = matchResult.index;
                const end = start + matchResult[0].length;
                
                // Check for overlap
                const hasOverlap = usedRanges.some(r => (start < r.end && end > r.start));
                
                if (!hasOverlap) {
                    usedRanges.push({ start, end });
                    
                    const before = highlighted.substring(0, start);
                    const matched = highlighted.substring(start, end);
                    const after = highlighted.substring(end);
                    
                    highlighted = before + `<span class="${colorClass}" title="Match: ${match.similarity}% similarity">${matched}</span>` + after;
                    
                    regex.lastIndex = end + `<span class="${colorClass}" title="Match: ${match.similarity}% similarity">`.length + '</span>'.length;
                }
            }});
        
        return highlighted;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.checkPlagiarism();
            }
            if (e.ctrlKey && e.key === 'Delete') {
                this.clearAll();
            }
        });
    }

    loadFromStorage() {
        const saved1 = localStorage.getItem('plagiarism_text1');
        const saved2 = localStorage.getItem('plagiarism_text2');
        if (saved1) document.getElementById('text1').value = saved1;
        if (saved2) document.getElementById('text2').value = saved2;
    }

    clearResults() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    saveToStorage() {
        localStorage.setItem('plagiarism_text1', document.getElementById('text1').value);
        localStorage.setItem('plagiarism_text2', document.getElementById('text2').value);
    }
}

// Initialize application
const app = new PlagiarismChecker();

// Auto-save every 5 seconds
setInterval(() => {
    app.saveToStorage();
}, 5000);

// Expose to window for HTML onclick handlers
window.setMode = (mode) => app.setMode(mode);
window.handleFileUpload = (input, targetId) => app.handleFileUpload(input, targetId);
window.checkPlagiarism = () => app.checkPlagiarism();
window.ClearAll = () => app.clearAll();