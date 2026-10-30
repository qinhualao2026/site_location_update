import logging.config
from config import LOG_FILE

 
# Centralized logging configuration using dictConfig
def setup_logging():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    logging.config.dictConfig({
        'version': 1,  # Configuration schema version
        'disable_existing_loggers': False,  # Ensure existing loggers are not disabled
        'formatters': {    # setup two different format
            'simple': {
                "format": "%(asctime)s | %(levelname)s | %(message)s"
            },
            'detailed': {
                "format": "%(asctime)s | %(name)s | %(filename)s: %(lineno)d | %(levelname)s | %(message)s"
            }
        },
        "handlers": {    # two handlers here: console and file
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "INFO"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_FILE,
                "formatter": "detailed",
                "level": "WARNING",
                "encoding": "utf-8",
                "maxBytes": 5 * 1024 * 1024,
                "backupCount": 5,
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console","file"]
            },
        "loggers": {    # setup logger w/ two handlers
            "logging_tester": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False
            }
        }
    })
    
