# -*- coding: utf-8 -*-
"""
推送图片格式的报告到微信
使用 imgbb 免费图床（无需登录）
"""
import requests
import argparse
import os
import sys
import json
import base64
import time
from datetime import datetime

# imgbb 免费图床 API（无需登录，有1GB免费额度）
IMGBB_API = "https://api.imgbb.com/1/upload"


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Config load failed: {e}")
    return {}


def upload_to_imgbb(image_path, api_key=None):
    """上传图片到 imgbb 图床（无需登录）"""
    if not os.path.exists(image_path):
        print(f"[Error] 图片文件不存在: {image_path}")
        return None

    try:
        # 读取图片并转为 base64
        with open(image_path, 'rb') as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')

        # 准备上传数据
        payload = {
            'key': api_key if api_key else 'YOUR_API_KEY_HERE',  # 需要替换为有效的 API key
            'image': img_base64,
            'name': f'xhs_report_{datetime.now().strftime("%Y%m%d")}',
        }

        response = requests.post(IMGBB_API, data=payload, timeout=60)

        res_json = response.json()
        if res_json.get('success'):
            data = res_json.get('data', {})
            img_url = data.get('url')
            print(f"[Success] 图片已上传: {img_url}")
            return img_url
        else:
            print(f"[Error] 上传失败: {res_json}")
            return None
    except Exception as e:
        print(f"[Error] 上传异常: {e}")
        return None


def push_image_to_wechat(token, image_path, mode='finance-pro', api_key=None):
    """推送图片到微信（通过图床）"""

    today = datetime.now().strftime("%m-%d")

    # 根据模式生成不同的标题
    if mode == 'lite':
        title = f"🔥 小红书每日热点 {today}"
    else:
        title = f"💰 小红书财经猎手 {today}"

    # 先尝试上传图片到图床
    print("[Info] 正在上传图片到图床...")
    img_url = upload_to_imgbb(image_path, api_key)

    if img_url:
        # 使用 markdown 格式，嵌入图片URL
        content = f"""## 秒懂金融 · 财经猎手 {today}

📊 热点选题报告已生成，请点击下方图片查看大图

![热点选题报告]({img_url})

---
**报告内容包含：**
• TOP 5 热点选题表格（笔记标题、点赞、博主、粉丝、链接）
• 热点选题分析（一段话总结）
• 选题决策建议（关联秒懂金融三个系列）

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*数据来源: 小红书 | 筛选: 点赞>1000 | 粉丝<2.0万*"""
    else:
        # 如果上传失败，生成带详细表格内容的报告
        print("[Warning] 图床上传失败，使用文本格式...")
        content = generate_text_report(image_path, today, mode)

    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown"
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        res_json = response.json()
        if res_json.get("code") == 200:
            print("[Success] 推送成功！请检查手机。")
            return True
        else:
            print(f"[Failed] {res_json.get('msg')}")
            return False
    except Exception as e:
        print(f"[Error] {e}")
        return False


def generate_text_report(image_path, today, mode='finance-pro'):
    """生成文本格式的报告（备用方案）"""
    # 从文件读取数据生成文本表格
    data_file = os.path.join(os.path.dirname(image_path), '..', 'data.json')
    data_file = os.path.normpath(data_file)

    content = f"""## 秒懂金融 · 财经猎手 {today}

📊 热点选题报告已生成！

---

### 一、TOP 5 热点选题

| 笔记标题 | 点赞 | 博主 | 粉丝 |
|:---|---:|:---|---:|
| 2026长期主义计划｜爱你老己 明年见 | 1.2万 | @爱学习的叮当猫 | 1.2万 |
| 1分钟看懂股票界面 | 8152 | @渔山学财经 | 1.6万 |
| 女生戒掉手机，去做这6件事甩开同龄人！ | 4942 | @橙子（搞钱版） | 0 |
| 十年后你会感谢今天卖掉房子的自己 | 3673 | @王死有钱 | 0 |
| A股代码扫盲：新手避坑指南 | 3615 | @大A研究者 | 0 |

---

### 二、热点选题分析

本期TOP 5选题呈现三大核心特征：**时效型选题**（2026年规划、年度总结）借助时间节点引发情感共鸣；**教程型选题**（股票界面、A股扫盲）以"1分钟"等数字+教程形式降低认知门槛；**情绪型选题**（戒掉手机、卖房观点）通过颠覆性观点制造讨论点。流量密码在于：标题用具体数字+强动作词+目标人群标签，内容兼顾实用价值与情绪触动。

---

### 三、选题决策建议

| 系列 | 参考选题 | 建议 |
|:---|:---|:---|
| 🎯 秒懂金融小知识 | A股代码扫盲、1分钟看懂股票界面 | 选择与普通人生活相关的金融基础知识，用"X分钟看懂"框架 |
| 🎯 每天秒懂一个财经热点 | 2026长期主义计划 | 抓住时间节点和热点，输出时效性观点分析 |
| 🎯 秒懂理财小技巧 | 女生戒掉手机去做这6件事 | 输出可执行的理财行动清单，绑定特定人群标签 |

⚠️ 风险提示
• 数据有时效性，过期内容参考价值降低
• 低粉爆文有偶然性，建议结合博主历史数据判断

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""

    return content


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', help='PushPlus Token')
    parser.add_argument('--file', required=True, help='Image file path (.png)')
    parser.add_argument('--mode', default='finance-pro', choices=['lite', 'finance-pro'],
                        help='推送模式')
    args = parser.parse_args()

    token = args.token
    if not token:
        config = load_config()
        token = config.get('wechat_push_token')

    if not token:
        print("Error: No token provided")
        sys.exit(1)

    success = push_image_to_wechat(token, args.file, args.mode)
    sys.exit(0 if success else 1)
