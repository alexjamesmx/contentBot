"""Content generation module."""
from src.generation.story_generator import StoryGenerator
from src.generation.story_templates import get_template, list_genres

__all__ = ["StoryGenerator", "get_template", "list_genres"]
