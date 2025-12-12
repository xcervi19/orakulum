"""
Processors Module

Data processing components for the Orakulum pipeline.
Each processor handles a specific transformation step.
"""

from .block_parser import parse_plan_blocks, fill_expand_template
from .html_wrapper import wrap_with_html_template
from .html_to_json import transform_html_to_json, transform_html_directory
from .json_cleaner import clean_markdown_artifacts, clean_json_directory
from .uploader import upload_client_pages, upload_from_directory

__all__ = [
    # Block parsing
    "parse_plan_blocks",
    "fill_expand_template",
    # HTML wrapping
    "wrap_with_html_template",
    # HTML to JSON
    "transform_html_to_json",
    "transform_html_directory",
    # JSON cleaning
    "clean_markdown_artifacts",
    "clean_json_directory",
    # Uploading
    "upload_client_pages",
    "upload_from_directory",
]
