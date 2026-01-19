#!/usr/bin/env python3
"""
小红书低粉爆文 - HTML微信推送模块
使用HTML模板生成美观的微信推送内容
"""
from datetime import datetime


def generate_html_template(notes, excel_path="", github_url=""):
    """
    生成HTML推送模板

    Args:
        notes: 笔记列表
        excel_path: Excel文件路径
        github_url: GitHub Pages URL

    Returns:
        str: HTML内容
    """
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 计算统计数据
    total_notes = len(notes)
    avg_likes = sum(n['likes'] for n in notes) // total_notes if total_notes > 0 else 0
    avg_followers = sum(n['followers'] for n in notes) // total_notes if total_notes > 0 else 0
    top_note = notes[0] if notes else None
    min_followers_note = min(notes, key=lambda x: x['followers']) if notes else None

    # 生成笔记卡片HTML
    notes_html = ""
    for i, note in enumerate(notes[:10], 1):
        title = note["title"][:35] + "..." if len(note["title"]) > 35 else note["title"]
        likes = note["likes"]
        followers = note["followers"]
        score = note["viral_score"]
        note_url = note["note_url"]

        # 根据排名设置不同的渐变背景色
        if i == 1:
            bg_gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            icon = "🏆"
        elif i == 2:
            bg_gradient = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            icon = "🥈"
        elif i == 3:
            bg_gradient = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            icon = "🥉"
        else:
            bg_gradient = "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
            icon = f"#{i}"

        notes_html += f"""
        <div style="margin-bottom: 16px;">
            <div style="background: {bg_gradient}; padding: 16px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 24px;">{icon}</span>
                    <span style="background: rgba(255,255,255,0.3); padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">爆款指数: {score:.2f}</span>
                </div>
                <div style="background: rgba(255,255,255,0.95); padding: 12px; border-radius: 8px; margin-top: 8px;">
                    <div style="font-size: 16px; font-weight: bold; color: #333; margin-bottom: 8px; line-height: 1.4;">
                        {title}
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 14px; color: #666; margin-bottom: 8px;">
                        <span>❤️ {likes:,} 赞</span>
                        <span>👥 {followers:,} 粉丝</span>
                    </div>
                    <a href="{note_url}" style="display: block; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 14px;">
                        🔗 查看笔记 →
                    </a>
                </div>
            </div>
        </div>
        """

    # 生成完整的HTML内容
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);">

        <!-- 标题区域 -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px 20px; border-radius: 16px; margin-bottom: 24px; text-align: center; box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);">
            <div style="font-size: 48px; margin-bottom: 12px;">📊</div>
            <h1 style="color: white; font-size: 28px; margin: 0 0 8px 0; font-weight: bold;">小红书财经爆文日报</h1>
            <div style="color: rgba(255,255,255,0.9); font-size: 14px;">{today}</div>
        </div>

        <!-- 统计数据卡片 -->
        <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #333; font-size: 18px; margin: 0 0 16px 0; font-weight: bold; border-bottom: 2px solid #667eea; padding-bottom: 8px;">📈 今日数据概览</h2>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px;">
                <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold; color: #2d3436;">{total_notes}</div>
                    <div style="font-size: 12px; color: #636e72;">发现爆文</div>
                </div>
                <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold; color: white;">{avg_likes:,}</div>
                    <div style="font-size: 12px; color: rgba(255,255,255,0.9);">平均点赞</div>
                </div>
                <div style="text-align: center; padding: 12px; background: linear-gradient(135deg, #55efc4 0%, #00b894 100%); border-radius: 8px;">
                    <div style="font-size: 24px; font-weight: bold; color: white;">{avg_followers:,}</div>
                    <div style="font-size: 12px; color: rgba(255,255,255,0.9);">平均粉丝</div>
                </div>
            </div>
        </div>

        <!-- TOP 10 爆款笔记 -->
        <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #333; font-size: 18px; margin: 0 0 16px 0; font-weight: bold; border-bottom: 2px solid #667eea; padding-bottom: 8px;">🔥 TOP 10 爆款笔记</h2>
            {notes_html}
        </div>

        <!-- 选题洞察 -->
        <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #333; font-size: 18px; margin: 0 0 16px 0; font-weight: bold; border-bottom: 2px solid #667eea; padding-bottom: 8px;">💡 选题洞察</h2>"""

    # 添加最高爆款指数卡片
    if top_note:
        html_content += f"""
            <div style="margin-bottom: 16px; padding: 12px; background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); border-radius: 8px;">
                <div style="font-weight: bold; color: #2d3436; margin-bottom: 4px;">🏆 最高爆款指数</div>
                <div style="font-size: 14px; color: #636e72;">{top_note['viral_score']:.2f} 分</div>
                <div style="font-size: 13px; color: #2d3436; margin-top: 4px;">{top_note['title'][:40]}</div>
            </div>"""

    # 添加平均数据卡片
    html_content += f"""
            <div style="margin-bottom: 16px; padding: 12px; background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); border-radius: 8px;">
                <div style="font-weight: bold; color: white; margin-bottom: 4px;">📈 平均数据</div>
                <div style="font-size: 14px; color: rgba(255,255,255,0.9);">点赞 {avg_likes:,} / 粉丝 {avg_followers:,}</div>
            </div>"""

    # 添加低粉高赞案例卡片
    if min_followers_note:
        html_content += f"""
            <div style="padding: 12px; background: linear-gradient(135deg, #55efc4 0%, #00b894 100%); border-radius: 8px;">
                <div style="font-weight: bold; color: white; margin-bottom: 4px;">⭐ 低粉高赞案例</div>
                <div style="font-size: 13px; color: rgba(255,255,255,0.95);">{min_followers_note['title'][:40]}</div>
                <div style="font-size: 14px; color: white; margin-top: 4px;">仅 {min_followers_note['followers']} 粉丝获得 {min_followers_note['likes']} 赞</div>
            </div>"""

    html_content += """
        </div>

        <!-- 链接区域 -->
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    """

    # 添加GitHub Pages链接
    if github_url:
        html_content += f"""
            <div style="margin-bottom: 12px;"><a href="{github_url}" style="display: block; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px;">🌐 查看完整网页报告 →</a></div>
    """

    # 添加Excel文件路径
    if excel_path:
        html_content += f"""
            <div style="font-size: 12px; color: #999; text-align: center; padding: 8px; background: #f8f9fa; border-radius: 6px;">📁 Excel文件: {excel_path}</div>
    """

    html_content += """
            <div style="font-size: 12px; color: #999; text-align: center; margin-top: 12px;">
                🔔 每日自动更新 | 扫描关键词: 金融、财经、理财
            </div>
        </div>

    </div>
    """

    return html_content


