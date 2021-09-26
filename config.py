import abc
from dataclasses import dataclass

import envparse


@dataclass
class Config(abc.ABC):
    """
    Abstract Config data class, do not instantiate this class.
    """

    SQLALCHEMY_DATABASE_URI: str
    SECRET_KEY: str
    REGISTER_OPEN: bool

    VERSION_STRING: str = "0.0.5"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False


@dataclass
class TestConfig(Config):
    """
    Config data class for testing.
    """
    def __init__(self):
        super().__init__(envparse.env.str("TEST_DATABASE_URL", default=None),
                         envparse.env.str("TEST_FLASK_KEY", default=None),
                         envparse.env.bool("TEST_REGISTER_OPEN", default=True))


@dataclass
class ProductionConfig(Config):
    """
    Config data class for production.
    """
    def __init__(self):
        super().__init__(envparse.env.str("DATABASE_URL", default=None),
                         envparse.env.str("HEROKU_FLASK_KEY", default=None),
                         envparse.env.bool("REGISTER_OPEN", default=False))


def get_config_from_env() -> Config:
    if envparse.env.bool("FLASK_DEBUG", default=True):
        return TestConfig()
    else:
        return ProductionConfig()
