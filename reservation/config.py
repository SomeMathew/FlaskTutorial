class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = r"sqlite:///reservation_tutorial.sqlite"


class DevConfig(Config):
    DEBUG = True


class DefaultConfig(DevConfig):
    pass


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///../tests/test_reservation_tutorial.sqlite"
