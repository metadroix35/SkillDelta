from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):

    # -----------------------------------
    # 🔹 Core
    # -----------------------------------
    APP_NAME: str = "SkillRot"
    DATABASE_URL: str

    # -----------------------------------
    # 🔹 LLM / APIs
    # -----------------------------------
    GROQ_API_KEY: str | None = None
    LLM_ENABLED: bool = False
    YOUTUBE_API_KEY: str | None = None

    # -----------------------------------
    # 🔹 Email
    # -----------------------------------
    EMAIL_ADDRESS: str | None = None
    EMAIL_PASSWORD: str | None = None

    # -----------------------------------
    # 🔐 JWT
    # -----------------------------------
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    # 🔁 Scheduler / Cron
    CRON_SECRET: str | None = None

    # -----------------------------------
    # ⚙ Config
    # -----------------------------------
    class Config:
        env_file = str(Path(__file__).resolve().parent.parent.parent / ".env")
        env_file_encoding = "utf-8"


# 🔥 Create global settings object
settings = Settings()

print("ENV FILE LOADED")
print("DATABASE URL USED:", settings.DATABASE_URL)

if not settings.EMAIL_ADDRESS or not settings.EMAIL_PASSWORD:
    print("⚠ WARNING: Email credentials not set. Email reminders will fail.")
