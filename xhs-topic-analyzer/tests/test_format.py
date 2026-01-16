# -*- coding: utf-8 -*-
"""
格式兼容性测试 (V6.1)
=====================
测试 FieldMapper 对各种数据格式的兼容能力
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from validate_data import FieldMapper


def test_new_format():
    """测试新格式（简化字段）"""
    feed = {
        "id": "123",
        "title": "测试标题",
        "nickname": "测试博主",
        "fans": 5000,
        "likedCount": 1000,
        "collectedCount": 100,
        "commentCount": 50
    }

    normalized = FieldMapper.normalize_feed(feed)
    assert normalized['title'] == '测试标题'
    assert normalized['nickname'] == '测试博主'
    assert normalized['fans'] == 5000
    assert normalized['likedCount'] == 1000
    print("  [PASS] 新格式测试通过")


def test_legacy_format():
    """测试旧格式（嵌套结构）"""
    feed = {
        "id": "123",
        "xsecToken": "token123",
        "noteCard": {
            "displayTitle": "旧格式标题",
            "user": {
                "userId": "user123",
                "nickname": "旧博主",
                "fans": 3000
            },
            "interactInfo": {
                "likedCount": 500,
                "collectedCount": 50,
                "commentCount": 20
            }
        }
    }

    normalized = FieldMapper.normalize_feed(feed)
    assert normalized['title'] == '旧格式标题'
    assert normalized['nickname'] == '旧博主'
    assert normalized['fans'] == 3000
    assert normalized['likedCount'] == 500
    print("  [PASS] 旧格式测试通过")


def test_field_aliases():
    """测试字段别名"""
    # 测试 author -> nickname
    feed1 = {"id": "1", "title": "测试", "author": "昵称", "fans": 100, "likedCount": 50}
    assert FieldMapper.get_field(feed1, 'nickname', 'author') == '昵称'

    # 测试 likes -> likedCount
    feed2 = {"id": "2", "title": "测试", "nickname": "博主", "fans": 100, "likes": 999}
    assert FieldMapper.get_field(feed2, 'likedCount', 'likes') == 999

    print("  [PASS] 字段别名测试通过")


def test_missing_fields():
    """测试缺失字段处理"""
    feed = {"id": "123"}  # 缺少其他字段

    normalized = FieldMapper.normalize_feed(feed)
    assert normalized['title'] is None
    assert normalized['nickname'] is None
    assert normalized['fans'] is None
    assert normalized['likedCount'] is None

    print("  [PASS] 缺失字段测试通过")


def test_mixed_format():
    """测试混合格式"""
    feed = {
        "id": "123",
        "noteCard": {
            "displayTitle": "混合格式标题",
            "user": {
                "nickname": "博主",
                "fans": 2000
            }
        },
        "likedCount": 888,  # 新格式字段
        "author": "备用昵称"  # 别名字段
    }

    # 优先级：新格式 > 旧格式
    likes = FieldMapper.get_field(feed, 'likedCount', 'likes')
    assert likes == 888

    print("  [PASS] 混合格式测试通过")


def main():
    print("=" * 60)
    print("格式兼容性测试 (V6.1)")
    print("=" * 60)

    tests = [
        test_new_format,
        test_legacy_format,
        test_field_aliases,
        test_missing_fields,
        test_mixed_format,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__} 异常: {e}")
            failed += 1

    print("-" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
