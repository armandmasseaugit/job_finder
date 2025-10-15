// Job Finder Modern Frontend JavaScript

// Global state management
const appState = {
    currentPage: 'home',
    userData: {
        totalJobs: 0,
        likedJobs: 0,
        dislikedJobs: 0
    }
};

// Page content templates
const pageTemplates = {
    home: `
        <div class="fade-in">
            <!-- Hero Section -->
            <div class="text-center mb-12">
                <div class="mx-auto w-32 h-32 mb-6 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                    <i class="fas fa-robot text-4xl text-white"></i>
                </div>
                <h1 class="text-4xl font-bold text-gray-900 mb-4">
                    👋 Hi, I'm <span class="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">JobBot!</span>
                </h1>
                <p class="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
                    Your AI-powered career companion. I'll help you discover amazing job opportunities that match your skills and aspirations.
                </p>
            </div>
            
            <!-- Stats Dashboard -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
                    <div class="flex items-center">
                        <div class="bg-blue-100 p-3 rounded-full mr-4">
                            <i class="fas fa-briefcase text-xl text-blue-600"></i>
                        </div>
                        <div>
                            <h3 class="text-2xl font-bold text-gray-900" id="total-jobs">${appState.userData.totalJobs}</h3>
                            <p class="text-gray-600">Total Job Offers</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
                    <div class="flex items-center">
                        <div class="bg-green-100 p-3 rounded-full mr-4">
                            <i class="fas fa-heart text-xl text-green-600"></i>
                        </div>
                        <div>
                            <h3 class="text-2xl font-bold text-gray-900" id="liked-jobs">${appState.userData.likedJobs}</h3>
                            <p class="text-gray-600">Jobs You Liked</p>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
                    <div class="flex items-center">
                        <div class="bg-red-100 p-3 rounded-full mr-4">
                            <i class="fas fa-thumbs-down text-xl text-red-600"></i>
                        </div>
                        <div>
                            <h3 class="text-2xl font-bold text-gray-900" id="disliked-jobs">${appState.userData.dislikedJobs}</h3>
                            <p class="text-gray-600">Jobs You Passed</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-xl p-8 text-white transform hover:scale-105 transition-all duration-300">
                    <div class="flex items-center mb-4">
                        <i class="fas fa-search text-3xl mr-4"></i>
                        <h3 class="text-2xl font-bold">Explore Job Offers</h3>
                    </div>
                    <p class="text-blue-100 mb-6">
                        Discover fresh opportunities from top companies. Filter by date, location, and relevance to find your perfect match.
                    </p>
                    <button onclick="navigateTo('explore')" 
                            class="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                        <i class="fas fa-arrow-right mr-2"></i>Start Exploring
                    </button>
                </div>
                
                <div class="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-xl p-8 text-white transform hover:scale-105 transition-all duration-300">
                    <div class="flex items-center mb-4">
                        <i class="fas fa-file-user text-3xl mr-4"></i>
                        <h3 class="text-2xl font-bold">AI CV Matching</h3>
                        <span class="bg-yellow-400 text-yellow-900 text-xs px-2 py-1 rounded-full ml-2">NEW!</span>
                    </div>
                    <p class="text-green-100 mb-6">
                        Upload your CV and let our advanced AI analyze your profile to find the top 5 jobs that match your skills perfectly.
                    </p>
                    <button onclick="navigateTo('cv-match')" 
                            class="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors">
                        <i class="fas fa-upload mr-2"></i>Upload CV
                    </button>
                </div>
            </div>
            
            <!-- Recent Activity -->
            <div class="mt-12">
                <h2 class="text-2xl font-bold text-gray-900 mb-6">
                    <i class="fas fa-clock text-blue-600 mr-2"></i>Recent Activity
                </h2>
                <div class="bg-white rounded-xl shadow-lg p-6" id="recent-activity">
                    <div class="text-center py-8 text-gray-500">
                        <i class="fas fa-history text-4xl mb-4"></i>
                        <p>No recent activity yet. Start exploring jobs to see your activity here!</p>
                    </div>
                </div>
            </div>
        </div>
    `,
    
    explore: `
        <div class="fade-in">
            <div class="flex justify-between items-center mb-8">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">
                        <i class="fas fa-search text-blue-600 mr-3"></i>Explore Job Offers
                    </h1>
                    <p class="text-gray-600 mt-2">Discover your next career opportunity</p>
                </div>
                <button onclick="navigateTo('home')" 
                        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                    <i class="fas fa-home mr-2"></i>Back to Home
                </button>
            </div>

            <!-- Filters -->
            <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Search</label>
                        <input 
                            type="text" 
                            id="job-search"
                            placeholder="Job title or company..."
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            onchange="filterJobs()"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Sort by</label>
                        <select 
                            id="job-sort"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            onchange="filterJobs()"
                        >
                            <option value="date">Publication Date</option>
                            <option value="relevance">Relevance Score</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Date from</label>
                        <input 
                            type="date" 
                            id="job-date"
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            onchange="filterJobs()"
                        >
                    </div>
                    <div class="flex items-end">
                        <button 
                            onclick="loadJobOffers()"
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
                            <i class="fas fa-search mr-2"></i>Refresh Jobs
                        </button>
                    </div>
                </div>
            </div>

            <!-- Jobs Container -->
            <div id="jobs-container">
                <div class="bg-white rounded-xl shadow-lg p-8 text-center">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
                    <p class="text-gray-500">Loading job offers...</p>
                </div>
            </div>
        </div>
    `,
    cvMatch: null  // Will be loaded from cv_matching.html
};

