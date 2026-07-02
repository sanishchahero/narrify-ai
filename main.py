from app.core.config import get_settings
from app.core.logger import logger


def main():
    settings = get_settings()

    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Using model: {settings.llm_model}")


if __name__ == "__main__":
    main()