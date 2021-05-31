import abc
from dataclasses import dataclass

import envparse


@dataclass
class Config(abc.ABC):
    """
    Abstract Config data class, do not instantiate this class.
    """

    DATABASE_URL: str
    DATABASE_SCHEMA: str

    FLASK_KEY: str


@dataclass
class TestConfig(Config):
    """
    Config data class for testing.
    """

    def __init__(self):
        super().__init__(envparse.env.str("TEST_DATABASE_URL"),
                         envparse.env.str("TEST_DATABASE_SCHEMA"),
                         envparse.env.str("TEST_FLASK_KEY"))


class ProductionConfig(Config):
    def __init__(self):
        super().__init__(envparse.env.str("DATABASE_URL"),
                         envparse.env.str("DATABASE_SCHEMA"),
                         envparse.env.str("HEROKU_FLASK_KEY"))


def get_config_from_env() -> Config:
    if envparse.env.bool("FLASK_DEBUG", default=True):
        return TestConfig()
    else:
        return ProductionConfig()
