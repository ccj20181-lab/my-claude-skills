# -*- coding: utf-8 -*-
"""
配置校验测试 (V6.1)
===================
测试 validate_config.py 的校验功能
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


def test_valid_config():
    """测试有效配置"""
    config = {
        "wechat_push_token": "a6443f3a5d0f4b11a42c281f831b5c15",
        "output_base_path": "/Users/henry/小红书选题抓取",
        "lite_mode": {
            "keywords": ["理财", "基金", "股票", "黄金", "存钱"],
            "min_likes": 500,
            "max_fans": 20000
        },
        "finance_pro_mode": {
            "keywords": ["理财", "基金", "股票", "副业", "搞钱", "存钱", "宏观经济", "黄金", "A股", "保险"],
            "min_likes": 1000,
            "max_fans": 20000
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)
        temp_path = f.name

    try:
        from validate_config import ConfigValidator
        validator = ConfigValidator(temp_path)
        result = validator.validate()

        assert result['status'] in ['success', 'warning'], f"期望成功，实际: {result['status']}"
        assert len(result['errors']) == 0, f"不应有错误: {result['errors']}"
        print("  [PASS] 有效配置测试通过")
        return True
    finally:
        os.unlink(temp_path)


def test_missing_token():
    """测试缺失token"""
    config = {
        "output_base_path": "/Users/henry/小红书选题抓取",
        "lite_mode": {
            "keywords": ["理财"]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)
        temp_path = f.name

    try:
        from validate_config import ConfigValidator
        validator = ConfigValidator(temp_path)
        result = validator.validate()

        assert result['status'] == 'error', f"期望错误，实际: {result['status']}"
        assert len(result['errors']) > 0, "应有错误信息"
        print("  [PASS] 缺失token测试通过")
        return True
    finally:
        os.unlink(temp_path)


def test_invalid_json():
    """测试无效JSON"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name

    try:
        from validate_config import ConfigValidator
        validator = ConfigValidator(temp_path)
        result = validator.validate()

        assert result['status'] == 'error', f"期望错误，实际: {result['status']}"
        print("  [PASS] 无效JSON测试通过")
        return True
    finally:
        os.unlink(temp_path)


def main():
    print("=" * 60)
    print("配置校验测试 (V6.1)")
    print("=" * 60)

    tests = [
        test_valid_config,
        test_missing_token,
        test_invalid_json,
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
