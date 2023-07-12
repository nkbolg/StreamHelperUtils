from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    deta_space_app_hostname: str
    deta_project_key: SecretStr

    # Вложенный класс с дополнительными указаниями для настроек
    class Config:
        # Имя файла, откуда будут прочитаны данные
        # (относительно текущей рабочей директории)
        env_file = '.env'
        # Кодировка читаемого файла
        env_file_encoding = 'utf-8'


def get_config():
    """Получение конфигурации из переменных среды или .env файла"""

    # При импорте файла сразу создастся
    # и провалидируется объект конфига,
    # который можно далее импортировать из разных мест
    return Settings()
