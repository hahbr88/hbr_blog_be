from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ✅ 컨테이너/프로덕션: OS 환경변수만 읽는다 (env_file 제거)
    model_config = SettingsConfigDict(env_ignore_empty=True)

    APP_NAME: str = "HBR Blog API"
    DATABASE_URL: str = "sqlite:///./dev.db"

settings = Settings()
