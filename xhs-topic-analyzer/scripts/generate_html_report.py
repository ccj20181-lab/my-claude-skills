#!/usr/bin/env python3
"""
HTML 报告生成器 - 小红书爆款选题分析器
(Tailwind CSS Professional Edition)

功能：
1. 读取分析数据生成 HTML 报告
2. 生成历史记录索引
3. 保存数据到 docs/data/reports/
4. 更新 metadata.json

By 幽浮喵 ฅ'ω'ฅ
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

    try:
        if os.path.abspath(data_file) != os.path.abspath(dest_file):
            shutil.copy(data_file, dest_file)
            print(f"[Data] 数据文件已复制: {dest_file}")
        else:
            print(f"[Data] 源文件与目标文件相同，跳过复制: {dest_file}")
    except shutil.SameFileError:
        print(f"[Data] 源文件与目标文件相同，跳过复制: {dest_file}")

    return f'data/reports/{date}.json'


def generate_report_html(notes: List[Dict[str, Any]], date: str, docs_dir: Path) -> str:
    """生成每日报告 HTML"""

    total_notes = len(notes)

    # 计算统计数据
    avg_likes = sum(n['likes'] for n in notes) // total_notes if total_notes > 0 else 0
    avg_followers = sum(n['fans'] for n in notes) // total_notes if total_notes > 0 else 0

    # 找出最高爆款指数
    top_note = max(notes, key=lambda x: x['viral_score'], default=None)

    # 选题分布统计
    topic_counts = {}
    for note in notes:
        topic = note['topic']
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    # 生成选题分布 HTML
    topic_distribution_html = ''
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)

    # 定义颜色循环
    colors = ['bg-blue-600', 'bg-indigo-500', 'bg-violet-500', 'bg-purple-500', 'bg-fuchsia-500']

    for i, (topic, count) in enumerate(sorted_topics[:5]):
        percentage = (count / total_notes * 100) if total_notes > 0 else 0
        color_class = colors[i % len(colors)]

        topic_distribution_html += f'''
        <div class="mb-4">
            <div class="flex justify-between items-center mb-1.5">
                <span class="text-sm font-medium text-slate-700">{topic}</span>
                <span class="text-xs text-slate-500 font-medium">{count}篇 ({percentage:.0f}%)</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                <div class="{color_class} h-2 rounded-full transition-all duration-500" style="width: {percentage}%"></div>
            </div>
        </div>
        '''

    # 生成笔记列表 HTML
    notes_html = ''
    for idx, note in enumerate(notes[:50], 1):  # 显示前50条
        title = note['title']
        likes = note['likes']
        favs = note['favs']
        comments = note['comments']
        viral_score = note['viral_score']
        note_url = note['url']
        author = note['author']

        # 排名样式
        rank_badge = ""
        if idx == 1:
            rank_badge = '<span class="flex items-center justify-center w-6 h-6 rounded-md bg-yellow-100 text-yellow-700 text-xs font-bold ring-1 ring-yellow-200">1</span>'
        elif idx == 2:
            rank_badge = '<span class="flex items-center justify-center w-6 h-6 rounded-md bg-slate-200 text-slate-700 text-xs font-bold ring-1 ring-slate-300">2</span>'
        elif idx == 3:
            rank_badge = '<span class="flex items-center justify-center w-6 h-6 rounded-md bg-orange-100 text-orange-700 text-xs font-bold ring-1 ring-orange-200">3</span>'
        else:
            rank_badge = f'<span class="flex items-center justify-center w-6 h-6 text-slate-400 text-xs font-medium">{idx}</span>'

        notes_html += f'''
        <tr class="hover:bg-slate-50 border-b border-slate-100 last:border-0 transition-colors group">
            <td class="px-6 py-4 whitespace-nowrap">
                {rank_badge}
            </td>
            <td class="px-6 py-4">
                <div class="flex flex-col max-w-sm">
                    <a href="{note_url}" target="_blank" class="text-sm font-medium text-slate-900 hover:text-blue-600 mb-1 line-clamp-2 leading-relaxed transition-colors" title="{title}">{title}</a>
                    <div class="flex items-center gap-2 mt-0.5">
                         <span class="text-xs text-slate-500 flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                            {author}
                         </span>
                         <span class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">{note.get('topic', '未分类')}</span>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                    <div class="flex flex-col">
                        <span class="text-sm font-bold text-blue-600">{viral_score:.1f}</span>
                        <div class="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden mt-1">
                            <div class="h-full bg-blue-500 rounded-full" style="width: {min(viral_score, 100)}%"></div>
                        </div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600 font-medium">
                {likes:,}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {favs:,}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                {comments:,}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right">
                <a href="{note_url}" target="_blank" class="text-xs font-medium text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-md transition-colors inline-flex items-center gap-1">
                    查看
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>
            </td>
        </tr>
        '''

    # 准备 MVP 数据
    mvp_title = top_note['title'] if top_note else '无数据'
    mvp_author = top_note['author'] if top_note else '-'
    mvp_score = top_note['viral_score'] if top_note else 0.0

    # 生成完整 HTML (Inside Iframe)
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>报告详情 - {date}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        /* Custom scrollbar for table */
        .custom-scrollbar::-webkit-scrollbar {{
            height: 8px;
            width: 8px;
        }}
        .custom-scrollbar::-webkit-scrollbar-track {{
            background: #f1f5f9;
        }}
        .custom-scrollbar::-webkit-scrollbar-thumb {{
            background: #cbd5e1;
            border-radius: 4px;
        }}
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {{
            background: #94a3b8;
        }}
    </style>
</head>
<body class="bg-slate-50/50 text-slate-800 antialiased min-h-screen p-4 md:p-8">

    <div class="max-w-7xl mx-auto space-y-6">

        <!-- Header -->
        <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-2">
            <div>
                <h1 class="text-2xl font-bold text-slate-900 tracking-tight">每日爆款分析报告</h1>
                <p class="text-sm text-slate-500 mt-1 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    {date}
                </p>
            </div>
            <div class="flex items-center gap-3">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                    <span class="w-1.5 h-1.5 rounded-full bg-green-500 mr-1.5"></span>
                    分析完成
                </span>
                <span class="text-xs text-slate-400">生成于 {datetime.now().strftime('%H:%M')}</span>
            </div>
        </header>

        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6">
            <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-slate-500">监控笔记数</p>
                    <div class="p-2 bg-blue-50 rounded-lg text-blue-600">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                    </div>
                </div>
                <p class="text-2xl font-bold text-slate-900">{total_notes}</p>
            </div>

            <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-slate-500">平均点赞</p>
                    <div class="p-2 bg-red-50 rounded-lg text-red-500">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                    </div>
                </div>
                <p class="text-2xl font-bold text-slate-900">{avg_likes:,}</p>
            </div>

             <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-slate-500">平均粉丝</p>
                    <div class="p-2 bg-purple-50 rounded-lg text-purple-600">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
                    </div>
                </div>
                <p class="text-2xl font-bold text-slate-900">{avg_followers:,}</p>
            </div>

             <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-2">
                    <p class="text-sm font-medium text-slate-500">最高爆款指数</p>
                    <div class="p-2 bg-orange-50 rounded-lg text-orange-500">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    </div>
                </div>
                <p class="text-2xl font-bold text-blue-600">{mvp_score:.1f}</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Left: Topic Distribution -->
            <div class="lg:col-span-1 space-y-6">
                <!-- Topic Card -->
                <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                    <h3 class="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" /></svg>
                        热门选题分布
                    </h3>
                    <div class="space-y-1">
                        {topic_distribution_html}
                    </div>
                </div>

                <!-- MVP Card -->
                <div class="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl border border-slate-700 p-6 shadow-sm text-white relative overflow-hidden group">
                    <div class="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-white/10 rounded-full blur-2xl group-hover:bg-white/20 transition-all duration-500"></div>

                    <div class="relative z-10">
                        <div class="flex justify-between items-start mb-4">
                            <div>
                                <h4 class="text-xs font-bold text-blue-300 uppercase tracking-wider mb-1">今日 MVP 笔记</h4>
                                <h3 class="text-lg font-bold text-white line-clamp-2">{mvp_title}</h3>
                            </div>
                            <span class="bg-white/20 backdrop-blur-sm px-2 py-1 rounded text-xs font-bold">TOP 1</span>
                        </div>

                        <div class="flex items-center gap-3 mb-4">
                            <div class="h-8 w-8 rounded-full bg-white/10 flex items-center justify-center text-xs">
                                {mvp_author[0] if mvp_author else '?'}
                            </div>
                            <span class="text-sm text-slate-300">@{mvp_author}</span>
                        </div>

                        <div class="flex items-center justify-between pt-4 border-t border-white/10">
                            <div>
                                <p class="text-xs text-slate-400">爆款指数</p>
                                <p class="text-xl font-bold text-blue-400">{mvp_score:.1f}</p>
                            </div>
                            <a href="#" class="text-xs bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-colors">
                                查看详情
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Right: Data Table -->
            <div class="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden h-fit">
                <div class="px-6 py-5 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
                    <h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
                        爆款笔记榜单 (Top 50)
                    </h3>
                    <div class="flex gap-2">
                        <span class="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded border border-slate-200">综合排序</span>
                    </div>
                </div>
                <div class="overflow-x-auto custom-scrollbar">
                    <table class="min-w-full divide-y divide-slate-200">
                        <thead class="bg-slate-50">
                            <tr>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider w-12">#</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">标题 / 作者</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">爆款指数</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">点赞</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">收藏</th>
                                <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">评论</th>
                                <th scope="col" class="relative px-6 py-3"><span class="sr-only">操作</span></th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-slate-200">
                            {notes_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="text-center text-slate-400 text-xs py-8">
            <p>Generated by XHS Topic Analyzer • <a href="https://github.com/henry" class="hover:text-slate-600 underline decoration-slate-300">View on GitHub</a></p>
        </footer>

    </div>
</body>
</html>'''

    # 保存 HTML 文件
    report_file = docs_dir / f'report-{date}.html'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[HTML] 报告已生成: {report_file}")
    return str(report_file)


def generate_daily_report(data_file: str) -> str:
    """生成每日报告的主函数"""
    print("[Start] 开始生成 HTML 报告...")

    # 加载数据
    data = load_data(data_file)
    notes = []
    raw_list = []

    if isinstance(data, list):
        raw_list = data
    elif isinstance(data, dict):
        if 'notes' in data: raw_list = data['notes']
        elif 'top_feeds' in data: raw_list = data['top_feeds']

    # 标准化字段映射
    for item in raw_list:
        note = {}
        # 标题
        note['title'] = item.get('title') or item.get('笔记标题') or '无标题'
        # 作者
        note['author'] = item.get('author') or item.get('user') or item.get('博主昵称') or '未知作者'
        # URL
        if item.get('url'): note['url'] = item.get('url')
        elif item.get('笔记链接'): note['url'] = item.get('笔记链接')
        elif item.get('id'): note['url'] = f"https://www.xiaohongshu.com/explore/{item.get('id')}"
        elif item.get('笔记ID'): note['url'] = f"https://www.xiaohongshu.com/explore/{item.get('笔记ID')}"
        else: note['url'] = '#'

        # 数据指标
        note['likes'] = int(item.get('likes') or item.get('liked_count') or item.get('点赞数') or 0)
        note['favs'] = int(item.get('favs') or item.get('collected_count') or item.get('收藏数') or 0)
        note['comments'] = int(item.get('comments') or item.get('comment_count') or item.get('评论数') or 0)
        note['fans'] = int(item.get('fans') or item.get('博主粉丝数') or 0)

        # 话题/关键词
        note['topic'] = item.get('topic') or item.get('keyword') or item.get('关键词') or '未分类'

        # 爆款指数
        if 'viral_score' in item:
            note['viral_score'] = float(item['viral_score'])
        elif '爆款指数' in item:
            note['viral_score'] = float(item['爆款指数'])
        else:
            # 简单计算
            score = (note['likes'] + note['favs'] * 2 + note['comments'] * 3) / 1000
            note['viral_score'] = round(score, 1)

        notes.append(note)

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
    report_path = generate_report_html(notes, date, docs_dir)

    # 复制数据文件
    data_rel_path = copy_data_file(data_file, date, docs_dir)

    # 计算统计数据
    total_notes = len(notes)
    avg_likes = sum(n['likes'] for n in notes) // total_notes if total_notes > 0 else 0

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
        metadata = {'generated_at': datetime.now().isoformat(), 'latest_report': '', 'total_reports': 0, 'history': []}

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
    history = [h for h in history if h.get('date') != date]
    history.insert(0, new_history_item)

    metadata['generated_at'] = datetime.now().isoformat()
    metadata['latest_report'] = f'report-{date}.html'
    metadata['total_reports'] = len(history)
    metadata['history'] = history

    save_metadata(metadata, docs_dir)
    print(f"[Success] 处理完成，共 {total_notes} 条数据")
    return report_path


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='生成 HTML 报告')
    parser.add_argument('--input', required=True, help='输入数据文件路径')
    args = parser.parse_args()

    generate_daily_report(args.input)
