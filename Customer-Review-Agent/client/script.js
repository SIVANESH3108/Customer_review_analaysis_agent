const API_URL = 'http://localhost:5000/api';
let sentimentChart = null;
let volumeChart = null;
let fullHistoryData = [];

// DOM Elements
const navLinks = document.querySelectorAll('.nav-links li');
const tabContents = document.querySelectorAll('.tab-content');
const reviewInput = document.getElementById('reviewInput');
const charCount = document.getElementById('charCount');
const clearBtn = document.getElementById('clearBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const fileUpload = document.getElementById('fileUpload');
const fileName = document.getElementById('fileName');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultsSection = document.getElementById('resultsSection');
const toastContainer = document.getElementById('toastContainer');
const historyTableBody = document.getElementById('historyTableBody');
const searchInput = document.getElementById('searchInput');
const deleteAllBtn = document.getElementById('deleteAllBtn');
const historyModal = document.getElementById('historyModal');
const modalBody = document.getElementById('modalBody');
const closeModalBtn = document.querySelector('.close-modal');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Auth Check
    const userId = localStorage.getItem('userId');
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }

    // Set welcome text if we want, or handle logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('userId');
            localStorage.removeItem('username');
            window.location.href = 'login.html';
        });
    }

    setupNavigation();
    setupInputListeners();
    loadDashboardStats();
    loadHistory();
});

function getAuthHeaders() {
    const userId = localStorage.getItem('userId');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userId}`
    };
}

// Navigation
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Remove active class from all
            navLinks.forEach(l => l.classList.remove('active'));
            tabContents.forEach(c => c.classList.add('hidden'));

            // Add active to clicked
            link.classList.add('active');
            const targetTab = link.getAttribute('data-tab');
            document.getElementById(targetTab).classList.remove('hidden');

            if (targetTab === 'dashboard-tab') {
                loadDashboardStats();
            } else if (targetTab === 'history-tab') {
                loadHistory();
            }
        });
    });
}

// Input Handlers
function setupInputListeners() {
    reviewInput.addEventListener('input', () => {
        charCount.textContent = `${reviewInput.value.length} characters`;
    });

    clearBtn.addEventListener('click', () => {
        reviewInput.value = '';
        charCount.textContent = '0 characters';
        fileUpload.value = '';
        fileName.textContent = 'No file chosen';
        resultsSection.classList.add('hidden');
    });

    fileUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            const reader = new FileReader();
            reader.onload = (e) => {
                reviewInput.value = e.target.result;
                charCount.textContent = `${reviewInput.value.length} characters`;
            };
            reader.readAsText(file);
        }
    });

    analyzeBtn.addEventListener('click', handleAnalyze);

    searchInput.addEventListener('input', (e) => {
        filterHistory(e.target.value);
    });

    deleteAllBtn.addEventListener('click', async () => {
        if (confirm("Are you sure you want to delete all your analysis history? This cannot be undone.")) {
            try {
                const res = await fetch(`${API_URL}/../analysis/all`, { 
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });
                if (res.ok) {
                    showToast('History cleared successfully', 'success');
                    loadHistory();
                }
            } catch (err) {
                showToast('Failed to clear history', 'error');
            }
        }
    });

    closeModalBtn.addEventListener('click', () => {
        historyModal.classList.remove('active');
    });
}

async function handleAnalyze() {
    const text = reviewInput.value.trim();
    if (!text) {
        showToast('Please enter or upload reviews first.', 'error');
        return;
    }

    loadingOverlay.classList.add('active');
    resultsSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ reviews: text })
        });

        const data = await response.json();

        if (!response.ok) throw new Error(data.error || 'Analysis failed');

        populateResults(data.analysis);
        showToast('Analysis complete!', 'success');
        resultsSection.classList.remove('hidden');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

function populateResults(analysis) {
    document.getElementById('resRating').innerHTML = `<i class="fa-solid fa-star"></i> <span>${analysis.rating || 'N/A'}</span>`;
    document.getElementById('resSummary').textContent = analysis.summary || 'No summary provided.';
    
    const sentimentEl = document.getElementById('resSentiment');
    sentimentEl.textContent = analysis.overall_sentiment || 'Unknown';
    sentimentEl.className = 'sentiment-text ' + (analysis.overall_sentiment ? analysis.overall_sentiment.toLowerCase() : '');

    document.getElementById('resPosPercent').textContent = analysis.positive_percentage || '0%';
    document.getElementById('resNeuPercent').textContent = analysis.neutral_percentage || '0%';
    document.getElementById('resNegPercent').textContent = analysis.negative_percentage || '0%';

    const posList = document.getElementById('resPosPoints');
    posList.innerHTML = '';
    if (analysis.positive_points) {
        analysis.positive_points.forEach(p => posList.innerHTML += `<li>${p}</li>`);
    }

    const negList = document.getElementById('resNegPoints');
    negList.innerHTML = '';
    if (analysis.top_complaints) {
        analysis.top_complaints.forEach(p => negList.innerHTML += `<li>${p}</li>`);
    }

    const keywordDiv = document.getElementById('resKeywords');
    keywordDiv.innerHTML = '';
    if (analysis.keywords) {
        analysis.keywords.forEach(k => keywordDiv.innerHTML += `<span class="tag">${k}</span>`);
    }

    document.getElementById('resBusinessRec').textContent = analysis.business_recommendation || '';
    const suggList = document.getElementById('resSuggestions');
    suggList.innerHTML = '';
    if (analysis.suggestions) {
        analysis.suggestions.forEach(s => suggList.innerHTML += `<li>${s}</li>`);
    }
}

// Dashboard
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_URL}/stats`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        if (data.stats) {
            updateDashboardUI(data.stats);
        }
    } catch (error) {
        console.error("Error loading stats", error);
    }
}