// Navigation function
async function navigateTo(page) {
    try {
        // Update app state
        appState.currentPage = page;
        
        // Update URL without page reload
        history.pushState({ page }, '', `#${page}`);
        
        // Load page content
        let content;
        
        if (page === 'home') {
            content = pageTemplates.home;
        } else if (page === 'explore') {
            content = pageTemplates.explore;
            // Load jobs after page renders
            setTimeout(() => loadJobOffers(), 100);
        } else if (page === 'cv-match') {
            if (!pageTemplates.cvMatch) {
                const response = await fetch('/cv-match');
                pageTemplates.cvMatch = await response.text();
            }
            content = pageTemplates.cvMatch;
        } else {
            content = pageTemplates.home; // Default fallback
        }
        
        // Update main content
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = content;
            
            // Re-process HTMX elements
            if (typeof htmx !== 'undefined') {
                htmx.process(mainContent);
            }
            
            // Re-initialize Alpine.js components
            if (typeof Alpine !== 'undefined') {
                Alpine.initTree(mainContent);
            }
        }
        
        // Update navigation active state
        updateNavigation(page);
        
    } catch (error) {
        console.error('Navigation error:', error);
        // Fallback to home page
        document.getElementById('main-content').innerHTML = pageTemplates.home;
    }
}

// Update navigation active states
function updateNavigation(currentPage) {
    const navButtons = document.querySelectorAll('[data-nav]');
    navButtons.forEach(button => {
        const page = button.getAttribute('data-nav');
        if (page === currentPage) {
            button.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
            button.classList.remove('text-gray-500');
        } else {
            button.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
            button.classList.add('text-gray-500');
        }
    });
}

// Load user stats from API
async function loadUserStats() {
    try {
        const response = await fetch('http://localhost:8000/stats');
        if (response.ok) {
            const stats = await response.json();
            appState.userData = {
                totalJobs: stats.total_jobs || 0,
                likedJobs: stats.liked_jobs || 0,
                dislikedJobs: stats.disliked_jobs || 0
            };
            
            // Update UI if on home page
            if (appState.currentPage === 'home') {
                const totalElement = document.getElementById('total-jobs');
                const likedElement = document.getElementById('liked-jobs');
                const dislikedElement = document.getElementById('disliked-jobs');
                
                if (totalElement) totalElement.textContent = appState.userData.totalJobs;
                if (likedElement) likedElement.textContent = appState.userData.likedJobs;
                if (dislikedElement) dislikedElement.textContent = appState.userData.dislikedJobs;
            }
        }
    } catch (error) {
        console.error('Error loading user stats:', error);
    }
}

