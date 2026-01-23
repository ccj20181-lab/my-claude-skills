/**
 * 爆款选题分析 Dashboard Logic
 * Professional Edition
 *
 * Features:
 * - Robust error handling & recovery
 * - Relative path resolution for GitHub Pages
 * - Responsive Mobile/Desktop UI
 */

class ReportDashboard {
    constructor() {
        // State
        this.metadata = null;
        this.sidebarOpen = false;

        // UI References
        this.elements = {
            sidebar: document.getElementById('sidebar'),
            sidebarOverlay: document.getElementById('sidebarOverlay'),
            sidebarToggle: document.getElementById('sidebarToggle'),
            historyList: document.getElementById('historyList'),
            loadingState: document.getElementById('loadingState'),
            errorState: document.getElementById('errorState'),
            welcomeState: document.getElementById('welcomeState'),
            reportFrame: document.getElementById('reportFrame'),
            errorMessage: document.getElementById('errorMessage'),
            retryBtn: document.getElementById('retryBtn'),
            latestReportDate: document.getElementById('latestReportDate'),
            totalReportsCount: document.getElementById('totalReportsCount')
        };

        // Bind methods
        this.toggleSidebar = this.toggleSidebar.bind(this);
        this.closeSidebar = this.closeSidebar.bind(this);
        this.retryLoading = this.retryLoading.bind(this);

        this.init();
    }

    async init() {
        console.log('[Dashboard] 初始化...');
        this.attachEventListeners();
        await this.loadData();
    }

