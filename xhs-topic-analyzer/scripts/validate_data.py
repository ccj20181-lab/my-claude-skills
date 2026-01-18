# -*- coding: utf-8 -*-
"""
数据完整性校验脚本 (V8.0 - 移除粉丝数据依赖)
专注于财经赛道爆款笔记：3天内 + 2000赞以上
"""

import json, sys, os
from typing import Any, Dict, List


class FieldMapper:
    """字段映射器：自动兼容新旧数据格式"""

    FIELD_ALIASES = {
        'noteCard.displayTitle': 'title', 'displayTitle': 'title',
        'noteCard.user.nickname': 'nickname', 'author': 'nickname',
        'noteCard.interactInfo.likedCount': 'likedCount', 'likes': 'likedCount',
        'noteCard.interactInfo.collectedCount': 'collectedCount',
        'noteCard.interactInfo.commentCount': 'commentCount',
    }
    # 移除 fans 字段要求
    REQUIRED_FIELDS = ['id', 'title', 'nickname', 'likedCount']

    @classmethod
    def normalize_feed(cls, feed: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        if 'noteCard' in feed:
            note_card = feed['noteCard']
            user = note_card.get('user', {})
            interact = note_card.get('interactInfo', {})
            for key, value in note_card.items():
                if key == 'user':
                    for k, v in user.items():
                        normalized[k] = v
                elif key == 'interactInfo':
                    for k, v in interact.items():
                        normalized[k] = v
                else:
                    normalized[key] = value
            normalized['xsecToken'] = feed.get('xsecToken', '')
            normalized['id'] = feed.get('id', '')
        else:
            normalized = dict(feed)

        for old_name, new_name in cls.FIELD_ALIASES.items():
            if old_name in normalized:
                normalized[new_name] = normalized.pop(old_name)

        for field in cls.REQUIRED_FIELDS:
            if field not in normalized:
                normalized[field] = None
        return normalized

    @classmethod
    def get_field(cls, feed: Dict[str, Any], *keys, default: Any = None) -> Any:
        for key in keys:
            if key in feed and feed[key] is not None:
                return feed[key]
        normalized = cls.normalize_feed(feed)
        for key in keys:
            if key in normalized and normalized[key] is not None:
                return normalized[key]
        return default


def validate_data_file(data_file: str) -> Dict:
    print("=" * 60)
    print("数据完整性校验 (V8.0 - 无粉丝数据依赖)")
    print("=" * 60)

    result = {'status': 'success', 'errors': [], 'warnings': [], 'stats': {}}

    if not os.path.exists(data_file):
        result['status'] = 'error'
        result['errors'].append(f"文件不存在: {data_file}")
        print(f"  文件不存在: {data_file}")
        return result

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        result['status'] = 'error'
        result['errors'].append(f"JSON解析错误: {e}")
        print(f"  JSON解析错误: {e}")
        return result

    feeds = data.get('feeds', [])
    if not isinstance(feeds, list):
        result['status'] = 'error'
        result['errors'].append("feeds字段必须是数组")
        print("  feeds字段格式错误")
        return result

    print(f"  笔记总数: {len(feeds)}")

    if feeds:
        first = feeds[0]
        if 'noteCard' in first:
            print("  格式: legacy (noteCard嵌套结构)")
        elif any(k in first for k in ['likedCount', 'nickname']):
            print("  格式: simplified (新格式)")
        else:
            print("  格式: unknown")

    field_stats = {
        'likes_valid': 0,
        'user_valid': 0,
        'normalized': 0
    }

    for feed in feeds:
        normalized = FieldMapper.normalize_feed(feed)
        if all(normalized.get(f) for f in FieldMapper.REQUIRED_FIELDS):
            field_stats['normalized'] += 1

        likes = FieldMapper.get_field(feed, 'likedCount', 'likes', default=0)
        author = FieldMapper.get_field(feed, 'nickname', 'author', default='')

        if likes and likes > 0:
            field_stats['likes_valid'] += 1
        if author:
            field_stats['user_valid'] += 1

    print(f"  字段标准化: {field_stats['normalized']}/{len(feeds)}")
    print(f"  有效点赞数: {field_stats['likes_valid']}/{len(feeds)}")
    print(f"  有效作者名: {field_stats['user_valid']}/{len(feeds)}")
    result['stats'] = field_stats

    # 财经赛道爆款标准：2000赞以上
    min_likes = 2000

    hits = []
    for feed in feeds:
        likes = FieldMapper.get_field(feed, 'likedCount', 'likes', default=0)
        title = FieldMapper.get_field(feed, 'title', 'displayTitle', default='')
        author = FieldMapper.get_field(feed, 'nickname', 'author', default='')
        if likes >= min_likes:
            hits.append({'title': title, 'likes': likes, 'author': author})

    print(f"  筛选条件: 点赞>={min_likes}")
    print(f"  符合条件: {len(hits)} 条")
    result['stats']['hits'] = len(hits)

    if len(hits) < 5:
        result['warnings'].append(f"符合条件的笔记不足5条")
        print(f"  ⚠️ 警告: 符合条件的笔记不足5条")

    print("=" * 60)
    if result['errors']:
        result['status'] = 'error'
        print("状态: 失败")
    elif result['warnings']:
        result['status'] = 'warning'
        print("状态: 有警告")
    else:
        print("状态: 通过")

    return result


if __name__ == '__main__':
    data_file = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
    result = validate_data_file(data_file)
    sys.exit(0 if result['status'] == 'success' else 1)
