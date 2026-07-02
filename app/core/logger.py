import sys

from loguru import logger


logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time}</green> | <level>{level}</level> | {message}",
)