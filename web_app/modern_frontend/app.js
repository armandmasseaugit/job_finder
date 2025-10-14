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
    
    explore: null, // Will be loaded from explore.html
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
            if (!pageTemplates.explore) {
                const response = await fetch('/web_app/modern_frontend/explore.html');
                pageTemplates.explore = await response.text();
            }
            content = pageTemplates.explore;
        } else if (page === 'cv-match') {
            if (!pageTemplates.cvMatch) {
                const response = await fetch('/web_app/modern_frontend/cv_matching.html');
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

// Export functions for global access
window.jobFinderApp = {
    navigateTo,
    loadUserStats,
    showNotification,
    appState
};