function updateDashboardUI(stats) {
    document.getElementById('statTotal').textContent = stats.total_analyses;
    document.getElementById('statAvgRating').textContent = stats.average_rating;
    document.getElementById('statPositive').textContent = stats.positive_reviews;
    document.getElementById('statNegative').textContent = stats.negative_reviews;

    const sentimentData = {
        labels: stats.sentiment_distribution.map(s => s.sentiment),
        data: stats.sentiment_distribution.map(s => s.count)
    };

    renderCharts(sentimentData, stats);
}

function renderCharts(sentimentData, stats) {
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Outfit', sans-serif";

    // Pie Chart
    const pieCtx = document.getElementById('sentimentPieChart').getContext('2d');
    if (sentimentChart) sentimentChart.destroy();
    
    sentimentChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: sentimentData.labels,
            datasets: [{
                data: sentimentData.data,
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b', '#3b82f6'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right' } }
        }
    });

    // Bar Chart
    const barCtx = document.getElementById('volumeBarChart').getContext('2d');
    if (volumeChart) volumeChart.destroy();
    
    volumeChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['Total Reviews', 'Positive', 'Negative'],
            datasets: [{
                label: 'Volume',
                data: [stats.total_analyses, stats.positive_reviews, stats.negative_reviews],
                backgroundColor: ['#6366f1', '#10b981', '#ef4444'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } }
        }
    });
}

// History
async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/history`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();
        if (data.history) {
            fullHistoryData = data.history;
            renderHistoryTable(fullHistoryData);
        }
    } catch (error) {
        console.error("Error loading history", error);
    }
}

function renderHistoryTable(data) {
    historyTableBody.innerHTML = '';
    data.forEach(record => {
        const date = new Date(record.created_at).toLocaleString();
        const sentiment = (record.sentiment || 'unknown').toLowerCase();
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${date}</td>
            <td><span class="sentiment-badge ${sentiment}">${record.sentiment}</span></td>
            <td><i class="fa-solid fa-star text-warning"></i> ${record.rating}</td>
            <td class="summary-cell">${record.summary}</td>
            <td>
                <button class="action-btn" onclick="viewRecord(${record.id})"><i class="fa-solid fa-eye"></i></button>
                <button class="action-btn delete-btn" onclick="deleteRecord(${record.id})"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        historyTableBody.appendChild(tr);
    });
}

function filterHistory(query) {
    const q = query.toLowerCase();
    const filtered = fullHistoryData.filter(r => 
        (r.summary && r.summary.toLowerCase().includes(q)) ||
        (r.sentiment && r.sentiment.toLowerCase().includes(q)) ||
        (r.customer_review && r.customer_review.toLowerCase().includes(q))
    );
    renderHistoryTable(filtered);
}

window.viewRecord = (id) => {
    const record = fullHistoryData.find(r => r.id === id);
    if (record) {
        modalBody.innerHTML = `
            <div class="summary-box">
                <h4>Original Reviews</h4>
                <p style="font-size: 0.9em; max-height: 150px; overflow-y: auto;">${record.customer_review}</p>
            </div>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h5>Rating</h5>
                    <h3 class="text-warning">${record.rating} <i class="fa-solid fa-star"></i></h3>
                </div>
                <div class="metric-card">
                    <h5>Sentiment</h5>
                    <h3 class="sentiment-text ${record.sentiment.toLowerCase()}">${record.sentiment}</h3>
                </div>
            </div>
            <div class="summary-box" style="margin-top: 1rem;">
                <h4>Summary</h4>
                <p>${record.summary}</p>
            </div>
            <div class="recommendation-box">
                <h4>Business Recommendation</h4>
                <p>${record.business_recommendation}</p>
            </div>
        `;
        historyModal.classList.add('active');
    }
};

window.deleteRecord = async (id) => {
    if (confirm("Delete this record?")) {
        try {
            const res = await fetch(`${API_URL}/../analysis/${id}`, { 
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            if (res.ok) {
                showToast('Record deleted', 'success');
                loadHistory();
            }
        } catch (err) {
            showToast('Failed to delete', 'error');
        }
    }
};

// UI Utils
function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-xmark';
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <p>${message}</p>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
