#!/usr/bin/env python3
"""
HTML Template Generator for GitHub Pages
100% reuses existing template styles from the viral report dashboard

This module generates HTML reports that match the existing Tailwind CSS design.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


def format_number(num: int) -> str:
    """Format large numbers with commas."""
    return "{:,}".format(num)


def get_rank_badge(rank: int) -> str:
    """Generate rank badge HTML based on position."""
    if rank == 1:
        return '<span class="px-2 py-1 text-xs font-bold rounded bg-yellow-100 text-yellow-700">TOP 1</span>'
    elif rank == 2:
        return '<span class="px-2 py-1 text-xs font-bold rounded bg-gray-200 text-gray-700">TOP 2</span>'
    elif rank == 3:
        return '<span class="px-2 py-1 text-xs font-bold rounded bg-orange-100 text-orange-700">TOP 3</span>'
    elif rank <= 10:
        return '<span class="px-2 py-1 text-xs font-semibold rounded bg-blue-50 text-blue-600">TOP 10</span>'
    else:
        return f'<span class="px-2 py-1 text-xs font-medium rounded bg-slate-100 text-slate-600">#{rank}</span>'


def generate_note_card(feed: Dict[str, Any], rank: int) -> str:
    """Generate a note card HTML matching the existing template style."""
    title = feed.get('title', 'Untitled')
    author = feed.get('author', feed.get('nickname', 'Unknown'))
    likes = feed.get('likes', 0)
    followers = feed.get('followers', 0)
    viral_score = feed.get('viral_score', 0)
    note_id = feed.get('id', feed.get('note_id', ''))
    xsec_token = feed.get('xsec_token', '')

    # Generate note URL
    note_url = f"https://www.xiaohongshu.com/explore/{note_id}"
    if xsec_token:
        note_url += f"?xsec_token={xsec_token}"

    rank_badge = get_rank_badge(rank)

    return f'''
        <div class="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md hover:border-blue-300 transition-all duration-200 group">
            <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 mb-2">
                        {rank_badge}
                        <h3 class="font-semibold text-slate-900 truncate group-hover:text-blue-600 transition-colors">
                            <a href="{note_url}" target="_blank" rel="noopener noreferrer" class="hover:underline">{title}</a>
                        </h3>
                    </div>
                    <div class="flex flex-wrap items-center gap-3 text-sm text-slate-600 mb-3">
                        <span class="flex items-center gap-1">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            {author}
                        </span>
                        <span class="flex items-center gap-1">
                            <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                            </svg>
                            {format_number(likes)}
                        </span>
                        <span class="flex items-center gap-1">
                            <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                            </svg>
                            {format_number(followers)}
                        </span>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-medium text-slate-500 uppercase tracking-wider">Viral Index</span>
                        <span class="text-lg font-bold text-blue-600">{viral_score:.2f}</span>
                    </div>
                </div>
            </div>
        </div>
        '''


def generate_stat_card(label: str, value: str, description: str, icon_color: str, icon_svg: str) -> str:
    """Generate a statistics card HTML."""
    return f'''
            <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
                    <div class="w-8 h-8 rounded-lg bg-{icon_color}-50 flex items-center justify-center">
                        {icon_svg}
                    </div>
                </div>
                <p class="text-3xl font-bold text-slate-900">{value}</p>
                <p class="text-xs text-slate-500 mt-1">{description}</p>
            </div>'''


def generate_report_html(
    feeds: List[Dict[str, Any]],
    analysis: Optional[Dict[str, Any]] = None,
    output_dir: str = "/Users/henry/gh-pages-deploy/reports"
) -> str:
    """
    Generate a complete HTML report reusing the existing template styles.

    Args:
        feeds: List of viral note data
        analysis: Optional analysis results from topic_analyzer
        output_dir: Directory to save the report

    Returns:
        The filename of the generated report
    """
    timestamp = datetime.now()
    report_id = timestamp.strftime("%Y%m%d-%H%M%S")
    report_filename = f"report-{report_id}.html"
    display_time = timestamp.strftime("%Y%m%d_%H%M%S")

    # Calculate statistics
    total_notes = len(feeds)
    total_likes = sum(f.get('likes', 0) for f in feeds)
    total_followers = sum(f.get('followers', 0) for f in feeds)
    avg_viral_score = sum(f.get('viral_score', 0) for f in feeds) / max(total_notes, 1)

    # Sort feeds by viral_score
    sorted_feeds = sorted(feeds, key=lambda x: x.get('viral_score', 0), reverse=True)

    # Generate note cards HTML
    note_cards_html = ""
    for rank, feed in enumerate(sorted_feeds, 1):
        note_cards_html += generate_note_card(feed, rank)

    # Generate statistics cards
    stat_cards = f'''
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {generate_stat_card(
                "Found Notes",
                str(total_notes),
                "Qualifying viral notes",
                "blue",
                '<svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>'
            )}
            {generate_stat_card(
                "Total Likes",
                format_number(total_likes),
                "Cumulative likes",
                "red",
                '<svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>'
            )}
            {generate_stat_card(
                "Total Followers",
                format_number(total_followers),
                "Blogger total followers",
                "indigo",
                '<svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>'
            )}
            {generate_stat_card(
                "Avg Index",
                f"{avg_viral_score:.2f}",
                "Average viral score",
                "emerald",
                '<svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>'
            )}
        </div>'''

    # Complete HTML document
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XHS Finance Viral Analysis - {display_time}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-slate-50 text-slate-800 p-6">
    <div class="max-w-7xl mx-auto mb-8">
        <div class="flex items-center justify-between mb-6">
            <div>
                <h1 class="text-2xl font-bold text-slate-900">XHS Finance Viral Analysis</h1>
                <p class="text-sm text-slate-500 mt-1">Discover low-follower high-engagement viral content</p>
            </div>
            <div class="text-right">
                <p class="text-xs text-slate-500">Report Time</p>
                <p class="text-sm font-semibold text-slate-900">{display_time}</p>
            </div>
        </div>
        {stat_cards}
    </div>
    <div class="max-w-7xl mx-auto">
        <div class="space-y-3">
        {note_cards_html}
        </div>
        <footer class="mt-12 pt-8 border-t border-slate-200 text-center">
            <p class="text-sm text-slate-600">Powered by <span class="font-semibold text-blue-600">Fufu Chan</span></p>
            <p class="text-xs text-slate-500 mt-1">Auto-analyze XHS finance low-follower viral content</p>
        </footer>
    </div>
</body>
</html>'''

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Write the file
    output_path = os.path.join(output_dir, report_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[SUCCESS] HTML report generated: {output_path}")
    return report_filename


def generate_report_from_json(json_path: str, output_dir: str = "/Users/henry/gh-pages-deploy/reports") -> str:
    """
    Generate HTML report from a JSON data file.

    Args:
        json_path: Path to JSON file containing feeds data
        output_dir: Output directory for the HTML report

    Returns:
        The filename of the generated report
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    feeds = data.get('feeds', data.get('notes', data))
    analysis = data.get('analysis', None)

    return generate_report_html(feeds, analysis, output_dir)


if __name__ == "__main__":
    # Test with sample data
    sample_feeds = [
        {
            "id": "test123",
            "title": "Test Note Title",
            "author": "Test Author",
            "likes": 5000,
            "followers": 1000,
            "viral_score": 25.5,
        }
    ]

    filename = generate_report_html(sample_feeds)
    print(f"Generated test report: {filename}")
