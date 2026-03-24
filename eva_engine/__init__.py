# This file makes the 'eva_engine' directory a Python package.

# Expose key components at the top level of the package
from .graph_handler import GraphHandler
from .utils import (
    log_message, 
    read_file_content, 
    write_file_content, 
    search_web, 
    analyze_text, 
    send_telegram_message, 
    github_search_repos, 
    github_get_file_contents
)
from .semantic_validator import validate_code
