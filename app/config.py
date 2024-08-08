import os
import pathlib
from functools import lru_cache

"""FastAPI Config"""

class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent

    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_URL", "redis://redis:6379/0")

    FIRECRAWL_API_KEY: str = os.environ.get("FIRECRAWL_API_KEY", "")

    PINECONE_INDEX_NAME: str = os.environ.get("PINECONE_INDEX_NAME", "")


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.environ.get("FAST_API_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()