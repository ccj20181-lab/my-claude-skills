#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ 已废弃：此脚本已废弃，请使用 main.py

逐张生成财经信息图 - 旧版兼容脚本
此脚本保留仅用于向后兼容，新功能请使用 scripts/main.py

推荐用法：
    python scripts/main.py "content/主题.md" --topic "主题名"
"""
import sys
import warnings
from pathlib import Path

# Show deprecation warning
warnings.warn(
    "\n" + "="*60 + "\n"
    "⚠️  generate_one_by_one.py 已废弃！\n"
    "请使用 main.py 作为主入口脚本。\n"
    "\n"
    "新用法：\n"
    "  python scripts/main.py \"file.md\" --topic \"主题\"\n"
    "="*60,
    DeprecationWarning,
    stacklevel=2
)

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.session import Session
from src.workflow import Workflow
from src.utils import logger


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='[已废弃] 逐张生成财经信息图 - 请使用 main.py',
        epilog='⚠️ 此脚本已废弃，建议使用: python scripts/main.py'
    )
    parser.add_argument('md_file', help='md文件路径')
    parser.add_argument('-r', '--resolution', choices=['1K', '2K', '4K'], default='4K', help='分辨率')
    parser.add_argument('-o', '--output', default=None, help='输出目录')
    parser.add_argument('--api', '--provider', dest='provider',
                        choices=['google', 'nanobanana'], help='API 选择')
    parser.add_argument('--topic', default=None, help='主题文件夹名称')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式模式')
    parser.add_argument('--debug', action='store_true', help='开启调试日志')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel('DEBUG')

    try:
        # Load config
        config = Config.load()

        # Override with CLI args
        if args.provider:
            config.api.provider = args.provider
        if args.output:
            config.output.base_dir = args.output
        if args.resolution:
            config.output.resolution = args.resolution

        # Use filename as topic if not specified
        topic = args.topic or Path(args.md_file).stem

        # Initialize session and workflow
        session = Session(topic, config)
        workflow = Workflow(config, session)

        # Run with single file
        md_path = Path(args.md_file).resolve()
        workflow.run([md_path], None, args.interactive)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
