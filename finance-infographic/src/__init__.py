"""
Finance Infographic Generator

A tool for generating finance-themed infographics using Gemini 3 Pro Image Preview.
"""

__version__ = "2.1.0"
__author__ = "finance-team"

from .config import Config, APIConfig, OutputConfig
from .session import Session
from .workflow import Workflow
from .api import get_client, APIClient, GoogleClient, NanoBananaClient
from .prompts import PromptBuilder
from .utils import logger, get_project_root, ensure_dir

__all__ = [
    "__version__",
    "__author__",
    "Config",
    "APIConfig",
    "OutputConfig",
    "Session",
    "Workflow",
    "get_client",
    "APIClient",
    "GoogleClient",
    "NanoBananaClient",
    "PromptBuilder",
    "logger",
    "get_project_root",
    "ensure_dir",
]
