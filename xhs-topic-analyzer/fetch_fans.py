#!/usr/bin/env python3
"""
获取小红书博主粉丝数据
使用小红书 MCP 的 cookies 访问 API
"""
import json
import requests
import time
import re
from pathlib import Path

# 数据文件路径
DATA_DIR = Path("/Users/henry/.claude/skills/xhs-topic-analyzer")
DATA_FILE = DATA_DIR / "data.json"
FANS_FILE = DATA_DIR / "fans.json"
COOKIE_FILE = Path("/Users/henry/.mcp/rednote/cookies.json")

def parse_fans_count(fans_str):
    """解析粉丝数字符串为数字"""
    if not fans_str:
        return 0

    fans_str = str(fans_str).strip()

    # 处理 "1.2万" 格式
    if '万' in fans_str:
        match = re.search(r'([\d.]+)\s*万', fans_str)
        if match:
            return int(float(match.group(1)) * 10000)

    # 处理 "3,456" 格式 - 去掉逗号
    fans_str = fans_str.replace(',', '').replace('+', '').replace('人', '').replace('粉丝', '').replace('关注', '')

    # 提取数字
    match = re.search(r'(\d+)', fans_str)
    if match:
        return int(match.group(1))

    return 0


def load_cookies():
    """加载小红书 cookies"""
    try:
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)

        # 转换为 requests 格式
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']

        return cookie_dict
    except Exception as e:
        print(f"加载 cookies 失败: {e}")
        return {}


def get_user_info_by_note(note_id, cookies):
    """通过笔记ID获取用户信息"""
    # 小红书 API 端点
    api_url = "https://edith.xiaohongshu.com/api/sns/web/v1/feed"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.xiaohongshu.com/',
        'Accept': 'application/json, text/plain, */*',
    }

    params = {
        'source_note_id': note_id,
        'image_formats': 'jpg,webp,avif',
        'extra': '{"need_body_topic":"1"}',
    }

    try:
        response = requests.get(api_url, params=params, headers=headers, cookies=cookies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                items = data['data']['items']
                if items and len(items) > 0:
                    note = items[0]['note_card']
                    if 'user' in note:
                        user = note['user']
                        return {
                            'nickname': user.get('nickname', ''),
                            'user_id': user.get('user_id', ''),
                            'fans_count': user.get('follower_count', 0),
                            'avatar': user.get('avatar', ''),
                        }
        return None
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return None


def get_user_info_from_profile(nickname, cookies):
    """通过用户主页搜索获取用户信息"""
    # 尝试通过搜索 API
    search_api = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.xiaohongshu.com/',
        'Accept': 'application/json, text/plain, */*',
    }

    params = {
        'keyword': nickname,
        'page': 1,
        'page_size': 20,
        'search_id': '',
        'sort': 'general',
        'note_type': '0',
    }

    try:
        response = requests.get(search_api, params=params, headers=headers, cookies=cookies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                items = data['data']['items']
                for item in items:
                    if item.get('model_type') == 'note':
                        note = item.get('note_card', {})
                        user = note.get('user', {})
                        if user.get('nickname') == nickname:
                            return {
                                'nickname': user.get('nickname', ''),
                                'user_id': user.get('user_id', ''),
                                'fans_count': user.get('follower_count', 0),
                                'avatar': user.get('avatar', ''),
                            }
        return None
    except Exception as e:
        print(f"搜索用户失败: {e}")
        return None


def main():
    # 读取 data.json
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取唯一博主和对应的笔记ID
    user_notes = {}
    for feed in data['feeds']:
        nickname = feed['nickname']
        if nickname not in user_notes:
            user_notes[nickname] = {
                'id': feed['id'],
                'url': f"https://www.xiaohongshu.com/explore/{feed['id']}"
            }

    print(f"总共唯一博主数: {len(user_notes)}")

    # 加载缓存
    fans_cache = {}
    if FANS_FILE.exists():
        with open(FANS_FILE, 'r', encoding='utf-8') as f:
            fans_cache = json.load(f)
        print(f"从缓存加载了 {len(fans_cache)} 个博主的粉丝数据")

    # 加载 cookies
    cookies = load_cookies()
    if not cookies:
        print("无法加载 cookies，退出")
        return

    # 获取粉丝数据
    results = {}
    from_cache = 0
    fetched = 0
    failed = []

    for i, (nickname, note_info) in enumerate(user_notes.items(), 1):
        print(f"\n[{i}/{len(user_notes)}] 处理: {nickname}")

        if nickname in fans_cache:
            results[nickname] = fans_cache[nickname]
            from_cache += 1
            print(f"  从缓存: {fans_cache[nickname]}")
            continue

        # 尝试通过笔记获取用户信息
        user_info = get_user_info_by_note(note_info['id'], cookies)

        if user_info and user_info['fans_count']:
            fans_count = user_info['fans_count']
            results[nickname] = fans_count
            fetched += 1
            print(f"  获取成功: {fans_count} 粉丝")
        else:
            # 尝试通过搜索获取
            print(f"  笔记API失败，尝试搜索...")
            user_info = get_user_info_from_profile(nickname, cookies)
            if user_info and user_info['fans_count']:
                fans_count = user_info['fans_count']
                results[nickname] = fans_count
                fetched += 1
                print(f"  搜索成功: {fans_count} 粉丝")
            else:
                results[nickname] = 0
                failed.append(nickname)
                print(f"  获取失败")

        # 防止请求过快
        time.sleep(1)

    # 保存 fans.json
    with open(FANS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # 更新 data.json
    for feed in data['feeds']:
        nickname = feed.get('nickname')
        if nickname in results:
            feed['fans'] = results[nickname]
        else:
            feed['fans'] = 0

    data['with_fans_data'] = True
    data['fans_fetched_at'] = time.strftime("%Y-%m-%dT%H:%M:%S")

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 输出摘要
    summary = {
        "status": "success",
        "users_visited": len(user_notes),
        "fans_collected": fetched,
        "fans_from_cache": from_cache,
        "missing_fans": len(failed)
    }

    print("\n" + "="*50)
    print("任务完成!")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("="*50)

    if failed:
        print(f"\n未获取到粉丝数的博主:")
        for name in failed:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