def push_html_to_wechat(token, notes, excel_path="", github_url=""):
    """
    推送HTML内容到微信

    Args:
        token: PushPlus token
        notes: 笔记列表
        excel_path: Excel文件路径
        github_url: GitHub Pages URL

    Returns:
        bool: 推送是否成功
    """
    import requests

    # 生成HTML内容
    html_content = generate_html_template(notes, excel_path, github_url)

    # 构建推送标题
    today = datetime.now().strftime("%m-%d %H:%M")
    title = f"📊 小红书爆文日报 {today}"

    # 推送到微信
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": html_content,
        "template": "html"
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()

        if result.get("code") == 200:
            print("\n[INFO] ✓ HTML微信推送成功!请查看手机")
            return True
        else:
            print(f"\n[WARN] HTML微信推送失败: {result.get('msg')}")
            print(f"[DEBUG] 响应内容: {result}")
            return False
    except Exception as e:
        print(f"\n[ERROR] HTML微信推送异常: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    test_notes = [
        {
            "title": "测试笔记标题这是一个很长的标题需要截断处理",
            "likes": 5000,
            "collects": 3000,
            "comments": 500,
            "followers": 10000,
            "interaction_rate": 85.0,
            "viral_score": 305.2,
            "note_url": "https://www.xiaohongshu.com/explore/123456"
        },
        {
            "title": "另一个测试笔记标题",
            "likes": 3000,
            "collects": 2000,
            "comments": 300,
            "followers": 5000,
            "interaction_rate": 106.0,
            "viral_score": 354.7,
            "note_url": "https://www.xiaohongshu.com/explore/789012"
        }
    ]

    html = generate_html_template(test_notes, excel_path="~/Documents/test.xlsx", github_url="https://example.github.io/test/")
    print("HTML内容生成成功!")
    print("HTML长度:", len(html))
