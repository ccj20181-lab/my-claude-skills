import os
import sys
import importlib.util
import json
from pathlib import Path
from typing import Type
from .base_template import BaseTemplate

class TemplateManager:
    """
    Manages the loading and discovery of video templates.
    """

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def load_template(self, template_name: str) -> BaseTemplate:
        """
        Loads the 'logic.py' from the specified template directory and returns an instance of the class.
        The class in logic.py must be named 'Template' and inherit from BaseTemplate.
        """
        template_path = self.templates_dir / template_name
        logic_file = template_path / "logic.py"

        if not logic_file.exists():
            raise ValueError(f"Template '{template_name}' not found at {template_path}")

        # Dynamic import of the python file
        spec = importlib.util.spec_from_file_location(f"templates.{template_name}", logic_file)
        if spec is None or spec.loader is None:
             raise ImportError(f"Could not load spec for template {template_name}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[f"templates.{template_name}"] = module
        spec.loader.exec_module(module)

        # Look for a class that inherits from BaseTemplate
        # Convention: The class should be named 'TemplateLogic' or we search for the first subclass

        template_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                issubclass(attr, BaseTemplate) and
                attr is not BaseTemplate):
                template_class = attr
                break

        if template_class is None:
            raise ImportError(f"No class inheriting from BaseTemplate found in {logic_file}")

        return template_class()

    def get_template_manifest(self, template_name: str) -> dict:
        """Reads the manifest.json of a template."""
        manifest_path = self.templates_dir / template_name / "manifest.json"
        if not manifest_path.exists():
            return {}

        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
