// 小红书财经爆文分析 - JavaScript交互脚本

let allNotes = [];  // 存储所有笔记数据
let filteredNotes = [];  // 存储筛选后的笔记

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadNotesData();
    setupEventListeners();
});

// 加载笔记数据
async function loadNotesData() {
    try {
        const response = await fetch('data/viral-notes.json');
        if (!response.ok) {
            throw new Error('数据加载失败');
        }
        allNotes = await response.json();
        filteredNotes = [...allNotes];

        updateStatistics();
        updateInsights();
        renderNotes(filteredNotes);
        updateLastModified();
    } catch (error) {
        console.error('加载数据失败:', error);
        showError('数据加载失败，请稍后重试');
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');

    searchButton.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // 筛选按钮
    const filterButtons = document.querySelectorAll('.filter-button');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 移除所有active类
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // 添加active类到当前按钮
            this.classList.add('active');
            // 执行筛选
            handleFilter(this.dataset.filter);
        });
    });

    // 导出按钮
    document.getElementById('exportJson').addEventListener('click', exportAsJson);
    document.getElementById('copyData').addEventListener('click', copyToClipboard);
}

// 更新统计数据
function updateStatistics() {
    const totalNotes = allNotes.length;
    const avgLikes = totalNotes > 0
        ? Math.round(allNotes.reduce((sum, note) => sum + note.likes, 0) / totalNotes)
        : 0;
    const avgFollowers = totalNotes > 0
        ? Math.round(allNotes.reduce((sum, note) => sum + note.followers, 0) / totalNotes)
        : 0;

    document.getElementById('totalNotes').textContent = totalNotes;
    document.getElementById('avgLikes').textContent = avgLikes.toLocaleString();
    document.getElementById('avgFollowers').textContent = avgFollowers.toLocaleString();
}

// 更新选题洞察
function updateInsights() {
    if (allNotes.length === 0) {
        document.getElementById('topNote').innerHTML = '<p>暂无数据</p>';
        document.getElementById('lowFollowerNote').innerHTML = '<p>暂无数据</p>';
        return;
    }

    // 最高爆款指数
    const topNote = allNotes[0];
    document.getElementById('topNote').innerHTML = `
        <div style="margin-bottom: 8px;">
            <strong>爆款指数:</strong> ${topNote.viral_score.toFixed(2)} 分
        </div>
        <div style="margin-bottom: 8px;">
            <strong>标题:</strong> ${truncateText(topNote.title, 50)}
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px;">
            <div>
                <div style="font-size: 12px; opacity: 0.7;">点赞</div>
                <div style="font-weight: bold;">${topNote.likes.toLocaleString()}</div>
            </div>
            <div>
                <div style="font-size: 12px; opacity: 0.7;">粉丝</div>
                <div style="font-weight: bold;">${topNote.followers.toLocaleString()}</div>
            </div>
            <div>
                <div style="font-size: 12px; opacity: 0.7;">互动率</div>
                <div style="font-weight: bold;">${topNote.interaction_rate}%</div>
            </div>
        </div>
        <a href="${topNote.note_url}" target="_blank"
           style="display: inline-block; margin-top: 12px; padding: 8px 16px; background: rgba(255,255,255,0.3); border-radius: 6px; text-decoration: none; color: inherit; font-weight: bold;">
            查看笔记 →
        </a>
    `;

    // 低粉高赞案例
    const minFollowersNote = [...allNotes].sort((a, b) => a.followers - b.followers)[0];
    document.getElementById('lowFollowerNote').innerHTML = `
        <div style="margin-bottom: 8px;">
            <strong>标题:</strong> ${truncateText(minFollowersNote.title, 50)}
        </div>
        <div style="margin-bottom: 8px;">
            <strong>仅 ${minFollowersNote.followers.toLocaleString()} 粉丝获得 ${minFollowersNote.likes.toLocaleString()} 赞</strong>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px;">
            <div>
                <div style="font-size: 12px; opacity: 0.7;">点赞</div>
                <div style="font-weight: bold;">${minFollowersNote.likes.toLocaleString()}</div>
            </div>
            <div>
                <div style="font-size: 12px; opacity: 0.7;">粉丝</div>
                <div style="font-weight: bold;">${minFollowersNote.followers.toLocaleString()}</div>
            </div>
            <div>
                <div style="font-size: 12px; opacity: 0.7;">爆款指数</div>
                <div style="font-weight: bold;">${minFollowersNote.viral_score.toFixed(2)}</div>
            </div>
        </div>
        <a href="${minFollowersNote.note_url}" target="_blank"
           style="display: inline-block; margin-top: 12px; padding: 8px 16px; background: rgba(255,255,255,0.3); border-radius: 6px; text-decoration: none; color: inherit; font-weight: bold;">
            查看笔记 →
        </a>
    `;
}

