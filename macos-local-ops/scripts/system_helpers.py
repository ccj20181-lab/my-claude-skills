#!/usr/bin/env python3
"""
系统辅助工具 - 系统通知、剪贴板和截图操作

支持三大功能:
1. 系统通知 (notify) - 发送 macOS 通知
2. 剪贴板 (clipboard) - 复制/粘贴剪贴板内容
3. 截图 (screenshot) - 截取屏幕或选中区域
"""

import argparse
import os
import subprocess
import sys


def send_notification(title: str, message: str, sound: str = 'Glass'):
    """
    发送系统通知

    Args:
        title: 通知标题
        message: 通知内容
        sound: 通知声音（默认: Glass）
    """
    script = f'display notification "{message}" with title "{title}" sound name "{sound}"'

    try:
        subprocess.run(['osascript', '-e', script], check=True)
        print(f"已发送通知: {title} - {message}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 发送通知失败: {e}", file=sys.stderr)
        return False


def clipboard_copy(text: str = None):
    """
    复制文本到剪贴板

    Args:
        text: 要复制的文本（None 表示从 stdin 读取）
    """
    if text is None:
        # 从 stdin 读取
        text = sys.stdin.read()

    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))

        if process.returncode == 0:
            print(f"已复制 {len(text)} 个字符到剪贴板")
            return True
        else:
            print("错误: 复制失败", file=sys.stderr)
            return False
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return False


def clipboard_paste():
    """
    从剪贴板粘贴文本

    Returns:
        str: 剪贴板内容
    """
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
        content = result.stdout
        print(content)
        return content
    except subprocess.CalledProcessError as e:
        print(f"错误: 读取剪贴板失败: {e}", file=sys.stderr)
        return None


def take_screenshot(path: str, selection: bool = False, delay: int = 0):
    """
    截取屏幕

    Args:
        path: 保存路径
        selection: 是否截取选中区域
        delay: 延迟秒数
    """
    # 展开路径
    expanded_path = os.path.expanduser(path)

    # 确保目录存在
    dirname = os.path.dirname(expanded_path)
    if dirname and not os.path.exists(dirname):
        print(f"错误: 目录不存在: {dirname}", file=sys.stderr)
        return False

    # 构建命令
    cmd = ['screencapture']

    if selection:
        cmd.append('-i')  # 交互式选择区域

    if delay > 0:
        cmd.extend(['-T', str(delay)])  # 延迟

    cmd.append(expanded_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"截图已保存: {expanded_path}")
            return True
        else:
            print(f"错误: 截图失败: {result.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='系统辅助工具 - 系统通知、剪贴板和截图操作',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 发送系统通知
  %(prog)s notify "任务完成" "所有文件已处理完毕"

  # 复制到剪贴板
  echo "重要文本" | %(prog)s clipboard copy
  %(prog)s clipboard copy "直接复制这段文本"

  # 读取剪贴板
  %(prog)s clipboard paste

  # 截取屏幕（保存到桌面）
  %(prog)s screenshot ~/Desktop/screenshot.png

  # 截取选中区域
  %(prog)s screenshot ~/Desktop/selection.png --selection

  # 延迟 5 秒截图
  %(prog)s screenshot ~/Desktop/screenshot.png --delay 5

可用的通知声音:
  Glass, Ping, Pop, Purr, Sosumi, Blow, Bottle, Frog, Funk, Morse, Tink
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='功能类型')

    # 通知命令
    notify_parser = subparsers.add_parser('notify', help='发送系统通知')
    notify_parser.add_argument('title', help='通知标题')
    notify_parser.add_argument('message', help='通知内容')
    notify_parser.add_argument('--sound', '-s', default='Glass', help='通知声音（默认: Glass）')

    # 剪贴板命令
    clipboard_parser = subparsers.add_parser('clipboard', help='剪贴板操作')
    clipboard_subparsers = clipboard_parser.add_subparsers(dest='clipboard_action', help='剪贴板操作')

    clipboard_copy_parser = clipboard_subparsers.add_parser('copy', help='复制到剪贴板')
    clipboard_copy_parser.add_argument('text', nargs='?', help='要复制的文本（留空则从 stdin 读取）')

    clipboard_subparsers.add_parser('paste', help='从剪贴板粘贴')

    # 截图命令
    screenshot_parser = subparsers.add_parser('screenshot', help='截取屏幕')
    screenshot_parser.add_argument('path', help='保存路径')
    screenshot_parser.add_argument('--selection', '-s', action='store_true', help='截取选中区域')
    screenshot_parser.add_argument('--delay', '-d', type=int, default=0, help='延迟秒数')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行对应命令
    if args.command == 'notify':
        success = send_notification(args.title, args.message, args.sound)
        sys.exit(0 if success else 1)

    elif args.command == 'clipboard':
        if args.clipboard_action == 'copy':
            if args.text:
                success = clipboard_copy(args.text)
            else:
                success = clipboard_copy()
            sys.exit(0 if success else 1)

        elif args.clipboard_action == 'paste':
            content = clipboard_paste()
            sys.exit(0 if content is not None else 1)

        else:
            clipboard_parser.print_help()
            sys.exit(1)

    elif args.command == 'screenshot':
        success = take_screenshot(args.path, args.selection, args.delay)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