// Handle browser back/forward buttons
window.addEventListener('popstate', (event) => {
    const page = event.state?.page || 'home';
    navigateTo(page);
});

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check URL for initial page
    const hash = window.location.hash.slice(1);
    const initialPage = hash || 'home';
    
    // Load initial page
    navigateTo(initialPage);
    
    // Load user stats
    loadUserStats();
    
    // Setup navigation event listeners
    document.addEventListener('click', (event) => {
        const target = event.target.closest('[data-nav]');
        if (target) {
            event.preventDefault();
            const page = target.getAttribute('data-nav');
            navigateTo(page);
        }
    });
    
    // Auto-refresh stats every 30 seconds
    setInterval(loadUserStats, 30000);
});

// Utility functions for HTMX responses
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// HTMX event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Handle HTMX responses
    document.body.addEventListener('htmx:responseError', function(event) {
        showNotification('Something went wrong. Please try again.', 'error');
    });
    
    document.body.addEventListener('htmx:afterRequest', function(event) {
        if (event.detail.successful) {
            // Refresh stats after successful like/dislike
            if (event.detail.pathInfo.requestPath.includes('/likes/')) {
                loadUserStats();
                showNotification('Feedback recorded!', 'success');
            }
        }
    });
});

// Job management functions
let currentJobs = [];

