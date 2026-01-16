# -*- coding: utf-8 -*-
"""
测试 PushPlus html 格式推送 base64 图片
"""
import requests
import base64
import json

# 读取图片并转 base64
image_path = "F:/选题抓取/20260106_FinancePro/daily_report.png"
with open(image_path, 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

# PushPlus token
token = "a6443f3a5d0f4b11a42c281f831b5c15"

# 使用 html 格式，嵌入 base64 图片
html_content = f'''
<html>
<body>
<h2>💰 小红书热点选题日报</h2>
<p>📊 报告已生成，请查看下图：</p>
<br>
<img src="data:image/png;base64,{img_base64}" style="max-width:100%;">
<br><br>
<p><small>报告生成时间: 2026-01-06</small></p>
</body>
</html>
'''

url = 'http://www.pushplus.plus/send'
data = {
    "token": token,
    "title": "💰 小红书热点选题 01-06",
    "content": html_content,
    "template": "html"
}

print("正在推送...")
response = requests.post(url, json=data, timeout=30)
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")

# 同时测试 json 格式
html_content2 = f'''
<h2>💰 小红书热点选题日报</h2>
<img src="data:image/png;base64,{img_base64}" style="max-width:100%;">
'''

data2 = {
    "token": token,
    "title": "💰 小红书热点选题 01-06",
    "content": html_content2,
    "template": "json"
}

print("\n使用 json 格式...")
response2 = requests.post(url, json=data2, timeout=30)
print(f"状态码: {response2.status_code}")
print(f"响应: {response2.json()}")