    attachEventListeners() {
        // Sidebar interactions
        if (this.elements.sidebarToggle) {
            this.elements.sidebarToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleSidebar();
            });
        }

        if (this.elements.sidebarOverlay) {
            this.elements.sidebarOverlay.addEventListener('click', this.closeSidebar);
        }

        // Retry button
        if (this.elements.retryBtn) {
            this.elements.retryBtn.addEventListener('click', this.retryLoading);
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024 && this.sidebarOpen) {
                this.closeSidebar(); // Reset state for desktop
            }
        });
    }

    toggleSidebar() {
        this.sidebarOpen = !this.sidebarOpen;
        if (this.sidebarOpen) {
            this.elements.sidebar.classList.remove('-translate-x-full');
            this.elements.sidebarOverlay.classList.remove('hidden');
        } else {
            this.elements.sidebar.classList.add('-translate-x-full');
            this.elements.sidebarOverlay.classList.add('hidden');
        }
    }

    closeSidebar() {
        this.sidebarOpen = false;
        this.elements.sidebar.classList.add('-translate-x-full');
        this.elements.sidebarOverlay.classList.add('hidden');
    }

    async loadData() {
        this.showLoading(true);
        this.showError(false);

        try {
            // Use relative path for GitHub Pages compatibility
            // ./data/metadata.json ensures it looks in the data folder relative to index.html
            const response = await fetch('./data/metadata.json');

            if (!response.ok) {
                throw new Error(`HTTP Error: ${response.status}`);
            }

            this.metadata = await response.json();
            this.renderDashboard();
            this.checkUrlParams();

        } catch (error) {
            console.error('[Dashboard] Data load failed:', error);
            this.showError(true, `无法加载数据配置 (${error.message})`);
        } finally {
            this.showLoading(false);
        }
    }

    retryLoading() {
        this.loadData();
    }

    renderDashboard() {
        if (!this.metadata) return;

        // Update Stats
        if (this.elements.latestReportDate) {
            this.elements.latestReportDate.textContent = this.formatDate(this.metadata.latest_report);
        }
        if (this.elements.totalReportsCount) {
            this.elements.totalReportsCount.textContent = `${this.metadata.total_reports || 0} 期`;
        }

        // Render History List
        this.renderHistoryList();
    }

    renderHistoryList() {
        const list = this.elements.historyList;
        list.innerHTML = ''; // Clear loading spinner

        if (!this.metadata.history || this.metadata.history.length === 0) {
            list.innerHTML = '<li class="px-4 py-3 text-sm text-slate-400 text-center">暂无历史报告</li>';
            return;
        }

        this.metadata.history.forEach(item => {
            const li = document.createElement('li');
            const isLatest = this.isLatest(item.filename);

            // Item styling
            const baseClass = "group flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 mx-2";
            const inactiveClass = "hover:bg-slate-50 text-slate-600";

            li.className = `${baseClass} ${inactiveClass}`;
            li.dataset.filename = item.filename;

            // Content
            li.innerHTML = `
                <div class="h-9 w-9 rounded-md bg-white border border-slate-200 flex items-center justify-center text-base shadow-sm group-hover:shadow transition-shadow shrink-0 icon-container">
                    ${isLatest ? '🔥' : '📄'}
                </div>
                <div class="flex-1 min-w-0">
                    <div class="flex justify-between items-baseline mb-0.5">
                        <span class="text-sm font-medium truncate">${item.date}</span>
                        ${isLatest ? '<span class="text-[10px] font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded ml-2">NEW</span>' : ''}
                    </div>
                    <div class="flex items-center justify-between text-xs text-slate-400">
                        <span class="truncate pr-2 max-w-[80px]">${item.top_topic || '数据分析'}</span>
                        <span>${this.formatNumber(item.total_notes)}条</span>
                    </div>
                </div>
            `;

            // Click Handler
            li.addEventListener('click', () => {
                this.loadReport(item.filename, item.date);
                this.setActiveItem(li);
                if (window.innerWidth < 1024) {
                    this.closeSidebar();
                }
            });

            list.appendChild(li);
        });
    }

    setActiveItem(activeLi) {
        // Reset all items
        const items = this.elements.historyList.querySelectorAll('li');
        items.forEach(el => {
            el.className = "group flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 mx-2 hover:bg-slate-50 text-slate-600";
            const icon = el.querySelector('.icon-container');
            if(icon) icon.className = "h-9 w-9 rounded-md bg-white border border-slate-200 flex items-center justify-center text-base shadow-sm group-hover:shadow transition-shadow shrink-0 icon-container";
        });

        // Set active styling
        activeClass = "bg-blue-50/80 text-blue-700 border border-blue-100/50";
        activeLi.className = "group flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-200 mx-2 bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-100";

        const activeIcon = activeLi.querySelector('.icon-container');
        if(activeIcon) {
            activeIcon.className = "h-9 w-9 rounded-md bg-white border border-blue-200 flex items-center justify-center text-base shadow-sm shrink-0 icon-container text-blue-600";
        }
    }

    checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const dateParam = urlParams.get('date');

        if (dateParam && this.metadata.history) {
            const report = this.metadata.history.find(h => h.date === dateParam);
            if (report) {
                // Find and click the list item to set active state
                const items = this.elements.historyList.querySelectorAll('li');
                for (let li of items) {
                    if (li.dataset.filename === report.filename) {
                        li.click();
                        return;
                    }
                }
                // Fallback if list item not found/rendered for some reason
                this.loadReport(report.filename, report.date);
            } else {
                this.showWelcome();
            }
        } else {
            this.showWelcome();
        }
    }

    loadReport(filename, date) {
        // Hide welcome, show iframe
        this.elements.welcomeState.classList.add('hidden');
        this.elements.reportFrame.classList.remove('hidden');

        // Ensure relative path
        // If filename is 'report-2023-01-01.html', it's in the same dir as index.html
        let src = filename;
        if (!src.startsWith('http') && !src.startsWith('/')) {
            src = './' + filename;
        }

        this.elements.reportFrame.src = src;

        // Update URL
        const url = new URL(window.location);
        url.searchParams.set('date', date);
        window.history.pushState({}, '', url);
    }

    showWelcome() {
        this.elements.reportFrame.classList.add('hidden');
        this.elements.welcomeState.classList.remove('hidden');
    }

    showLoading(isLoading) {
        if (isLoading) {
            this.elements.loadingState.classList.remove('hidden');
        } else {
            this.elements.loadingState.classList.add('hidden');
        }
    }

    showError(isError, msg = '') {
        if (isError) {
            this.elements.errorMessage.textContent = msg;
            this.elements.errorState.classList.remove('hidden');
            this.elements.welcomeState.classList.add('hidden');
            this.elements.reportFrame.classList.add('hidden');
        } else {
            this.elements.errorState.classList.add('hidden');
        }
    }

    // Helpers
    formatDate(filename) {
        if (!filename) return '-';
        // Extracts date from report-YYYY-MM-DD.html or just returns filename
        const match = filename.match(/(\d{4}-\d{2}-\d{2})/);
        return match ? match[1] : filename;
    }

    formatNumber(num) {
        if (!num) return '0';
        if (num >= 10000) return (num / 10000).toFixed(1) + 'w';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
        return num.toString();
    }

    isLatest(filename) {
        return this.metadata.latest_report === filename;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ReportDashboard();
});
