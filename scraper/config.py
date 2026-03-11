"""
爬虫配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import random


class ScraperSettings(BaseSettings):
    # 爬虫配置
    headless: bool = True
    timeout_ms: int = 30000
    page_load_timeout_ms: int = 60000
    
    # 反反爬配置
    min_delay_ms: int = 2000
    max_delay_ms: int = 5000
    max_retries: int = 3
    
    # User-Agent 池
    user_agents: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]
    
    # 代理配置（可选）
    proxy_server: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_random_user_agent() -> str:
    """随机选择一个 User-Agent"""
    settings = ScraperSettings()
    return random.choice(settings.user_agents)


def get_random_delay() -> int:
    """获取随机延迟（毫秒）"""
    settings = ScraperSettings()
    return random.randint(settings.min_delay_ms, settings.max_delay_ms)


settings = ScraperSettings()