// 渲染笔记卡片
function renderNotes(notes) {
    const notesGrid = document.getElementById('notesGrid');

    if (notes.length === 0) {
        notesGrid.innerHTML = '<div class="loading">没有找到符合条件的笔记</div>';
        return;
    }

    notesGrid.innerHTML = notes.map((note, index) => {
        const rankClass = index < 3 ? `rank-${index + 1}` : '';
        const rankIcon = index === 0 ? '🏆' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`;

        return `
            <div class="note-card">
                <div class="note-header">
                    <div class="note-rank ${rankClass}">${rankIcon}</div>
                    <div class="note-score-badge">爆款指数: ${note.viral_score.toFixed(2)}</div>
                </div>
                <div class="note-body">
                    <div class="note-title" title="${note.title}">${note.title}</div>
                    <div class="note-stats">
                        <div class="stat-item">
                            <div class="stat-item-label">❤️ 点赞</div>
                            <div class="stat-item-value">${note.likes.toLocaleString()}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">⭐ 收藏</div>
                            <div class="stat-item-value">${note.collects.toLocaleString()}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">💬 评论</div>
                            <div class="stat-item-value">${note.comments.toLocaleString()}</div>
                        </div>
                    </div>
                    <div class="note-stats">
                        <div class="stat-item">
                            <div class="stat-item-label">👥 粉丝</div>
                            <div class="stat-item-value">${note.followers.toLocaleString()}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">📈 互动率</div>
                            <div class="stat-item-value">${note.interaction_rate}%</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-item-label">🔥 爆款</div>
                            <div class="stat-item-value">${note.viral_score.toFixed(2)}</div>
                        </div>
                    </div>
                </div>
                <div class="note-footer">
                    <a href="${note.note_url}" target="_blank" class="note-link">
                        🔗 查看笔记 →
                    </a>
                </div>
            </div>
        `;
    }).join('');
}

// 搜索功能
function handleSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();

    if (!searchTerm) {
        filteredNotes = [...allNotes];
    } else {
        filteredNotes = allNotes.filter(note =>
            note.title.toLowerCase().includes(searchTerm)
        );
    }

    renderNotes(filteredNotes);
}

// 筛选功能
function handleFilter(filterType) {
    switch (filterType) {
        case 'all':
            filteredNotes = [...allNotes];
            break;
        case 'high':
            filteredNotes = allNotes.filter(note => note.likes > 5000);
            break;
        case 'low':
            filteredNotes = allNotes.filter(note => note.followers < 5000);
            break;
        case 'viral':
            filteredNotes = allNotes.filter(note => note.viral_score > 200);
            break;
        default:
            filteredNotes = [...allNotes];
    }

    renderNotes(filteredNotes);
}

// 导出为JSON
function exportAsJson() {
    const dataStr = JSON.stringify(allNotes, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `xhs_viral_notes_${new Date().getTime()}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

// 复制到剪贴板
function copyToClipboard() {
    const dataStr = JSON.stringify(allNotes, null, 2);
    navigator.clipboard.writeText(dataStr).then(() => {
        alert('数据已复制到剪贴板！');
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制失败，请重试');
    });
}

// 更新最后修改时间
function updateLastModified() {
    const updateTimeElement = document.getElementById('updateTime');
    const now = new Date();
    const timeStr = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
    updateTimeElement.textContent = `更新时间: ${timeStr}`;
}

// 显示错误信息
function showError(message) {
    const notesGrid = document.getElementById('notesGrid');
    notesGrid.innerHTML = `
        <div class="loading" style="color: var(--danger-color);">
            <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
            <div>${message}</div>
        </div>
    `;
}

// 截断文本
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + '...';
}
