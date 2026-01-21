#!/usr/bin/env python3
"""
智能搜索工具 - 使用多策略搜索文件和内容

支持两种搜索策略:
1. Spotlight (mdfind) - 搜索文件名
2. ripgrep (rg) - 搜索文件内容

支持按大小、时间、类型筛选结果
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def mdfind_search(query: str, path: str = None) -> list:
    """
    使用 Spotlight 搜索文件

    Args:
        query: 搜索关键词
        path: 搜索范围（None 表示全局搜索）

    Returns:
        list: 匹配的文件路径列表
    """
    cmd = ['mdfind', query]

    # 如果指定了路径，添加范围限制
    if path:
        expanded_path = os.path.expanduser(path)
        if os.path.exists(expanded_path):
            cmd.extend(['-onlyin', expanded_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return files
        return []
    except subprocess.TimeoutExpired:
        print("警告: 搜索超时", file=sys.stderr)
        return []
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return []


def rg_search(query: str, path: str = None) -> list:
    """
    使用 ripgrep 搜索文件内容

    Args:
        query: 搜索关键词（支持正则）
        path: 搜索范围

    Returns:
        list: 匹配的行（格式: 文件路径:行号:内容）
    """
    # 检查 ripgrep 是否安装
    try:
        subprocess.run(['rg', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 ripgrep (rg)", file=sys.stderr)
        print("安装: brew install ripgrep", file=sys.stderr)
        return []

    cmd = ['rg', query, '--no-heading', '--line-number', '--no-color']

    # 添加搜索路径
    if path:
        expanded_path = os.path.expanduser(path)
        cmd.append(expanded_path)
    else:
        cmd.append('.')

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 or result.returncode == 1:  # 1 表示没找到结果
            lines = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return lines
        return []
    except subprocess.TimeoutExpired:
        print("警告: 搜索超时", file=sys.stderr)
        return []
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return []


def parse_size_filter(size_str: str) -> tuple:
    """
    解析大小筛选字符串

    Examples:
        ">10M" → ('>', 10 * 1024 * 1024)
        "<1G"  → ('<', 1 * 1024 * 1024 * 1024)
        "100K" → ('=', 100 * 1024)
    """
    match = re.match(r'([><=]?)(\d+(?:\.\d+)?)([BKMG]?)', size_str.upper())
    if not match:
        return None

    operator = match.group(1) or '='
    value = float(match.group(2))
    unit = match.group(3) or 'B'

    # 转换为字节
    multipliers = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3}
    size_bytes = int(value * multipliers[unit])

    return (operator, size_bytes)


def filter_by_size(files: list, size_filter: tuple) -> list:
    """根据大小筛选文件"""
    operator, size_bytes = size_filter
    filtered = []

    for file_path in files:
        try:
            file_size = os.path.getsize(file_path)

            if operator == '>' and file_size > size_bytes:
                filtered.append(file_path)
            elif operator == '<' and file_size < size_bytes:
                filtered.append(file_path)
            elif operator == '=' and file_size == size_bytes:
                filtered.append(file_path)
            elif operator == '>=' and file_size >= size_bytes:
                filtered.append(file_path)
            elif operator == '<=' and file_size <= size_bytes:
                filtered.append(file_path)
        except OSError:
            continue

    return filtered


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'K', 'M', 'G']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}T"


def print_results(results: list, search_type: str, limit: int = 20):
    """打印搜索结果"""
    if not results:
        print("未找到结果")
        return

    # 限制输出数量
    display_results = results[:limit]

    print(f"\n找到 {len(results)} 个结果（显示前 {len(display_results)} 个）:\n")

    for idx, result in enumerate(display_results, 1):
        if search_type == 'content':
            # ripgrep 输出格式: 文件路径:行号:内容
            print(f"{idx}. {result}")
        else:
            # mdfind 输出格式: 文件路径
            file_path = result

            # 添加文件大小（如果存在）
            if os.path.exists(file_path):
                try:
                    size = format_size(os.path.getsize(file_path))
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    mtime_str = mtime.strftime("%Y-%m-%d %H:%M")
                    print(f"{idx}. [{size}] {mtime_str} - {file_path}")
                except OSError:
                    print(f"{idx}. {file_path}")
            else:
                print(f"{idx}. {file_path}")

    if len(results) > limit:
        print(f"\n... 还有 {len(results) - limit} 个结果未显示")


def main():
    parser = argparse.ArgumentParser(
        description='智能搜索工具 - 使用多策略搜索文件和内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 搜索文件名（使用 Spotlight）
  %(prog)s "项目文档"
  %(prog)s ".pdf" --path ~/Downloads

  # 按内容搜索（使用 ripgrep）
  %(prog)s "TODO" --type content --path ~/Documents

  # 按大小筛选
  %(prog)s ".pdf" --path ~/Downloads --size ">10M"

  # 组合搜索
  %(prog)s "发票" --path ~/Downloads --type name --limit 20
        """
    )

    parser.add_argument('query', help='搜索关键词')

    parser.add_argument(
        '--path', '-p',
        help='搜索范围（默认: 当前目录）',
        default='.'
    )

    parser.add_argument(
        '--type', '-t',
        choices=['name', 'content'],
        default='name',
        help='搜索类型: name（文件名）或 content（内容）'
    )

    parser.add_argument(
        '--size', '-s',
        help='按大小筛选（示例: ">10M", "<1G", "100K"）'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=20,
        help='最多显示结果数（默认: 20）'
    )

    args = parser.parse_args()

    # 执行搜索
    if args.type == 'name':
        results = mdfind_search(args.query, args.path)
    else:
        results = rg_search(args.query, args.path)

    # 应用大小筛选
    if args.size and args.type == 'name':
        size_filter = parse_size_filter(args.size)
        if size_filter:
            results = filter_by_size(results, size_filter)
        else:
            print(f"警告: 无效的大小筛选格式 '{args.size}'", file=sys.stderr)

    # 打印结果
    print_results(results, args.type, args.limit)

    sys.exit(0)


if __name__ == '__main__':
    main()
