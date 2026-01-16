# -*- coding: utf-8 -*-
"""
端到端管道测试 (V6.1)
=====================
测试完整执行流程
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def test_data_validation():
    """测试数据校验流程"""
    test_data = {
        "feeds": [
            {"id": "1", "title": "测试1", "nickname": "博主1", "fans": 5000, "likedCount": 1000},
            {"id": "2", "title": "测试2", "nickname": "博主2", "fans": 8000, "likedCount": 600},
            {"id": "3", "title": "测试3", "nickname": "博主3", "fans": 15000, "likedCount": 2000},
        ],
        "keywords": ["理财", "基金", "股票", "黄金", "存钱"],
        "fetched_at": "2026-01-07T18:00:00",
        "mode": "lite",
        "keywords_executed": ["理财", "基金", "股票", "黄金", "存钱"]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_path = f.name

    try:
        from validate_data import validate_data_file
        result = validate_data_file(temp_path, 'lite')

        assert result['status'] == 'success', f"期望成功，实际: {result['status']}"
        assert result['stats']['hits'] >= 2, f"应有至少2条符合条件，实际: {result['stats']['hits']}"
        print("  [PASS] 数据校验流程测试通过")
        return True
    finally:
        os.unlink(temp_path)


def test_keyword_validation():
    """测试关键词校验"""
    test_data = {
        "feeds": [],
        "keywords_executed": ["理财", "基金", "股票", "黄金", "存钱"]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_path = f.name

    try:
        from validate_data import validate_keywords
        expected = ["理财", "基金", "股票", "黄金", "存钱"]
        result = validate_keywords(temp_path, expected)

        assert result['status'] == 'success', f"期望成功，实际: {result['status']}"
        assert len(result['missing']) == 0, f"不应有缺失关键词: {result['missing']}"
        print("  [PASS] 关键词校验测试通过")
        return True
    finally:
        os.unlink(temp_path)


def test_legacy_data_compatibility():
    """测试旧格式数据兼容"""
    test_data = {
        "feeds": [
            {
                "id": "1",
                "noteCard": {
                    "displayTitle": "旧格式标题",
                    "user": {"nickname": "旧博主", "fans": 3000},
                    "interactInfo": {"likedCount": 800}
                }
            }
        ],
        "keywords_executed": ["理财"]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_path = f.name

    try:
        from validate_data import validate_data_file
        result = validate_data_file(temp_path, 'lite')

        assert result['status'] == 'success', f"期望成功，实际: {result['status']}"
        assert result['stats']['likes_valid'] == 1, f"应有1条有效点赞数，实际: {result['stats']['likes_valid']}"
        print("  [PASS] 旧格式兼容测试通过")
        return True
    finally:
        os.unlink(temp_path)


def main():
    print("=" * 60)
    print("端到端管道测试 (V6.1)")
    print("=" * 60)

    tests = [
        test_data_validation,
        test_keyword_validation,
        test_legacy_data_compatibility,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
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
