#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Video Factory - Main CLI Entry Point
"""
import argparse
import sys
import os
from pathlib import Path

# Add current directory to path so imports work
# main.py is in scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.scaffolding import Scaffolder
from engine.template_manager import TemplateManager
from engine.asset_gen import AssetGenerator

# Configuration
SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"

def cmd_create(args):
    """
    Handle the 'create' command: New Project
    """
    output_path = Path(args.output).resolve()

    print(f"🎬 Video Factory: Creating new project at '{output_path}'")
    print(f"   Topic: {args.topic}")
    print(f"   Template: {args.template}")

    # 1. Load Template Logic
    print("🔹 Loading template...")
    manager = TemplateManager(TEMPLATES_DIR)
    try:
        template = manager.load_template(args.template)
    except Exception as e:
        print(f"❌ Failed to load template '{args.template}': {e}")
        return 1

    meta = template.get_meta()

    # 2. Scaffolding (Create Remotion Project)
    print("🔹 Scaffolding project...")
    scaffolder = Scaffolder(output_path)

    # Create base structure
    scaffolder.create_project(output_path.name)

    # Install template-specific React files
    react_files = template.get_react_files()
    scaffolder.install_template_files(react_files)

    # Setup config
    scaffolder.setup_config(
        width=meta.get("width", 1080),
        height=meta.get("height", 1440),
        fps=meta.get("fps", 30)
    )

    # 3. Content Generation (Topic -> Script)
    print("🔹 Generating script structure...")
    script = template.get_structure(args.topic)

    # 4. Prompt Generation (Script -> Prompts)
    print("🔹 Generating visual prompts...")
    script_with_prompts = template.generate_prompts(script)

    # 5. Asset Generation (Prompts -> Images)
    if not args.skip_assets:
        print("🔹 Generating assets...")
        asset_gen = AssetGenerator(output_path)
        final_scenes = asset_gen.generate_assets(script_with_prompts)

        # Save Data
        asset_gen.save_manifest(final_scenes, meta)
    else:
        print("⏩ Skipping asset generation (--skip-assets)")
        # Save Data without generated images
        asset_gen = AssetGenerator(output_path)
        asset_gen.save_manifest(script_with_prompts, meta)

    print("\n" + "="*50)
    print(f"✅ Project created successfully at: {output_path}")
    print("👉 Next steps:")
    print(f"   cd {output_path}")
    print("   npm install")
    print("   npm start  # To launch Remotion Studio")
    print("="*50)

def cmd_gen_assets(args):
    """
    Handle 'gen-assets' command: Regenerate assets for existing project
    """
    print("Feature coming soon: Re-generating assets for existing project.")

def main():
    parser = argparse.ArgumentParser(description="Video Factory Skill CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: create
    create_parser = subparsers.add_parser("create", help="Create a new video project")
    create_parser.add_argument("--topic", required=True, help="The topic of the video")
    create_parser.add_argument("--template", default="knowledge-explainer", help="The visual template to use")
    create_parser.add_argument("--output", required=True, help="Output directory path")
    create_parser.add_argument("--skip-assets", action="store_true", help="Skip AI image generation")

    # Command: gen-assets
    gen_parser = subparsers.add_parser("gen-assets", help="Generate assets for an existing project")
    gen_parser.add_argument("--project", required=True, help="Path to the project")

    args = parser.parse_args()

    if args.command == "create":
        return cmd_create(args)
    elif args.command == "gen-assets":
        return cmd_gen_assets(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    exit(main())
