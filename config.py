import os
from urllib.parse import quote_plus


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "0519")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "project_management")
    DB_CHARSET = os.environ.get("DB_CHARSET", "utf8mb4")

    DB_USER_ESCAPED = quote_plus(DB_USER)
    DB_PASSWORD_ESCAPED = quote_plus(DB_PASSWORD)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        (
            f"mysql+pymysql://{DB_USER_ESCAPED}:{DB_PASSWORD_ESCAPED}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
