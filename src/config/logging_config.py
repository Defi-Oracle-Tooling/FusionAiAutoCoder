"""Configure logging for the application."""
from typing import Dict, Any, Optional
import logging
import logging.config
from pathlib import Path
import json

def configure_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    config_file: Optional[Path] = None
) -> logging.Logger:
    """Configure application logging."""
    if config_file and config_file.exists():
        with open(config_file) as f:
            config: Dict[str, Any] = json.load(f)
            logging.config.dictConfig(config)
    else:
        # Default configuration
        log_config: Dict[str, Any] = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": log_level or "INFO"
                }
            },
            "loggers": {
                "fusion_ai": {
                    "handlers": ["console"],
                    "level": log_level or "INFO",
                    "propagate": True
                }
            }
        }
        
        # Add file handler if specified
        if log_file:
            log_config["handlers"]["file"] = {
                "class": "logging.FileHandler",
                "filename": str(log_file),
                "formatter": "standard",
                "level": log_level or "INFO"
            }
            log_config["loggers"]["fusion_ai"]["handlers"].append("file")
        
        logging.config.dictConfig(log_config)
    
    return logging.getLogger("fusion_ai")