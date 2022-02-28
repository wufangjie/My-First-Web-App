import secrets
from pydantic import BaseSettings, validator
from typing import Optional, List


config_mysql = {
    "dialect": "mysql",
    "driver": "mysqlconnector",
    "user": "debian-sys-maint",
    "password": "lF66Yxv1DKOh5doW",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "my_blog"
}


def make_orm_uri(config):
    for key in ["driver", "user", "password", "port"]:
        config.setdefault(key, "")
    sep = ["+" if config["driver"] else "",
           ":" if config["password"] else "",
           ":" if config["port"] else ""]
    return "{dialect}{sep[0]}{driver}://{user}{sep[1]}{password}@{host}{sep[2]}{port}/{database}".format(sep=sep, **config)


class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "testing" #secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @validator("SQLALCHEMY_DATABASE_URI")
    def valid_db_uri(cls, value: Optional[str]) -> str:
        if value is None:
            value = make_orm_uri(config_mysql)
        return value

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:8888",
    ]

    PICTURE_ROOT: str = "pictures/"

    class Config:
        case_sensitive = True


settings = Settings()
