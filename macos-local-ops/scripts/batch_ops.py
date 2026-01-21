#!/usr/bin/env python3
"""
批量操作工具 - 批量重命名、移动和复制文件

安全第一: 默认启用 dry-run 模式，预览变更但不执行
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def match_files(path: str, pattern: str) -> list:
    """
    使用 glob 匹配文件

    Args:
        path: 搜索路径
        pattern: glob 模式（支持通配符）

    Returns:
        list: 匹配的文件路径列表
    """
    import glob

    expanded_path = os.path.expanduser(path)

    # 如果 pattern 包含路径分隔符，直接使用
    if os.path.dirname(pattern):
        search_pattern = os.path.join(expanded_path, pattern)
    else:
        search_pattern = os.path.join(expanded_path, pattern)

    files = glob.glob(search_pattern, recursive=True)

    # 过滤掉目录
    return [f for f in files if os.path.isfile(f)]


def preview_rename(files: list, pattern: str, replacement: str) -> list:
    """
    预览重命名操作

    Args:
        files: 文件列表
        pattern: 正则模式
        replacement: 替换字符串

    Returns:
        list: (旧路径, 新路径) 元组列表
    """
    changes = []

    try:
        regex = re.compile(pattern)
    except re.error as e:
        print(f"错误: 无效的正则表达式 '{pattern}': {e}", file=sys.stderr)
        return []

    for old_path in files:
        dirname = os.path.dirname(old_path)
        filename = os.path.basename(old_path)

        # 应用正则替换
        new_filename = regex.sub(replacement, filename)

        # 如果文件名有变化
        if new_filename != filename:
            new_path = os.path.join(dirname, new_filename)
            changes.append((old_path, new_path))

    return changes


def preview_move(files: list, dest: str) -> list:
    """
    预览移动操作

    Args:
        files: 文件列表
        dest: 目标目录

    Returns:
        list: (源路径, 目标路径) 元组列表
    """
    expanded_dest = os.path.expanduser(dest)

    # 确保目标目录存在
    if not os.path.exists(expanded_dest):
        print(f"错误: 目标目录不存在: {dest}", file=sys.stderr)
        return []

    changes = []
    for src_path in files:
        filename = os.path.basename(src_path)
        dst_path = os.path.join(expanded_dest, filename)
        changes.append((src_path, dst_path))

    return changes


def preview_copy(files: list, dest: str) -> list:
    """
    预览复制操作

    Args:
        files: 文件列表
        dest: 目标目录

    Returns:
        list: (源路径, 目标路径) 元组列表
    """
    return preview_move(files, dest)


def print_preview(changes: list, operation: str):
    """
    打印操作预览

    Args:
        changes: (源路径, 目标路径) 元组列表
        operation: 操作类型
    """
    if not changes:
        print("没有文件需要处理")
        return

    print(f"\n[预览] 将执行以下操作 ({operation}):\n")

    for idx, (src, dst) in enumerate(changes, 1):
        # 只显示文件名（如果路径太长）
        src_name = os.path.basename(src)
        dst_name = os.path.basename(dst)

        if os.path.dirname(src) != os.path.dirname(dst):
            # 移动/复制操作
            print(f"{idx}. {src_name}")
            print(f"   → {dst}")
        else:
            # 重命名操作
            print(f"{idx}. {src_name} → {dst_name}")

    print(f"\n共影响 {len(changes)} 个文件")


def confirm_action() -> bool:
    """
    请求用户确认

    Returns:
        bool: 用户是否确认
    """
    try:
        response = input("\n确认执行? [y/N]: ").strip().lower()
        return response in ['y', 'yes']
    except (EOFError, KeyboardInterrupt):
        print("\n操作已取消")
        return False


def execute_rename(changes: list) -> int:
    """
    执行重命名操作

    Args:
        changes: (源路径, 目标路径) 元组列表

    Returns:
        int: 成功重命名的文件数
    """
    success_count = 0

    for old_path, new_path in changes:
        try:
            # 检查目标文件是否已存在
            if os.path.exists(new_path):
                print(f"警告: 跳过（目标已存在）: {new_path}", file=sys.stderr)
                continue

            os.rename(old_path, new_path)
            success_count += 1
            print(f"✓ {os.path.basename(old_path)} → {os.path.basename(new_path)}")

        except Exception as e:
            print(f"错误: {old_path}: {e}", file=sys.stderr)

    return success_count


def execute_move(changes: list) -> int:
    """
    执行移动操作

    Args:
        changes: (源路径, 目标路径) 元组列表

    Returns:
        int: 成功移动的文件数
    """
    success_count = 0

    for src_path, dst_path in changes:
        try:
            # 检查目标文件是否已存在
            if os.path.exists(dst_path):
                print(f"警告: 跳过（目标已存在）: {dst_path}", file=sys.stderr)
                continue

            shutil.move(src_path, dst_path)
            success_count += 1
            print(f"✓ {os.path.basename(src_path)} → {dst_path}")

        except Exception as e:
            print(f"错误: {src_path}: {e}", file=sys.stderr)

    return success_count


def execute_copy(changes: list) -> int:
    """
    执行复制操作

    Args:
        changes: (源路径, 目标路径) 元组列表

    Returns:
        int: 成功复制的文件数
    """
    success_count = 0

    for src_path, dst_path in changes:
        try:
            # 检查目标文件是否已存在
            if os.path.exists(dst_path):
                print(f"警告: 跳过（目标已存在）: {dst_path}", file=sys.stderr)
                continue

            shutil.copy2(src_path, dst_path)
            success_count += 1
            print(f"✓ {os.path.basename(src_path)} → {dst_path}")

        except Exception as e:
            print(f"错误: {src_path}: {e}", file=sys.stderr)

    return success_count


def main():
    parser = argparse.ArgumentParser(
        description='批量操作工具 - 批量重命名、移动和复制文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 批量重命名（预览模式）
  %(prog)s rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_"

  # 批量重命名（确认后执行）
  %(prog)s rename --path ~/Desktop --pattern "^IMG_" --replacement "photo_" --execute

  # 批量移动（预览）
  %(prog)s move --path ~/Downloads --pattern "*.pdf" --dest ~/Documents/PDFs

  # 批量复制
  %(prog)s copy --path ~/Pictures --pattern "*.jpg" --dest ~/Backup

安全提示:
  - 默认启用 dry-run 模式，只预览不执行
  - 使用 --execute 参数确认执行操作
  - 目标文件已存在时会自动跳过
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='操作类型')

    # 重命名命令
    rename_parser = subparsers.add_parser('rename', help='批量重命名文件')
    rename_parser.add_argument('--path', '-p', default='.', help='文件所在路径（默认: 当前目录）')
    rename_parser.add_argument('--pattern', '-r', required=True, help='正则表达式模式')
    rename_parser.add_argument('--replacement', '-R', required=True, help='替换字符串')
    rename_parser.add_argument('--execute', '-e', action='store_true', help='执行操作（默认只预览）')
    rename_parser.add_argument('--force', '-f', action='store_true', help='强制执行，不询问确认')

    # 移动命令
    move_parser = subparsers.add_parser('move', help='批量移动文件')
    move_parser.add_argument('--path', '-p', default='.', help='文件所在路径（默认: 当前目录）')
    move_parser.add_argument('--pattern', '-r', required=True, help='glob 模式（支持通配符）')
    move_parser.add_argument('--dest', '-d', required=True, help='目标目录')
    move_parser.add_argument('--execute', '-e', action='store_true', help='执行操作（默认只预览）')
    move_parser.add_argument('--force', '-f', action='store_true', help='强制执行，不询问确认')

    # 复制命令
    copy_parser = subparsers.add_parser('copy', help='批量复制文件')
    copy_parser.add_argument('--path', '-p', default='.', help='文件所在路径（默认: 当前目录）')
    copy_parser.add_argument('--pattern', '-r', required=True, help='glob 模式（支持通配符）')
    copy_parser.add_argument('--dest', '-d', required=True, help='目标目录')
    copy_parser.add_argument('--execute', '-e', action='store_true', help='执行操作（默认只预览）')
    copy_parser.add_argument('--force', '-f', action='store_true', help='强制执行，不询问确认')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 根据命令执行操作
    if args.command == 'rename':
        files = match_files(args.path, '*')
        changes = preview_rename(files, args.pattern, args.replacement)
        print_preview(changes, '重命名')

        if args.execute or args.force:
            if not args.force and not confirm_action():
                print("操作已取消")
                sys.exit(0)

            count = execute_rename(changes)
            print(f"\n完成: 成功重命名 {count}/{len(changes)} 个文件")
        else:
            print("\n提示: 使用 --execute 参数执行操作")

    elif args.command == 'move':
        files = match_files(args.path, args.pattern)
        changes = preview_move(files, args.dest)
        print_preview(changes, '移动')

        if args.execute or args.force:
            if not args.force and not confirm_action():
                print("操作已取消")
                sys.exit(0)

            count = execute_move(changes)
            print(f"\n完成: 成功移动 {count}/{len(changes)} 个文件")
        else:
            print("\n提示: 使用 --execute 参数执行操作")

    elif args.command == 'copy':
        files = match_files(args.path, args.pattern)
        changes = preview_copy(files, args.dest)
        print_preview(changes, '复制')

        if args.execute or args.force:
            if not args.force and not confirm_action():
                print("操作已取消")
                sys.exit(0)

            count = execute_copy(changes)
            print(f"\n完成: 成功复制 {count}/{len(changes)} 个文件")
        else:
            print("\n提示: 使用 --execute 参数执行操作")

    sys.exit(0)


if __name__ == '__main__':
    main()
