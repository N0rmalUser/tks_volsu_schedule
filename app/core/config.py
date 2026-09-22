from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Config(BaseSettings):
    """Конфигурация приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ===== TELEGRAM =====
    tg_bot_token: str
    admin_chat_id: int = Field(
        description=(
            "ID административного чата.\n"
            "Для каждого пользователя, нажавшего «Начать», "
            "бот создаёт отдельный топик.\n"
            "Сообщения из топика пересылаются пользователю.\n"
            "Сообщения из топика #General рассылаются всем пользователям."
        ),
    )

    # ===== VK =====
    vk_bot_token: str

    # ===== LOGGING =====
    timezone: str
    numerator: int
    college_cron: str

    # ===== UNIVERSITY =====
    teachers: list[str]
    groups: list[str]
    rooms: list[str]
    parent_rooms: dict[str, list[str]]

    students: dict[str, str]
    aliases: dict[str, str]
    substitute: dict[str, list[str]]

    # Вычисляется автоматически
    all_personal: list[str] = []

    # ===== COLLEGE =====
    api_url: str
    api_key: str

    college_teachers: list[str]
    college_groups: list[str]

    substitute_college: dict[str, list[dict[str, str]]]

    # ===== POSTGRESQL =====
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: SecretStr
    postgres_db: str = "postgres"

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def alembic_database_url(self) -> str:
        return self.database_url.render_as_string(hide_password=False)

    @model_validator(mode="after")
    def build_all_personal(self) -> Config:
        """Объединённый список преподавателей и сотрудников-студентов."""
        self.all_personal = sorted(set(self.teachers) | set(self.students))
        return self


config = Config()
