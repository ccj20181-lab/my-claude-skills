from pathlib import Path
from typing import Optional
from .utils import get_project_root, logger

class PromptBuilder:
    def __init__(self, template_path: Optional[Path] = None):
        if template_path is None:
            # Default to references/templates/base_prompt.md
            template_path = get_project_root() / 'references' / 'templates' / 'base_prompt.md'

        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> str:
        try:
            return self.template_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to load prompt template from {self.template_path}: {e}")
            return ""

    def build_prompt(self, content: str, title: Optional[str] = None) -> str:
        """
        Build the final prompt by substituting values into the template.
        """
        title_instruction = ""
        if title:
            title_instruction = f"【主标题】: \"{title}\"\n(CRITICAL: 必须严格使用这个标题，一个字都不能改，也不要缩短。)"
        else:
            title_instruction = "【主标题】: (请根据【文案】内容提炼一个简短的主标题，样式与参考图完全一致)"

        try:
            prompt = self.template.format(
                title_instruction=title_instruction,
                content=content
            )
            return prompt
        except KeyError as e:
            logger.error(f"Missing key in template: {e}")
            # Fallback to simple concatenation if formatting fails
            return f"{self.template}\n\n【文案】\n{content}"
