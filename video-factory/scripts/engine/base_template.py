from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseTemplate(ABC):
    """
    Abstract base class for Video Factory templates.
    Each template must implement the logic to structure content and provide React components.
    """

    @abstractmethod
    def get_structure(self, topic: str) -> List[Dict[str, Any]]:
        """
        Parses a topic into a structured script (scenes).

        Args:
            topic: The input topic or text.

        Returns:
            A list of scene dictionaries (e.g., [{'type': 'title', 'text': '...'}, ...])
        """
        pass

    @abstractmethod
    def generate_prompts(self, script: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Converts script segments into image generation prompts.

        Args:
            script: The structured script from get_structure.

        Returns:
            The script with added 'image_prompt' fields.
        """
        pass

    @abstractmethod
    def get_react_files(self) -> Dict[str, str]:
        """
        Returns a map of filenames to their content for scaffolding.

        Returns:
            Dict where keys are relative file paths (e.g., 'Composition.tsx')
            and values are the file content strings.
        """
        pass

    @abstractmethod
    def get_meta(self) -> Dict[str, Any]:
        """
        Returns metadata about the template.

        Returns:
            Dict containing 'name', 'description', 'width', 'height', 'fps', etc.
        """
        pass