async function loadJobOffers() {
    try {
        console.log('🔍 Starting loadJobOffers function...');
        
        const container = document.getElementById('jobs-container');
        if (!container) {
            console.error('❌ jobs-container element not found!');
            return;
        }
        
        console.log('✅ Container found, showing loading state...');
        
        // Show loading
        container.innerHTML = `
            <div class="bg-white rounded-xl shadow-lg p-8 text-center">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
                <p class="text-gray-500">Loading job offers...</p>
            </div>
        `;
        
        // Get filter values
        const search = document.getElementById('job-search')?.value || '';
        const sortBy = document.getElementById('job-sort')?.value || 'date';
        const dateFilter = document.getElementById('job-date')?.value || '';
        
        console.log('📊 Filter values:', { search, sortBy, dateFilter });
        
        // Build API URL with filters
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (sortBy) params.append('sort_by', sortBy);
        if (dateFilter) params.append('date_filter', dateFilter);
        
        const apiUrl = `http://localhost:8000/offers?${params.toString()}`;
        console.log('🌐 Making API call to:', apiUrl);
        
        const response = await fetch(apiUrl);
        
        console.log('📡 Response status:', response.status);
        console.log('📡 Response ok:', response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        console.log('📥 Parsing JSON response...');
        const jobs = await response.json();
        console.log('✅ Jobs received:', jobs.length);
        
        currentJobs = jobs;
        
        displayJobs(jobs);
        
    } catch (error) {
        console.error('❌ Error in loadJobOffers:', error);
        const container = document.getElementById('jobs-container');
        if (container) {
            container.innerHTML = `
                <div class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
                    <i class="fas fa-exclamation-triangle text-red-500 text-2xl mb-3"></i>
                    <h3 class="text-lg font-semibold text-red-700 mb-2">Error loading jobs</h3>
                    <p class="text-red-600">Failed to load job offers: ${error.message}</p>
                    <button onclick="loadJobOffers()" class="mt-4 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors">
                        <i class="fas fa-refresh mr-2"></i>Retry
                    </button>
                </div>
            `;
        }
    }
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-container');
    if (!container) return;
    
    if (jobs.length === 0) {
        container.innerHTML = `
            <div class="bg-white rounded-xl shadow-lg p-8 text-center">
                <i class="fas fa-search text-gray-400 text-4xl mb-4"></i>
                <h3 class="text-xl font-semibold text-gray-700 mb-2">No jobs found</h3>
                <p class="text-gray-500">Try adjusting your filters or search terms.</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="mb-6 text-center">
            <p class="text-blue-800 bg-blue-50 inline-block px-4 py-2 rounded-lg">
                <i class="fas fa-briefcase mr-2"></i>Displaying ${jobs.length} job offers
            </p>
        </div>
        <div class="space-y-6">
    `;
    
    jobs.forEach(job => {
        const relevanceScore = job.relevance_score || 0;
        const scoreClass = relevanceScore > 7 ? 'bg-green-100 text-green-800' : 
                          relevanceScore > 5 ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-blue-100 text-blue-800';
        const remoteIcon = job.remote === 'full_remote' ? 'fa-home' : 
                          job.remote === 'hybrid' || job.remote === 'partial' ? 'fa-building' : 'fa-map-marker-alt';
        const remoteText = job.remote === 'full_remote' ? 'Full Remote' :
                          job.remote === 'hybrid' || job.remote === 'partial' ? 'Hybrid' :
                          job.remote === 'no' ? 'On-site' : job.remote || 'Unknown';
        
        html += `
            <div class="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow border border-gray-100">
                <div class="flex justify-between items-start mb-4">
                    <div class="flex-1">
                        <div class="flex items-center mb-3">
                            <img src="${job.logo_url || 'https://via.placeholder.com/48x48/3B82F6/FFFFFF?text=?'}" 
                                 alt="${job.company_name} logo" 
                                 class="w-12 h-12 rounded-lg mr-4 object-cover"
                                 onerror="this.src='https://via.placeholder.com/48x48/3B82F6/FFFFFF?text=${(job.company_name || 'C')[0]}'">
                            <div>
                                <h3 class="text-xl font-semibold text-gray-900">${job.name || 'No title'}</h3>
                                <p class="text-blue-600 font-medium">${job.company_name || 'Unknown Company'}</p>
                            </div>
                        </div>
                        
                        <div class="flex flex-wrap items-center text-gray-600 text-sm space-x-4 mb-3">
                            <div class="flex items-center">
                                <i class="fas ${remoteIcon} mr-2"></i>
                                <span>${job.city || 'Remote'} • ${remoteText}</span>
                            </div>
                            <div class="flex items-center">
                                <i class="fas fa-calendar mr-2"></i>
                                <span>Published: ${job.publication_date || 'Unknown'}</span>
                            </div>
                        </div>
                        
                        ${job.description_preview ? `
                            <p class="text-gray-700 text-sm leading-relaxed">${job.description_preview.substring(0, 200)}${job.description_preview.length > 200 ? '...' : ''}</p>
                        ` : ''}
                    </div>
                    
                    <div class="flex flex-col items-end space-y-3 ml-6">
                        <div class="${scoreClass} px-3 py-1 rounded-full text-sm font-medium">
                            Score: ${relevanceScore.toFixed(1)}
                        </div>
                        <div class="flex space-x-2">
                            <button class="bg-green-100 hover:bg-green-200 text-green-600 p-2 rounded-lg transition-colors"
                                    onclick="likeJob('${job.reference}', 'like')"
                                    title="Like this job">
                                <i class="fas fa-heart"></i>
                            </button>
                            <button class="bg-red-100 hover:bg-red-200 text-red-600 p-2 rounded-lg transition-colors"
                                    onclick="likeJob('${job.reference}', 'dislike')"
                                    title="Dislike this job">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="flex justify-between items-center pt-4 border-t border-gray-100">
                    <a href="${job.url || '#'}" 
                       target="_blank"
                       class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium">
                        <i class="fas fa-external-link-alt mr-2"></i>View Job
                    </a>
                    <span class="text-xs text-gray-500">Ref: ${job.reference || 'N/A'}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function filterJobs() {
    if (currentJobs.length > 0) {
        loadJobOffers(); // Reload with new filters
    }
}

async function likeJob(jobRef, feedback) {
    try {
        const response = await fetch(`http://localhost:8000/likes/${jobRef}?feedback=${feedback}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification(`Job ${feedback === 'like' ? 'liked' : 'disliked'}!`, 'success');
            loadUserStats(); // Refresh stats
        } else {
            showNotification('Failed to save feedback', 'error');
        }
    } catch (error) {
        console.error('Error liking job:', error);
        showNotification('Error saving feedback', 'error');
    }
}

// Export functions for global access
window.jobFinderApp = {
    navigateTo,
    loadUserStats,
    showNotification,
    loadJobOffers,
    likeJob,
    appState
};