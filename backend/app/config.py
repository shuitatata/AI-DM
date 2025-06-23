"""配置管理模块"""

import os
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"  # 忽略额外字段
    )

    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_model_name: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.7

    # 应用配置
    debug: bool = True
    log_level: str = "INFO"

    # 模板配置
    template_base_dir: str = "../templates"


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
