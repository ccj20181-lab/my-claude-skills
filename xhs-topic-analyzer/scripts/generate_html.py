#!/usr/bin/env python3
"""
HTML页面生成器 - 用于GitHub Pages部署
读取JSON数据并更新docs/data/目录下的数据文件
"""
import json
import shutil
from pathlib import Path
from datetime import datetime


def generate_site_data(json_path, output_dir):
    """
    生成网站数据文件

    Args:
        json_path: JSON数据文件路径
        output_dir: 输出目录(docs/data/)
    """
    print(f"[INFO] 开始生成网站数据...")

    # 读取JSON数据
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"[ERROR] JSON文件不存在: {json_path}")
        return False

    with open(json_file, 'r', encoding='utf-8') as f:
        notes = json.load(f)

    print(f"[INFO] 读取到 {len(notes)} 条笔记数据")

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 复制JSON数据到docs/data/
    target_file = output_path / "viral-notes.json"

    # 如果源文件和目标文件不是同一个文件,才进行复制
    if json_file.resolve() != target_file.resolve():
        shutil.copy2(json_file, target_file)
        print(f"[INFO] ✓ 数据文件已复制: {target_file}")
    else:
        print(f"[INFO] ✓ 数据文件已在目标位置: {target_file}")

    # 生成元数据
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_notes": len(notes),
        "avg_likes": sum(n['likes'] for n in notes) // len(notes) if notes else 0,
        "avg_followers": sum(n['followers'] for n in notes) // len(notes) if notes else 0,
        "top_viral_score": notes[0]['viral_score'] if notes else 0,
        "version": "1.0.0"
    }

    metadata_file = output_path / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"[INFO] ✓ 元数据文件已生成: {metadata_file}")

    return True


def main():
    """
    主函数 - 用于测试
    """
    import argparse

    parser = argparse.ArgumentParser(description='生成GitHub Pages数据文件')
    parser.add_argument('--input', required=True, help='输入JSON文件路径')
    parser.add_argument('--output', default='docs/data', help='输出目录(默认: docs/data)')
    args = parser.parse_args()

    success = generate_site_data(args.input, args.output)

    if success:
        print("\n[SUCCESS] 网站数据生成完成!")
        print(f"[INFO] 可以部署到GitHub Pages了")
        return 0
    else:
        print("\n[ERROR] 生成失败!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
