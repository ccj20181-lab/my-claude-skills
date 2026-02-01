#!/usr/bin/env python3
"""
蜗牛朋友圈文案自动生成机器人
每天定时生成：反馈篇 + 上岸篇 + 报名篇
并推送到微信
"""

import os
import sys
import json
import random
import requests
from datetime import datetime
import pytz
import anthropic

# 风格指南和引用文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_GUIDE_PATH = os.path.join(BASE_DIR, "references", "style-guide.md")
RANDOM_ELEMENTS_PATH = os.path.join(BASE_DIR, "config", "random-elements.md")

def load_file_content(filepath):
    """读取文件内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"[警告] 无法读取文件 {filepath}: {e}")
        return ""

def get_client():
    """初始化 Anthropic 客户端 (支持智谱 GLM)"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL") # 适配智谱 API

    if not api_key:
        print("[错误] 未设置 ANTHROPIC_API_KEY 环境变量")
        return None

    if base_url:
        return anthropic.Anthropic(api_key=api_key, base_url=base_url)
    else:
        return anthropic.Anthropic(api_key=api_key)

def generate_copy(client, copy_type, style_guide, random_elements):
    """生成单条文案"""

    # 定义不同类型的特定提示词
    type_prompts = {
        "反馈篇": """
请生成一篇【反馈篇】朋友圈文案。
核心内容：学员对蜗牛老师的课程、讲义（七大模块/33大主题）的好评。
要求：
1. 引用学员的具体评价（使用引号）。
2. 表达蜗牛老师的感恩和价值感。
3. 语气真诚，不要过于商业化。
4. 参考风格指南中的【反馈篇】结构模板。
""",
        "上岸篇": """
请生成一篇【上岸篇】朋友圈文案。
核心内容：恭喜学员成功考编上岸（地点随机，成绩具体）。
要求：
1. 包含具体的成绩数据（笔试/面试分数、排名、逆袭情况等），请从随机元素库中随机组合。
2. 描述备考的艰辛和成功的喜悦。
3. 结尾表达祝福和鼓励。
4. 参考风格指南中的【上岸篇】结构模板。
""",
        "报名篇": """
请生成一篇【报名篇】朋友圈文案。
核心内容：号召还在犹豫的学员加入学习，或者提醒考期临近。
要求：
1. 语气不要像硬广，要像朋友的提醒和建议。
2. 强调"早准备"的重要性，或者"方法不对努力白费"的痛点。
3. 可以简要提及产品（七大模块/系统课）的帮助。
4. 结尾引导私信或咨询（如：想通过的来聊聊）。
5. 保持蜗牛老师一贯的真诚、温暖风格。
"""
    }

    prompt = f"""
你是一位名为"蜗牛老师"的教师考编结构化面试辅导专家。
请根据以下资料，写一条朋友圈文案。

【风格指南】
{style_guide}

【随机元素库】(请从中随机选择地点、分数、场景等细节，确保多样性)
{random_elements}

【本次任务】
{type_prompts.get(copy_type)}

【输出要求】
1. 直接输出文案内容，不要包含"好的"、"文案如下"等废话。
2. 适当使用Emoji，符合蜗牛老师风格。
3. 格式清晰，方便复制粘贴。
4. 【严禁杜撰题目】：严禁出现具体的题目名称。涉及题目时请用"考到的那个大题"、"押中了原题"等模糊表述。
5. 【隐私保护】：严禁出现学员具体姓名（如小王、小李），统一用"学员"、"同学"、"宝妈"等代称。
6. 【数据模糊化】：严禁出现具体的笔试/面试排名数字（如第5名）、具体分数（如85+、85.4分）。必须使用"高分逆袭"、"名列前茅"、"压线进面"、"全场最高"等模糊表达。
7. 【时间模糊化】：严禁出现具体的查成绩时间（如"早上7点"、"7:00"）。统一使用"一大早"、"刚刚"、"下班后"、"临睡前"等模糊时间状语。
"""

    try:
        message = client.messages.create(
            model=os.environ.get("LLM_MODEL", "glm-4-plus"), # 默认使用 GLM-4-Plus，可配置
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"[错误] 生成 {copy_type} 失败: {e}")
        return f"生成失败: {e}"

def send_pushplus(token, title, content):
    """发送 PushPlus 通知"""
    url = "http://www.pushplus.plus/send"

    # 简单的 HTML 格式化
    html_content = content.replace("\n", "<br>")

    payload = {
        "token": token,
        "title": title,
        "content": html_content,
        "template": "html"
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"[推送] {resp.json()}")
        return True
    except Exception as e:
        print(f"[错误] 推送失败: {e}")
        return False

def main():
    print("启动蜗牛朋友圈文案生成器...")

    # 检查环境变量
    pushplus_token = os.environ.get("PUSHPLUS_TOKEN")
    if not pushplus_token:
        print("[警告] 未设置 PUSHPLUS_TOKEN，将只在控制台输出，不推送。")

    # 加载资源
    style_guide = load_file_content(STYLE_GUIDE_PATH)
    random_elements = load_file_content(RANDOM_ELEMENTS_PATH)

    client = get_client()
    if not client:
        return

    # 生成三篇文案
    today = datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d')
    results = []

    types = ["反馈篇", "上岸篇", "报名篇"]
    full_text = f"📅 {today} 蜗牛朋友圈文案备选\n\n"

    for t in types:
        print(f"正在生成 {t}...")
        copy = generate_copy(client, t, style_guide, random_elements)
        results.append({"type": t, "content": copy})

        full_text += f"➖➖➖➖ {t} ➖➖➖➖\n"
        full_text += copy + "\n\n"
        print(f"✅ {t} 生成完毕")

    # 输出到控制台
    print("\n" + "="*20 + "\n" + full_text + "\n" + "="*20)

    # 推送
    if pushplus_token:
        title = f"🐌 蜗牛文案 {today} (3条)"
        send_pushplus(pushplus_token, title, full_text)

if __name__ == "__main__":
    main()
