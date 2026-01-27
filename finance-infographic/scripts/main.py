#!/usr/bin/env python3
"""
Finance Infographic Generator - Main Entry Script

Usage:
    python scripts/main.py "content/主题.md" --topic "主题名"
    python scripts/main.py "md1.md" "md2.md" --titles "是什么" "为什么" --topic "主题"
"""
import sys
import io
import argparse
from pathlib import Path

# Handle Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project root to path so src can be imported
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from src.config import Config
from src.session import Session
from src.workflow import Workflow
from src.utils import logger
from src import __version__

def main():
    parser = argparse.ArgumentParser(
        description=f'Finance Infographic Generator v{__version__}',
        epilog='''
Examples:
  python scripts/main.py "content/主题.md" --topic "主题名"
  python scripts/main.py "md1.md" "md2.md" --titles "是什么" "为什么" --topic "主题"
  python scripts/main.py "file.md" -o ~/Desktop/output --topic "主题"
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument('md_files', nargs='+', help='Markdown files to process')

    # Optional arguments
    parser.add_argument('--topic', '-t', default='default', help='Topic name for organization (folder name)')
    parser.add_argument('--titles', nargs='+', help='Custom titles for the infographics (overrides filenames)')
    parser.add_argument('--no-interactive', action='store_true', help='Disable interactive mode (skip confirmations)')
    parser.add_argument('--dry-run', action='store_true', help='Generate prompts only, skip image generation')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--output', '-o', help='Override output directory')

    # Config overrides (optional, though config.yaml/.env is preferred)
    parser.add_argument('--provider', choices=['google', 'nanobanana'], help='Override API provider')

    args = parser.parse_args()

    # Determine interactive mode (default is True, disabled by flag)
    interactive = not args.no_interactive

    # Setup Logging
    if args.debug:
        logger.setLevel('DEBUG')
        logger.debug("Debug logging enabled")

    try:
        # 1. Load Configuration
        config = Config.load()

        # Override config with CLI args if provided
        if args.provider:
            config.api.provider = args.provider
        if args.output:
            config.output.base_dir = args.output

        # 2. Initialize Session
        session = Session(args.topic, config)

        # 3. Initialize Workflow
        workflow = Workflow(config, session)

        # 4. Run Workflow
        md_paths = [Path(f).resolve() for f in args.md_files]
        workflow.run(md_paths, args.titles, interactive, args.dry_run)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
