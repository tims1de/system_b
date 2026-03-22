from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """General application settings"""
    APP_TITLE: str
    APP_DESCRIPTION: str
    APP_VERSION: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class DatabaseSettings(BaseSettings):
    """Database settings with property-based URLs"""
    MODE: Literal["DEV", "TEST"] = "DEV"

    DB_DIALECT: str
    DB_DRIVER: str
    DB_NAME: str

    TEST_DB_DIALECT: str
    TEST_DB_DRIVER: str
    TEST_DB_NAME: str

    @property
    def database_url(self) -> str:
        """Main database URL"""
        return f"{self.DB_DIALECT}+{self.DB_DRIVER}:///{self.DB_NAME}"

    @property
    def test_database_url(self) -> str:
        """Test database URL"""
        return f"{self.TEST_DB_DIALECT}+{self.TEST_DB_DRIVER}:///{self.TEST_DB_NAME}"

    @property
    def url(self) -> str:
        """Actual database URL based on MODE"""
        if self.MODE == "TEST":
            return self.test_database_url
        return self.database_url

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


class Settings(AppSettings, DatabaseSettings):
    """Combined settings class"""
    SYSTEM_NAME: str
    SIGNER_CERT_NAME: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()