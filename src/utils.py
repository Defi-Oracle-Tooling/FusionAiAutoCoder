"""
Utility functions for FusionAiAutoCoder.
"""
import os
import logging
import json
import sys
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

def setup_logging() -> logging.Logger:
    """Configure and return a logger for the application.
    
    Returns:
        A configured logger instance.
    """
    # Get log level from environment or default to INFO
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"fusion_ai_{timestamp}.log")
    
    # Configure logging format and handlers
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("fusion_ai")
    logger.info(f"Logging initialized at level {log_level_str}")
    
    return logger

def read_config_file(file_path: str) -> Dict[str, Any]:
    """Read configuration from a JSON file.
    
    Args:
        file_path: Path to the configuration file.
        
    Returns:
        Dictionary containing configuration values.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Configuration file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Error parsing configuration file: {file_path}")
        return {}

def save_result(result: Dict[str, Any], output_dir: str, filename: Optional[str] = None) -> str:
    """Save operation result to a file.
    
    Args:
        result: Result data to save.
        output_dir: Directory to save the file.
        filename: Optional filename, defaults to timestamp-based name.
        
    Returns:
        Path to the saved file.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.json"
    
    # Ensure filename has .json extension
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Full path to output file
    output_path = os.path.join(output_dir, filename)
    
    # Write result to file
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    logging.info(f"Result saved to {output_path}")
    return output_path

def parse_code_blocks(text: str) -> List[Dict[str, str]]:
    """Parse code blocks from markdown-formatted text.
    
    Args:
        text: Text containing markdown code blocks.
        
    Returns:
        List of dictionaries with 'code' and 'language' keys.
    """
    import re
    
    # Regex pattern for code blocks: ```language\n...\n```
    pattern = r'```(\w*)\n([\s\S]*?)\n```'
    
    # Find all code blocks
    matches = re.findall(pattern, text)
    
    code_blocks = []
    for language, code in matches:
        code_blocks.append({
            'language': language.lower() if language else 'text',
            'code': code.strip()
        })
    
    return code_blocks

def detect_language(code: str) -> str:
    """Attempt to detect the programming language of a code snippet.
    
    Args:
        code: Code snippet to analyze.
        
    Returns:
        Detected language name or 'unknown'.
    """
    # Simple heuristics for language detection
    if code.strip().startswith('<?php'):
        return 'php'
    elif 'function' in code and '{' in code and '}' in code and ';' in code:
        if 'import React' in code or 'import {' in code:
            return 'typescript'
        elif 'console.log' in code:
            return 'javascript'
    elif 'def ' in code and ':' in code and ('import ' in code or 'class ' in code):
        return 'python'
    elif 'public class' in code or 'private class' in code:
        return 'java'
    elif '#include' in code and ('{' in code and '}' in code):
        return 'c' if not ('cout' in code or 'cin' in code or '::' in code) else 'cpp'
    elif '[' in code and ']' in code and '->' in code:
        return 'php'
    
    # Default to unknown
    return 'unknown'

def is_gpu_available() -> bool:
    """Check if GPU acceleration is available.
    
    Returns:
        True if GPU is available, False otherwise.
    """
    try:
        # Try to import CUDA-related libraries
        import torch
        return torch.cuda.is_available()
    except ImportError:
        try:
            # Try tensorflow as well
            import tensorflow as tf
            return len(tf.config.list_physical_devices('GPU')) > 0
        except ImportError:
            return False
    return False

def get_version_info() -> Dict[str, str]:
    """Get version information for the system and dependencies.
    
    Returns:
        Dictionary with version information.
    """
    import platform
    import pkg_resources
    
    version_info = {
        'system': platform.system(),
        'python': platform.python_version(),
        'fusion_ai': '1.0.0',  # Hardcoded for now, should be pulled from package
    }
    
    # Add versions of key dependencies
    dependencies = ['autogen', 'fastapi', 'pydantic', 'azure-identity']
    for dep in dependencies:
        try:
            version = pkg_resources.get_distribution(dep).version
            version_info[dep] = version
        except pkg_resources.DistributionNotFound:
            version_info[dep] = 'not installed'
    
    return version_info

def is_valid_code(code: str, language: str) -> bool:
    """Simple validation of syntax for code snippets.
    
    Args:
        code: Code to validate.
        language: Programming language.
        
    Returns:
        True if syntax appears valid, False otherwise.
    """
    if language == 'python':
        try:
            import ast
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    # For other languages, just perform basic checks
    # This is a simplified approach - a real implementation would use language-specific tools
    if language in ['javascript', 'typescript']:
        # Check for basic syntax balance
        return code.count('{') == code.count('}') and code.count('(') == code.count(')')
    
    # Default to True for languages we don't check
    return True