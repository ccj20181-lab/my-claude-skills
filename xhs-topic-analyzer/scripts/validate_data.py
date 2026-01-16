# -*- coding: utf-8 -*-
"""
数据完整性校验脚本 (V6.1 兼容增强版)
支持新旧两种数据格式的自动兼容
"""

import json, sys, os
from typing import Any, Dict, List


class FieldMapper:
    """字段映射器：自动兼容新旧数据格式"""
    
    FIELD_ALIASES = {
        'noteCard.displayTitle': 'title', 'displayTitle': 'title',
        'noteCard.user.nickname': 'nickname', 'author': 'nickname',
        'noteCard.user.userId': 'userId', 'userId': 'userId',
        'noteCard.user.fans': 'fans', 'user.fans': 'fans',
        'noteCard.interactInfo.likedCount': 'likedCount', 'likes': 'likedCount',
        'noteCard.interactInfo.collectedCount': 'collectedCount',
        'noteCard.interactInfo.commentCount': 'commentCount',
    }
    REQUIRED_FIELDS = ['id', 'title', 'nickname', 'fans', 'likedCount']
    
    @classmethod
    def normalize_feed(cls, feed: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {}
        if 'noteCard' in feed:
            note_card = feed['noteCard']
            user = note_card.get('user', {})
            interact = note_card.get('interactInfo', {})
            for key, value in note_card.items():
                if key == 'user':
                    for k, v in user.items(): normalized[k] = v
                elif key == 'interactInfo':
                    for k, v in interact.items(): normalized[k] = v
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


def validate_data_file(data_file: str, mode: str = 'finance-pro') -> Dict:
    print("=" * 60)
    print("数据完整性校验 (V6.1 兼容增强版)")
    print("=" * 60)
    
    result = {'status': 'success', 'errors': [], 'warnings': [], 'stats': {}}
    
    if not os.path.exists(data_file):
        result['status'] = 'error'
        result['errors'].append(f"文件不存在: {data_file}")
        print("  文件不存在")
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
        elif any(k in first for k in ['likedCount', 'nickname', 'fans']):
            print("  格式: simplified (新格式)")
        else:
            print("  格式: unknown")
    
    field_stats = {'has_fans': 0, 'fans_zero': 0, 'fans_missing': 0,
                   'likes_valid': 0, 'user_valid': 0, 'normalized': 0}
    
    for feed in feeds:
        normalized = FieldMapper.normalize_feed(feed)
        if all(normalized.get(f) for f in FieldMapper.REQUIRED_FIELDS):
            field_stats['normalized'] += 1
        
        fans = FieldMapper.get_field(feed, 'fans', default=0)
        likes = FieldMapper.get_field(feed, 'likedCount', 'likes', default=0)
        author = FieldMapper.get_field(feed, 'nickname', 'author', default='')
        
        if fans is not None and fans > 0:
            field_stats['has_fans'] += 1
        elif fans == 0:
            field_stats['fans_zero'] += 1
        else:
            field_stats['fans_missing'] += 1
        
        if likes and likes > 0:
            field_stats['likes_valid'] += 1
        if author:
            field_stats['user_valid'] += 1
    
    print(f"  字段标准化: {field_stats['normalized']}/{len(feeds)}")
    print(f"  有粉丝数据: {field_stats['has_fans']}/{len(feeds)}")
    print(f"  有效点赞数: {field_stats['likes_valid']}/{len(feeds)}")
    result['stats'] = field_stats
    
    min_likes = 1000 if mode == 'finance-pro' else 500
    max_fans = 20000 if mode == 'finance-pro' else float('inf')
    
    hits = []
    for feed in feeds:
        fans = FieldMapper.get_field(feed, 'fans', default=0)
        likes = FieldMapper.get_field(feed, 'likedCount', 'likes', default=0)
        title = FieldMapper.get_field(feed, 'title', 'displayTitle', default='')
        author = FieldMapper.get_field(feed, 'nickname', 'author', default='')
        if likes >= min_likes and fans < max_fans:
            hits.append({'title': title, 'likes': likes, 'fans': fans, 'author': author})
    
    print(f"  筛选条件: 点赞>={min_likes}, 粉丝<{max_fans}")
    print(f"  符合条件: {len(hits)} 条")
    result['stats']['hits'] = len(hits)
    
    if len(hits) < 5:
        result['warnings'].append(f"符合条件的笔记不足5条")
    
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
    mode = sys.argv[2] if len(sys.argv) > 2 else 'finance-pro'
    result = validate_data_file(data_file, mode)
    sys.exit(0 if result['status'] == 'success' else 1)
