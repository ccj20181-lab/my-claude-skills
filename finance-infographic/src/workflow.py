import time
import sys
import platform
import subprocess
import os
from pathlib import Path
from typing import List, Optional

from .config import Config
from .session import Session
from .api import get_client, APIClient
from .prompts import PromptBuilder
from .utils import logger, get_project_root

class Workflow:
    def __init__(self, config: Config, session: Session):
        self.config = config
        self.session = session
        self.api_client = get_client(config.api)
        self.prompt_builder = PromptBuilder()

        # Load reference images
        ref_dir = get_project_root() / 'references'
        self.reference_images = self.session.get_reference_images(ref_dir)
        if not self.reference_images:
            logger.warning("No reference images found in references/ directory!")

    def _extract_title_from_md(self, content: str) -> str:
        """
        从 markdown 内容的第一行提取主标题。
        第一行格式应该是: # 标题
        返回去掉 # 前缀后的标题。
        """
        first_line = content.strip().split('\n')[0]
        if first_line.startswith('# '):
            return first_line[2:].strip()  # 去掉 '# ' 前缀
        elif first_line.startswith('#'):
            return first_line[1:].strip()  # 去掉 '#' 前缀
        return ""  # 如果没有找到标题格式，返回空字符串

    def _open_file(self, file_path: Path):
        """Open a file with the default system application."""
        try:
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', str(file_path)))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(str(file_path))
            else:                                   # linux variants
                subprocess.call(('xdg-open', str(file_path)))
        except Exception as e:
            logger.warning(f"Could not open file {file_path}: {e}")

    def run(self, md_files: List[Path], titles: Optional[List[str]] = None, interactive: bool = True, dry_run: bool = False):
        """
        Execute the workflow for the given markdown files.
        """
        if not md_files:
            logger.warning("No markdown files provided.")
            return

        # Normalize titles
        if not titles:
            titles = [f.stem for f in md_files]
        elif len(titles) < len(md_files):
            # Pad titles if not enough provided
            titles.extend([f.stem for f in md_files[len(titles):]])

        logger.info(f"Starting workflow for {len(md_files)} files. Topic: {self.session.topic}")
        if dry_run:
            logger.info("DRY RUN MODE: Image generation will be skipped.")

        # Interactive Batch Confirmation
        if interactive:
            self._interactive_confirmation(md_files, titles)

        # Execution Loop
        for i, md_file in enumerate(md_files):
            file_title = titles[i]  # 文件名标题，仅用于日志显示
            logger.info(f"[{i+1}/{len(md_files)}] Processing: {file_title}")

            try:
                # 1. Read content
                content = md_file.read_text(encoding='utf-8')

                # 2. Extract title from md first line (CRITICAL: 使用 md 文件第一行作为主标题)
                display_title = self._extract_title_from_md(content)
                if not display_title:
                    # 如果 md 文件没有 # 标题，回退到使用文件名
                    logger.warning(f"No # title found in {md_file.name}, using filename as title")
                    display_title = file_title

                logger.info(f"Using display title: '{display_title}'")
                self.session.save_source(content, display_title)

                # 3. Build Prompt (使用从 md 提取的标题)
                prompt = self.prompt_builder.build_prompt(content, display_title)
                prompt_path = self.session.save_prompt(prompt, i, display_title)

                # 3. Mandatory Prompt Review
                if interactive:
                    print(f"\n--- Prompt Review: {display_title} ---")
                    print(f"Opening prompt file for review: {prompt_path}")
                    self._open_file(prompt_path)

                    if not self._get_user_confirmation(f"Prompt ready. Generate image for '{display_title}'?"):
                        logger.info(f"Skipping {display_title}")
                        continue

                # Dry Run Check
                if dry_run:
                    logger.info(f"Dry run: Skipping generation for '{display_title}'")
                    continue

                # 4. Generate Image
                logger.info(f"Generating image for '{display_title}'...")
                image_data = self.api_client.generate_image(prompt, self.reference_images, resolution=self.config.output.resolution)

                # 5. Save Image
                if image_data:
                    path = self.session.save_image(image_data, i, display_title)
                    print(f"  ✅ Saved: {path.name}")
                else:
                    logger.error(f"Failed to generate image for '{display_title}'")
                    print(f"  ❌ Failed: {display_title}")

            except Exception as e:
                logger.error(f"Failed to process {display_title}: {e}")

            # Rate limiting / polite delay
            time.sleep(1)

        logger.info("Workflow completed.")

    def _analyze_content(self, content: str) -> str:
        """Use LLM to analyze the content structure."""
        prompt = (
            "Analyze the following text for an infographic:\n"
            "1. Suggest a short Main Title (2-5 chars)\n"
            "2. Summarize key points (3 bullets)\n"
            "3. Suggest visual layout (e.g. List, Comparison, Process)\n\n"
            f"Text content:\n{content[:3000]}"
        )
        return self.api_client.generate_text(prompt) or "Analysis failed."

    def _interactive_confirmation(self, md_files: List[Path], titles: List[str]):
        """
        Show the plan and ask for user confirmation.
        """
        print("\n=== Workflow Plan ===")
        print(f"Topic: {self.session.topic}")
        print(f"Output Directory: {self.session.session_dir}")
        print("\nFiles to process:")
        for i, (f, t) in enumerate(zip(md_files, titles)):
            print(f"  {i+1}. {f.name} -> Title: {t}")
        print("=====================\n")

        if not self._get_user_confirmation("Proceed with this plan?"):
            logger.info("Workflow aborted by user.")
            sys.exit(0)

    def _get_user_confirmation(self, question: str) -> bool:
        """Get yes/no confirmation from user."""
        while True:
            try:
                response = input(f"{question} [y/n]: ").lower().strip()
                if response in ['y', 'yes']:
                    return True
                if response in ['n', 'no']:
                    return False
            except EOFError:
                # Handle non-interactive environments
                logger.warning("Non-interactive environment detected, assuming Yes.")
                return True
            except KeyboardInterrupt:
                logger.info("\nInterrupted by user.")
                sys.exit(1)
