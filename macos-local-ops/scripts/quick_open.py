#!/usr/bin/env python3
"""
智能打开工具 - 快速打开文件、文件夹和应用

快捷别名:
  d      → ~/Desktop
  doc    → ~/Documents
  down   → ~/Downloads
  pics   → ~/Pictures
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# 快捷别名配置
ALIASES = {
    'd': '~/Desktop',
    'desktop': '~/Desktop',
    'doc': '~/Documents',
    'documents': '~/Documents',
    'down': '~/Downloads',
    'downloads': '~/Downloads',
    'pics': '~/Pictures',
    'pictures': '~/Pictures',
}


def expand_path(path: str) -> str:
    """展开路径中的 ~ 和快捷别名"""
    # 检查是否为快捷别名
    if path in ALIASES:
        path = ALIASES[path]

    # 展开 ~
    path = os.path.expanduser(path)

    # 转换为绝对路径
    return os.path.abspath(path)


def find_app_by_name(app_name: str) -> str:
    """模糊匹配应用名称"""
    app_name_lower = app_name.lower()

    # 常见应用目录
    search_paths = [
        '/Applications',
        '/System/Applications',
        os.path.expanduser('~/Applications'),
    ]

    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue

        for item in os.listdir(base_path):
            if item.lower().startswith(app_name_lower) and item.endswith('.app'):
                return os.path.join(base_path, item)

    # 如果没有找到，返回原始名称（可能是完整名称）
    return app_name


def open_item(path: str, app: str = None) -> bool:
    """
    打开文件、文件夹或应用

    Args:
        path: 路径（支持快捷别名和 ~）
        app: 指定使用哪个应用打开

    Returns:
        bool: 是否成功打开
    """
    # 展开路径
    expanded_path = expand_path(path)

    # 检查路径是否存在
    if not os.path.exists(expanded_path):
        # 尝试作为应用名称查找
        app_path = find_app_by_name(path)
        if os.path.exists(app_path):
            expanded_path = app_path
        else:
            print(f"错误: 路径 '{path}' 不存在", file=sys.stderr)
            print(f"展开后: {expanded_path}", file=sys.stderr)
            return False

    # 构建命令
    cmd = ['open']

    if app:
        cmd.extend(['-a', app])

    cmd.append(expanded_path)

    # 执行命令
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"错误: {result.stderr}", file=sys.stderr)
            return False

        # 打印成功信息
        item_type = "应用" if expanded_path.endswith('.app') else "文件夹" if os.path.isdir(expanded_path) else "文件"
        print(f"已打开 {item_type}: {expanded_path}")
        return True

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='智能打开工具 - 快速打开文件、文件夹和应用',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
快捷别名:
  d, desktop      → ~/Desktop
  doc, documents  → ~/Documents
  down, downloads → ~/Downloads
  pics, pictures  → ~/Pictures

示例:
  %(prog)s d                    # 打开桌面
  %(prog)s ~/Documents          # 打开文档目录
  %(prog)s report.pdf           # 打开文件
  %(prog)s safari               # 打开 Safari 应用
  %(prog)s . -a TextEdit        # 用 TextEdit 打开当前目录
        """
    )

    parser.add_argument(
        'path',
        nargs='?',
        default='d',
        help='路径、文件名或应用名（默认: d）'
    )

    parser.add_argument(
        '-a', '--app',
        help='指定使用哪个应用打开'
    )

    args = parser.parse_args()

    # 打开项目
    success = open_item(args.path, args.app)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
