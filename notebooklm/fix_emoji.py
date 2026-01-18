#!/usr/bin/env python3
"""
批量修复 Windows GBK 编码下的 emoji 显示问题
将所有 emoji 符号替换为文本标签
"""

import re
from pathlib import Path

# Emoji 映射表
EMOJI_MAP = {
    '✅': '[OK]',
    '❌': '[Error]',
    '⚠️': '[Warning]',
    '🔧': '[Setup]',
    '📦': '[Package]',
    '🌐': '[Web]',
    '🚀': '[Run]',
    '🔑': '[Key]',
    '🔒': '[Lock]',
    '🔓': '[Unlock]',
    '🔐': '[Auth]',
    '💾': '[Save]',
    '🗑️': '[Delete]',
    '📝': '[Note]',
    '📚': '[Books]',
    '📓': '[Notebook]',  # 新增
    '🔍': '[Search]',
    '⏳': '[Wait]',
    '⏱️': '[Timer]',
    '🎯': '[Target]',
    '✨': '[Sparkle]',
    '💡': '[Idea]',
    '📊': '[Chart]',
    '📁': '[Folder]',
    '✓': '[OK]',
    '💬': '[Message]',
    '📤': '[Submit]',
    '🔄': '[Reload]',
}

def fix_emoji_in_file(file_path: Path):
    """修复单个文件中的 emoji"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 替换所有已知的 emoji
        for emoji, replacement in EMOJI_MAP.items():
            content = content.replace(emoji, replacement)

        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed: {file_path.name}")
            return True
        else:
            print(f"[Skip] No emoji found: {file_path.name}")
            return False

    except Exception as e:
        print(f"[Error] Failed to fix {file_path}: {e}")
        return False

def main():
    """主函数"""
    script_dir = Path(__file__).parent / "scripts"

    if not script_dir.exists():
        print("[Error] Scripts directory not found")
        return

    print("[Fix] Starting emoji fix for all Python files...")
    print()

    fixed_count = 0
    for py_file in script_dir.glob("*.py"):
        if fix_emoji_in_file(py_file):
            fixed_count += 1

    print()
    print(f"[Done] Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
