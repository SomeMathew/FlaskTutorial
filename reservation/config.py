class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = r"sqlite:///reservation_tutorial.sqlite"


class DevConfig(Config):
    DEBUG = True


class DefaultConfig(DevConfig):
    pass
