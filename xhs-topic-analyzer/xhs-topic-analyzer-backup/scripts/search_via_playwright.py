#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 Playwright 搜索小红书内容
由于 MCP 服务无法连接,使用浏览器自动化作为备用方案
"""

import json
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import re
from pathlib import Path

# 配置
SKILL_DIR = Path("/Users/henry/.claude/skills/xhs-topic-analyzer")
CONFIG_FILE = SKILL_DIR / "config.json"
DATA_FILE = SKILL_DIR / "data.json"

# Finance Pro Mode 关键词
KEYWORDS = ["理财", "基金", "股票", "副业", "搞钱", "存钱", "宏观经济", "黄金", "A股", "保险"]

async def extract_fans_number(page):
    """从页面提取粉丝数"""
    try:
        # 等待页面加载
        await page.wait_for_timeout(2000)

        # 尝试从页面提取粉丝数
        fans_text = await page.evaluate("""
            () => {
                // 尝试多种选择器
                const selectors = [
                    '.user-info .fans',
                    '.author-info .fans',
                    '[class*="fans"]',
                    '[class*="follower"]',
                    '.user-card .count'
                ];

                for (const selector of selectors) {
                    const element = document.querySelector(selector);
                    if (element) {
                        return element.textContent.trim();
                    }
                }

                // 尝试从页面文本中提取
                const bodyText = document.body.textContent;
                const match = bodyText.match(/粉丝[：:]\s*([0-9.万千]+)/);
                if (match) {
                    return match[1];
                }

                return null;
            }
        """)

        if fans_text:
            # 转换粉丝数为数字
            fans_text = fans_text.strip()
            if '万' in fans_text:
                return int(float(fans_text.replace('万', '')) * 10000)
            elif '千' in fans_text:
                return int(float(fans_text.replace('千', '')) * 1000)
            else:
                return int(re.sub(r'[^\d]', '', fans_text))
        return 0
    except Exception as e:
        print(f"提取粉丝数失败: {e}")
        return 0

async def search_keyword(page, keyword):
    """搜索单个关键词"""
    print(f"\n🔍 搜索关键词: {keyword}")

    # 访问搜索结果页面
    search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
    await page.goto(search_url)
    await page.wait_for_timeout(3000)

    # 检查是否需要登录
    is_login_required = await page.evaluate("""
        () => {
            return document.body.textContent.includes('登录后查看搜索结果')
        }
    """)

    if is_login_required:
        print(f"❌ 搜索 '{keyword}' 失败: 需要登录")
        return []

    # 提取搜索结果
    notes = await page.evaluate("""
        () => {
            const results = [];

            // 尝试提取笔记卡片
            const noteCards = document.querySelectorAll('[class*="note-item"], [class*="feed-card"], a[href*="/explore/"]');

            noteCards.forEach(card => {
                try {
                    const link = card.href || card.querySelector('a[href*="/explore/"]')?.href;
                    if (!link) return;

                    // 提取笔记 ID
                    const idMatch = link.match(/\/explore\/([a-f0-9]+)/);
                    if (!idMatch) return;

                    const id = idMatch[1];

                    // 提取标题
                    const titleElement = card.querySelector('[class*="title"]') ||
                                       card.querySelector('.note-title') ||
                                       card.querySelector('h3') ||
                                       card.querySelector('h4');
                    const title = titleElement ? titleElement.textContent.trim() : '';

                    // 提取博主昵称
                    const authorElement = card.querySelector('[class*="author"]') ||
                                        card.querySelector('[class*="nickname"]') ||
                                        card.querySelector('.user-name');
                    const nickname = authorElement ? authorElement.textContent.trim() : '';

                    // 提取点赞数
                    const likeElement = card.querySelector('[class*="like"]') ||
                                      card.querySelector('[class*="liked"]');
                    let likedCount = 0;
                    if (likeElement) {
                        const likeText = likeElement.textContent.trim();
                        if ('万' in likeText) {
                            likedCount = int(float(likeText.replace('万', '')) * 10000);
                        } else {
                            likedCount = int(re.sub(r'[^\d]', '', likeText));
                        }
                    }

                    if (title && id) {
                        results.push({
                            id,
                            title,
                            nickname,
                            likedCount,
                            collectedCount: 0,
                            commentCount: 0
                        });
                    }
                } catch (e) {
                    console.error('提取笔记失败:', e);
                }
            });

            return results;
        }
    """)

    print(f"✅ 搜索 '{keyword}' 完成: 找到 {len(notes)} 条结果")
    return notes

async def main():
    """主函数"""
    print("🚀 开始使用 Playwright 搜索小红书内容...")

    # 读取配置
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)

    all_notes = []
    search_results = {}

    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # 搜索每个关键词
            for keyword in KEYWORDS:
                notes = await search_keyword(page, keyword)
                search_results[keyword] = len(notes)
                all_notes.extend(notes)

                # 避免请求过快
                await asyncio.sleep(2)

        finally:
            await browser.close()

    # 去重
    seen_ids = set()
    unique_notes = []
    for note in all_notes:
        if note['id'] not in seen_ids:
            seen_ids.add(note['id'])
            unique_notes.append(note)

    # 按点赞数排序
    unique_notes.sort(key=lambda x: x['likedCount'], reverse=True)

    # 构建 URL 列表
    note_urls = [f"https://www.xiaohongshu.com/explore/{note['id']}" for note in unique_notes]

    # 统计唯一博主
    unique_nicknames = set(note['nickname'] for note in unique_notes if note['nickname'])

    # 构建结果数据
    result = {
        "feeds": unique_notes,
        "keywords": KEYWORDS,
        "fetched_at": datetime.now().isoformat(),
        "total_search_results": len(unique_notes),
        "unique_nicknames": len(unique_nicknames),
        "with_fans_data": False,
        "mode": "pro",
        "keywords_executed": KEYWORDS,
        "note_urls": note_urls
    }

    # 保存数据
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n" + "="*60)
    print("✅ 搜索完成!")
    print(f"📊 搜索结果统计:")
    for keyword, count in search_results.items():
        print(f"   - {keyword}: {count} 条")
    print(f"\n📈 总计: {len(unique_notes)} 条笔记")
    print(f"👥 唯一博主: {len(unique_nicknames)} 位")
    print(f"💾 数据已保存到: {DATA_FILE}")
    print("="*60)

    # 返回摘要
    return {
        "status": "success",
        "search_results_per_keyword": search_results,
        "total_search_results": len(unique_notes),
        "unique_nicknames": len(unique_nicknames),
        "mode": "pro",
        "keywords_executed": KEYWORDS,
        "note_urls": note_urls[:10]  # 只返回前10个URL作为示例
    }

if __name__ == "__main__":
    result = asyncio.run(main())
    print("\n📋 返回摘要:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
