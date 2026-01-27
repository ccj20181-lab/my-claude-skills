#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ 已废弃：此脚本已废弃，请使用 main.py

批量生成财经信息图 - 旧版兼容脚本
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
    "⚠️  batch_generate.py 已废弃！\n"
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
        description='[已废弃] 批量生成财经信息图 - 请使用 main.py',
        epilog='⚠️ 此脚本已废弃，建议使用: python scripts/main.py'
    )
    parser.add_argument('md_files', nargs='+', help='md 文件路径列表')
    parser.add_argument('-r', '--resolution', default='4K', choices=['1K', '2K', '4K'], help='分辨率')
    parser.add_argument('--api', '--provider', dest='provider', default=None,
                        choices=['google', 'nanobanana'], help='API 选择')
    parser.add_argument('--topic', '-t', default='default', help='主题名称（创建文件夹）')
    parser.add_argument('--titles', nargs='+', help='主标题列表（与md文件对应）')
    parser.add_argument('-o', '--output', default=None, help='输出目录')
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

        # Initialize session and workflow
        session = Session(args.topic, config)
        workflow = Workflow(config, session)

        # Run
        md_paths = [Path(f).resolve() for f in args.md_files]
        workflow.run(md_paths, args.titles, args.interactive)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
