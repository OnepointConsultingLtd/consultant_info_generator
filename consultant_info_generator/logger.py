import logging
import logging.config

default_config = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "WARNING",
            "stream": "ext://sys.stderr",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
logging.config.dictConfig(default_config)

logger = logging.getLogger("pdf_to_markdown")
