/**
 * 报告查看器 - Tailwind CSS 版
 *
 * 功能：
 * - 加载历史报告元数据
 * - 管理侧边栏导航
 * - 控制 iframe 内容切换
 * - 响应式交互
 *
 * By 猫娘工程师 幽浮喵 ฅ'ω'ฅ
 */

class ReportViewer {
    constructor() {
        this.metadata = null;
        this.currentReport = null;
        this.sidebarOpen = window.innerWidth >= 1024; // lg breakpoint

        // DOM Elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.reportFrame = document.getElementById('reportFrame');
        this.loadingState = document.getElementById('loadingState');
        this.welcomeState = document.getElementById('welcomeState');
        this.historyList = document.querySelector('.history-list');
    }

    async init() {
        console.log('[ReportViewer] 🚀 初始化中...');
        this.setupEventListeners();
        await this.loadData();
    }

    async loadData() {
        this.showLoading();
        try {
            await this.loadMetadata();
            this.renderHistoryList();

            // 如果有最新报告，自动加载
            if (this.metadata && this.metadata.latest_report) {
                // 检查 URL 参数是否有指定日期
                const urlParams = new URLSearchParams(window.location.search);
                const dateParam = urlParams.get('date');

                if (dateParam) {
                    const targetReport = this.metadata.history.find(h => h.date === dateParam);
                    if (targetReport) {
                        this.loadReport(targetReport.filename, targetReport.date);
                    } else {
                        this.showWelcome();
                    }
                } else {
                    // 默认显示欢迎页，用户点击左侧查看
                    this.showWelcome();
                }
            } else {
                this.showWelcome();
            }
        } catch (error) {
            console.error('[ReportViewer] ❌ 初始化失败:', error);
            this.showError('无法加载数据，请检查网络连接或稍后重试');
        }
    }

    setupEventListeners() {
        // 侧边栏切换
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => this.closeSidebar());
        }

        // 监听窗口大小变化
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024) {
                this.sidebarOverlay.classList.add('hidden');
                this.sidebar.classList.remove('-translate-x-full');
            } else {
                if (!this.sidebarOpen) {
                    this.sidebar.classList.add('-translate-x-full');
                }
            }
        });

        // iframe 加载监听
        if (this.reportFrame) {
            this.reportFrame.addEventListener('load', () => {
                this.hideLoading();
                // 仅当 src 不为空时才打印加载完成
                if (this.reportFrame.contentWindow.location.href !== 'about:blank') {
                    console.log('[ReportViewer] 📄 报告加载完成');
                }
            });
        }
    }

    async loadMetadata() {
        // 使用相对路径 ./data/metadata.json 解决 GitHub Pages 路径问题
        const response = await fetch('./data/metadata.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        this.metadata = await response.json();
    }

    renderHistoryList() {
        if (!this.historyList || !this.metadata) return;

        this.historyList.innerHTML = '';

        this.metadata.history.forEach(item => {
            const li = document.createElement('li');
            const isLatest = item.date === this.metadata.latest_report?.replace('report-', '').replace('.html', '');

            // Tailwind classes
            const baseClasses = 'history-item cursor-pointer p-3 rounded-lg border transition-colors mb-2';
            const activeClasses = isLatest
                ? 'bg-blue-50 border-blue-200'
                : 'bg-white border-transparent hover:bg-slate-50 hover:border-slate-200';

            li.className = `${baseClasses} ${activeClasses}`;
            li.dataset.date = item.date;
            li.dataset.filename = item.filename;

            li.innerHTML = `
                <div class="flex justify-between items-center mb-1">
                    <span class="font-medium text-slate-700">${item.date}</span>
                    <span class="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">${item.total_notes}条</span>
                </div>
                <div class="text-xs text-slate-500 flex justify-between">
                     <span class="truncate max-w-[100px]">📌 ${item.top_topic}</span>
                     <span>❤️ ${this.formatNumber(item.avg_likes)}</span>
                </div>
            `;

            li.addEventListener('click', () => {
                this.loadReport(item.filename, item.date);
                // 移动端点击后自动关闭侧边栏
                if (window.innerWidth < 1024) {
                    this.closeSidebar();
                }

                // 更新选中状态样式
                document.querySelectorAll('.history-item').forEach(el => {
                    el.classList.remove('ring-2', 'ring-blue-500', 'border-blue-500');
                    // 重置背景色
                    if (el.classList.contains('bg-blue-50')) {
                        // 保持最新项的基础样式，但移除选中环
                    }

                    if (el === li) {
                        el.classList.add('ring-2', 'ring-blue-500', 'border-blue-500');
                    }
                });
            });

            this.historyList.appendChild(li);
        });
    }

    loadReport(filename, date) {
        console.log(`[ReportViewer] 加载报告: ${filename}`);
        this.showLoading();
        this.welcomeState.classList.add('hidden');
        this.reportFrame.classList.remove('hidden');

        // 使用相对路径
        this.reportFrame.src = filename;

        // 更新 URL 参数，方便分享
        const url = new URL(window.location);
        url.searchParams.set('date', date);
        window.history.pushState({}, '', url);
    }

    showWelcome() {
        this.hideLoading();
        this.reportFrame.classList.add('hidden');
        this.welcomeState.classList.remove('hidden');
    }

    showLoading() {
        this.loadingState.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingState.classList.add('hidden');
    }

    showError(msg) {
        this.loadingState.innerHTML = `
            <div class="text-center text-red-500 p-4">
                <div class="text-4xl mb-2">⚠️</div>
                <p>${msg}</p>
                <button id="retryBtn" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
                    重试
                </button>
            </div>
        `;
        this.loadingState.classList.remove('hidden');

        // 绑定重试事件
        document.getElementById('retryBtn').addEventListener('click', () => {
            this.loadData();
        });
    }

    toggleSidebar() {
        if (this.sidebar.classList.contains('-translate-x-full')) {
            this.openSidebar();
        } else {
            this.closeSidebar();
        }
    }

    openSidebar() {
        this.sidebar.classList.remove('-translate-x-full');
        this.sidebarOverlay.classList.remove('hidden');
        this.sidebarOpen = true;
    }

    closeSidebar() {
        this.sidebar.classList.add('-translate-x-full');
        this.sidebarOverlay.classList.add('hidden');
        this.sidebarOpen = false;
    }

    formatNumber(num) {
        if (num >= 10000) return (num / 10000).toFixed(1) + 'w';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
        return num.toString();
    }
}

// 启动
document.addEventListener('DOMContentLoaded', () => {
    window.viewer = new ReportViewer();
    window.viewer.init();
});
