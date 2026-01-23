#!/usr/bin/env python3
"""
HTML 报告生成器 - 小红书爆款选题分析器
(Tailwind CSS 专业版)

功能：
1. 读取分析数据生成 HTML 报告
2. 生成历史记录索引
3. 保存数据到 docs/data/reports/
4. 更新 metadata.json

作者：猫娘工程师 幽浮喵 ฅ'ω'ฅ
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / 'config.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_data(data_file: str) -> Dict[str, Any]:
    """加载分析数据"""
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_metadata(metadata: Dict[str, Any], docs_dir: Path):
    """保存元数据到 metadata.json"""
    metadata_file = docs_dir / 'data' / 'metadata.json'
    metadata_file.parent.mkdir(parents=True, exist_ok=True)

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"[Metadata] 已更新: {metadata_file}")


def copy_data_file(data_file: str, date: str, docs_dir: Path):
    """复制数据文件到 docs/data/reports/"""
    reports_dir = docs_dir / 'data' / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)

    dest_file = reports_dir / f'{date}.json'

    shutil.copy(data_file, dest_file)
    print(f"[Data] 数据文件已复制: {dest_file}")

    return f'data/reports/{date}.json'


def generate_report_html(data: Dict[str, Any], date: str, docs_dir: Path) -> str:
    """生成每日报告 HTML"""

    # 提取数据 - 兼容两种数据结构
    raw_notes = data.get('notes', [])
    if not raw_notes and 'top_feeds' in data:
        raw_notes = data.get('top_feeds', [])

    # 标准化数据格式
    notes = []
    for n in raw_notes:
        # 基础字段映射
        note = {
            'title': n.get('title', '无标题'),
            'author': n.get('author') or n.get('user', '未知作者'),
            'url': n.get('url') or (f"https://www.xiaohongshu.com/explore/{n.get('id')}" if n.get('id') else '#'),
            'likes': n.get('likes') or n.get('liked_count', 0),
            'favs': n.get('favs') or n.get('collected_count', 0),
            'comments': n.get('comments') or n.get('comment_count', 0),
            'topic': n.get('topic') or n.get('keyword', '未分类'),
        }

        # 计算或获取额外指标
        # 如果没有粉丝数，用收藏数代替展示（或隐藏）
        note['fans'] = n.get('fans') or n.get('collected_count', 0)

        # 计算爆款指数 (简单算法: 点赞 + 收藏*2 + 评论*3) / 1000
        if 'viral_score' in n:
            note['viral_score'] = n['viral_score']
        else:
            score = (note['likes'] + note['favs'] * 2 + note['comments'] * 3) / 1000
            note['viral_score'] = round(score, 1)

        notes.append(note)

    total_notes = len(notes)

    # 计算统计数据
    avg_likes = sum(n['likes'] for n in notes) // total_notes if total_notes > 0 else 0
    # 计算平均粉丝数 (或收藏数)
    avg_followers = sum(n['fans'] for n in notes) // total_notes if total_notes > 0 else 0

    # 找出最高爆款指数和低粉高赞案例 (这里改为高收藏案例)
    top_note = max(notes, key=lambda x: x['viral_score'], default=None)

    # 寻找"互动率高"的案例代替"低粉高赞"
    # 定义互动率 = (收藏+评论)/点赞
    high_engagement_note = max(
        notes,
        key=lambda x: (x['favs'] + x['comments']) / x['likes'] if x['likes'] > 0 else 0,
        default=None
    )

    # 选题分布统计
    topic_counts = {}
    for note in notes:
        topic = note['topic']
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # 生成选题分布 HTML
    topic_distribution_html = ''
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    for topic, count in sorted_topics[:5]:
        percentage = (count / total_notes * 100) if total_notes > 0 else 0
        topic_distribution_html += f'''
        <div class="mb-4">
            <div class="flex justify-between items-center mb-1">
                <span class="text-sm font-medium text-slate-700">{topic}</span>
                <span class="text-xs text-slate-500">{count}条 ({percentage:.1f}%)</span>
            </div>
            <div class="w-full bg-slate-200 rounded-full h-2.5">
                <div class="bg-blue-600 h-2.5 rounded-full" style="width: {percentage}%"></div>
            </div>
        </div>
        '''

    # 生成笔记卡片 HTML
    notes_html = ''
    for idx, note in enumerate(notes[:20], 1):  # 只显示前20条
        title = note['title']
        likes = note['likes']
        favs = note['favs']
        comments = note['comments']
        viral_score = note['viral_score']
        note_url = note['url']
        author = note['author']

        rank_badge_color = 'bg-yellow-100 text-yellow-800' if idx == 1 else \
                          'bg-slate-100 text-slate-800' if idx == 2 else \
                          'bg-orange-100 text-orange-800' if idx == 3 else \
                          'bg-slate-50 text-slate-600'

        notes_html += f'''
        <div class="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden flex flex-col">
            <div class="p-5 flex-1">
                <div class="flex justify-between items-start mb-3">
                    <span class="{rank_badge_color} text-xs font-bold px-2.5 py-0.5 rounded-full">#{idx}</span>
                    <span class="bg-blue-50 text-blue-700 text-xs font-semibold px-2.5 py-0.5 rounded-full">爆款指数: {viral_score:.1f}</span>
                </div>
                <h3 class="text-lg font-bold text-slate-900 mb-4 line-clamp-2 h-14" title="{title}">{title}</h3>
                <div class="grid grid-cols-3 gap-2 text-center text-sm">
                    <div class="bg-slate-50 p-2 rounded border border-slate-100">
                        <div class="text-slate-500 text-xs mb-1">点赞</div>
                        <div class="font-semibold text-slate-800">{likes:,}</div>
                    </div>
                    <div class="bg-slate-50 p-2 rounded border border-slate-100">
                        <div class="text-slate-500 text-xs mb-1">收藏</div>
                        <div class="font-semibold text-slate-800">{favs:,}</div>
                    </div>
                    <div class="bg-slate-50 p-2 rounded border border-slate-100">
                        <div class="text-slate-500 text-xs mb-1">评论</div>
                        <div class="font-semibold text-slate-800">{comments:,}</div>
                    </div>
                </div>
                <div class="mt-3 text-xs text-slate-500 text-center">
                    作者: <span class="font-medium text-slate-700">@{author}</span>
                </div>
            </div>
            <div class="bg-slate-50 p-3 border-t border-slate-200 text-center">
                <a href="{note_url}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center justify-center gap-1">
                    查看原文
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                </a>
            </div>
        </div>
        '''

    # 生成完整 HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书财经爆款选题 - {date}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased">
    <div class="flex h-screen overflow-hidden">
        <!-- 侧边栏占位，实际由 JS 动态加载或在 index.html 中处理，单页报告为了兼容性保留简洁顶部导航 -->

        <div class="flex-1 flex flex-col h-full overflow-hidden">
            <!-- 顶部导航 -->
            <header class="bg-white border-b border-slate-200 h-16 flex items-center px-6 justify-between flex-shrink-0 z-10">
                <div class="flex items-center gap-3">
                    <a href="index.html" class="text-slate-500 hover:text-blue-600 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                    </a>
                    <h1 class="text-xl font-bold text-slate-800">小红书财经爆款选题分析报告</h1>
                    <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded border border-blue-200">{date}</span>
                </div>
                <div class="text-sm text-slate-500">
                    生成时间: {datetime.now().strftime('%H:%M:%S')}
                </div>
            </header>

            <!-- 主内容滚动区 -->
            <main class="flex-1 overflow-y-auto p-6 scroll-smooth">
                <div class="max-w-7xl mx-auto space-y-6">

                    <!-- 统计卡片 -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
                            <div class="flex items-center gap-4">
                                <div class="p-3 bg-blue-50 text-blue-600 rounded-lg">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <div>
                                    <p class="text-sm font-medium text-slate-500">发现爆文</p>
                                    <p class="text-2xl font-bold text-slate-900">{total_notes}</p>
                                </div>
                            </div>
                        </div>
                        <div class="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
                            <div class="flex items-center gap-4">
                                <div class="p-3 bg-red-50 text-red-600 rounded-lg">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                </div>
                                <div>
                                    <p class="text-sm font-medium text-slate-500">平均点赞</p>
                                    <p class="text-2xl font-bold text-slate-900">{avg_likes:,}</p>
                                </div>
                            </div>
                        </div>
                        <div class="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
                            <div class="flex items-center gap-4">
                                <div class="p-3 bg-green-50 text-green-600 rounded-lg">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                                    </svg>
                                </div>
                                <div>
                                    <p class="text-sm font-medium text-slate-500">平均粉丝</p>
                                    <p class="text-2xl font-bold text-slate-900">{avg_followers:,}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <!-- 选题洞察 -->
                        <div class="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-gradient-to-br from-blue-50 to-white rounded-lg border border-blue-100 p-6 shadow-sm">
                                <div class="flex items-center gap-2 mb-4">
                                    <span class="text-2xl">🏆</span>
                                    <h3 class="text-lg font-bold text-slate-800">最高爆款指数</h3>
                                </div>
                                <div class="space-y-2">
                                    {f'<div class="font-medium text-slate-900 line-clamp-2">{top_note.get("title", "无")}</div><div class="text-sm text-slate-600">爆款指数: <span class="font-bold text-blue-600">{top_note.get("viral_score", 0):.1f}</span></div><div class="text-xs text-slate-500">❤️ {top_note.get("likes", 0):,} 赞 | @{top_note.get("author", "未知")}</div>' if top_note else "<p class='text-slate-500'>暂无数据</p>"}
                                </div>
                            </div>

                            <div class="bg-gradient-to-br from-green-50 to-white rounded-lg border border-green-100 p-6 shadow-sm">
                                <div class="flex items-center gap-2 mb-4">
                                    <span class="text-2xl">⭐</span>
                                    <h3 class="text-lg font-bold text-slate-800">高互动潜力</h3>
                                </div>
                                <div class="space-y-2">
                                     {f'<div class="font-medium text-slate-900 line-clamp-2">{high_engagement_note.get("title", "无")}</div><div class="text-sm text-slate-600">互动数: <span class="font-bold text-green-600">{high_engagement_note.get("favs", 0) + high_engagement_note.get("comments", 0):,}</span></div><div class="text-xs text-slate-500">❤️ {high_engagement_note.get("likes", 0):,} 赞 | @{high_engagement_note.get("author", "未知")}</div>' if high_engagement_note else "<p class='text-slate-500'>暂无数据</p>"}
                                </div>
                            </div>
                        </div>

                        <!-- 选题分布 -->
                        <div class="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
                            <h3 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                                </svg>
                                选题分布
                            </h3>
                            <div>
                                {topic_distribution_html}
                            </div>
                        </div>
                    </div>

                    <!-- 笔记列表 -->
                    <div class="space-y-4">
                        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
                            <span class="text-2xl">🔥</span>
                            TOP {min(20, total_notes)} 爆款笔记
                        </h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {notes_html}
                        </div>
                    </div>

                    <!-- 页脚 -->
                    <footer class="mt-12 pt-8 border-t border-slate-200 text-center text-slate-500 text-sm pb-8">
                        <p>🔔 每日自动更新 | 扫描关键词: 金融、财经、理财</p>
                        <p class="mt-2 text-xs">数据来源于小红书公开内容 · 仅供学习参考</p>
                    </footer>
                </div>
            </main>
        </div>
    </div>
</body>
</html>'''

    # 保存 HTML 文件
    report_file = docs_dir / f'report-{date}.html'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[HTML] 报告已生成: {report_file}")
    return str(report_file)


def update_index_html(metadata: Dict[str, Any], docs_dir: Path):
    """更新 index.html 作为历史记录索引页"""

    # 生成历史记录列表 HTML (JSON 结构，由前端 JS 渲染)
    # 为了 SEO 和无 JS 环境，我们也可以预渲染一部分

    # 这里我们只更新 index.html 的结构，内容由 report.js 动态加载
    # 但为了更好的体验，我们将基本的骨架写入

    # 历史记录列表 - 预渲染前5条
    history_html = ''
    for item in metadata.get('history', [])[:5]:
        date = item.get('date', '')
        total_notes = item.get('total_notes', 0)
        avg_likes = item.get('avg_likes', 0)
        top_topic = item.get('top_topic', '未分类')

        is_latest = item.get('date') == metadata.get('latest_report', '').replace('report-', '').replace('.html', '')
        active_class = 'bg-blue-50 border-blue-200' if is_latest else 'hover:bg-slate-50 border-transparent'

        history_html += f'''
        <li class="history-item cursor-pointer p-3 rounded-lg border {active_class} transition-colors mb-2" data-date="{date}">
            <div class="flex justify-between items-center mb-1">
                <span class="font-medium text-slate-700">{date}</span>
                <span class="text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">{total_notes}条</span>
            </div>
            <div class="text-xs text-slate-500 flex justify-between">
                 <span>📌 {top_topic}</span>
                 <span>❤️ {avg_likes:,}</span>
            </div>
        </li>
        '''

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书财经爆款选题分析 - 仪表盘</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        /* 隐藏滚动条但允许滚动 */
        .no-scrollbar::-webkit-scrollbar {{
            display: none;
        }}
        .no-scrollbar {{
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
    </style>
</head>
<body class="bg-slate-50 h-screen overflow-hidden flex text-slate-800">

    <!-- 移动端侧边栏遮罩 -->
    <div id="sidebarOverlay" class="fixed inset-0 bg-black/50 z-20 hidden lg:hidden glass-effect"></div>

    <!-- 侧边栏 -->
    <aside id="sidebar" class="fixed inset-y-0 left-0 w-64 bg-white border-r border-slate-200 z-30 transform -translate-x-full lg:translate-x-0 transition-transform duration-300 flex flex-col">
        <div class="p-4 border-b border-slate-100 flex items-center gap-3">
            <span class="text-2xl">📊</span>
            <div>
                <h1 class="font-bold text-slate-800 leading-tight">爆款选题分析</h1>
                <p class="text-xs text-slate-500">财经/理财赛道</p>
            </div>
        </div>

        <div class="flex-1 overflow-y-auto p-4 no-scrollbar">
            <div class="mb-4">
                <h3 class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">历史报告</h3>
                <ul class="history-list space-y-1">
                    <!-- 历史记录将由 JS 动态加载 -->
                    <div class="animate-pulse space-y-3">
                        <div class="h-16 bg-slate-100 rounded-lg"></div>
                        <div class="h-16 bg-slate-100 rounded-lg"></div>
                        <div class="h-16 bg-slate-100 rounded-lg"></div>
                    </div>
                </ul>
            </div>
        </div>

        <div class="p-4 border-t border-slate-100">
            <div class="text-xs text-center text-slate-400">
                <p>共 {metadata.get('total_reports', 0)} 期报告</p>
                <p class="mt-1">By 幽浮喵 ฅ'ω'ฅ</p>
            </div>
        </div>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col h-full lg:ml-64 transition-all duration-300">

        <!-- 顶部导航条 (移动端显示) -->
        <header class="bg-white border-b border-slate-200 h-16 flex items-center px-4 justify-between lg:hidden flex-shrink-0">
            <button id="sidebarToggle" class="p-2 text-slate-600 hover:bg-slate-100 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
            </button>
            <span class="font-bold text-slate-800">仪表盘</span>
            <div class="w-10"></div> <!-- 占位保持居中 -->
        </header>

        <!-- iframe 容器 -->
        <main class="flex-1 relative bg-slate-50 overflow-hidden">
            <div id="loadingState" class="absolute inset-0 flex items-center justify-center bg-white z-10">
                <div class="text-center">
                    <div class="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                    <p class="text-slate-500 text-sm">正在加载报告...</p>
                </div>
            </div>

            <iframe id="reportFrame" name="contentFrame" class="w-full h-full border-none" src=""></iframe>

            <!-- 欢迎页/空状态 (当没有选中报告时显示) -->
            <div id="welcomeState" class="absolute inset-0 flex items-center justify-center bg-slate-50 hidden">
                <div class="text-center p-8 max-w-md">
                    <div class="text-6xl mb-6">👋</div>
                    <h2 class="text-2xl font-bold text-slate-800 mb-2">欢迎回来</h2>
                    <p class="text-slate-500 mb-8">请从左侧列表选择一期报告查看详细数据分析。</p>

                    <div class="grid grid-cols-2 gap-4 text-left">
                        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                            <div class="text-xs text-slate-400 uppercase mb-1">最新报告</div>
                            <div class="font-medium text-slate-800">{metadata.get('latest_report', '').replace('report-', '').replace('.html', '')}</div>
                        </div>
                        <div class="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                            <div class="text-xs text-slate-400 uppercase mb-1">累计分析</div>
                            <div class="font-medium text-slate-800">{metadata.get('total_reports', 0)} 期</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script src="assets/js/report.js"></script>
</body>
</html>'''

    # 保存 index.html
    index_file = docs_dir / 'index.html'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[Index] 索引页已更新: {index_file}")


def generate_daily_report(data_file: str) -> str:
    """生成每日报告的主函数

    Args:
        data_file: 数据文件路径（如 data.json）

    Returns:
        生成的 HTML 报告文件路径
    """
    print("[Start] 开始生成 HTML 报告...")

    # 加载数据
    data = load_data(data_file)
    # 兼容两种数据结构
    notes = data.get('notes', [])
    if not notes and 'top_feeds' in data:
        # 转换 top_feeds 格式以匹配 notes 的基本字段用于统计
        raw_feeds = data.get('top_feeds', [])
        for feed in raw_feeds:
            notes.append({
                'title': feed.get('title', ''),
                'likes': feed.get('liked_count', 0),
                'fans': feed.get('collected_count', 0), # 暂用收藏数代替
                'topic': feed.get('keyword', '未分类'),
                'viral_score': 0 # 暂无
            })

    if not notes:
        print("[Warning] 没有找到笔记数据")
        return None

    # 获取当前日期
    date = datetime.now().strftime('%Y-%m-%d')

    # 获取项目目录
    script_dir = Path(__file__).parent
    docs_dir = script_dir.parent / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 生成每日报告 HTML
    report_path = generate_report_html(data, date, docs_dir)

    # 复制数据文件
    data_rel_path = copy_data_file(data_file, date, docs_dir)

    # 计算统计数据
    total_notes = len(notes)
    avg_likes = sum(n.get('likes', 0) for n in notes) // total_notes if total_notes > 0 else 0

    # 统计选题分布
    topic_counts = {}
    for note in notes:
        topic = note.get('topic', '未分类')
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    top_topic = max(topic_counts.items(), key=lambda x: x[1])[0] if topic_counts else '未分类'

    # 更新或创建 metadata
    metadata_file = docs_dir / 'data' / 'metadata.json'
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'latest_report': f'report-{date}.html',
            'total_reports': 0,
            'history': []
        }

    # 添加新的历史记录
    new_history_item = {
        'date': date,
        'filename': f'report-{date}.html',
        'data_file': data_rel_path,
        'total_notes': total_notes,
        'avg_likes': avg_likes,
        'top_topic': top_topic,
        'generated_at': datetime.now().isoformat()
    }

    # 检查是否已存在同日期的记录
    history = metadata.get('history', [])
    history = [h for h in history if h.get('date') != date]  # 移除旧的同日期记录
    history.insert(0, new_history_item)  # 添加到开头

    # 更新 metadata
    metadata['generated_at'] = datetime.now().isoformat()
    metadata['latest_report'] = f'report-{date}.html'
    metadata['total_reports'] = len(history)
    metadata['history'] = history

    # 保存 metadata
    save_metadata(metadata, docs_dir)

    # 更新 index.html
    update_index_html(metadata, docs_dir)

    print(f"[Success] HTML 报告生成完成: {report_path}")
    return report_path


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='生成 HTML 报告')
    parser.add_argument('--input', required=True, help='输入数据文件路径')
    parser.add_argument('--output', help='输出目录（默认为 docs/）')

    args = parser.parse_args()

    generate_daily_report(args.input)
