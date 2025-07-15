from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    db_user: str = "root"
    db_password: str = "123456"
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "yecai_ocr"
    result_dir: str = "results"
    database_url: Optional[str] = None  # 可选，优先用

    class Config:
        env_file = "config/.env"

    @property
    def sqlalchemy_database_url(self):
        if self.database_url:
            return self.database_url
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}" 
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings() 