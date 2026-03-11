"""
基础爬虫类
所有供应商爬虫的基类
"""
from playwright.sync_api import sync_playwright, Page, Browser
from playwright_stealth import stealth_sync
from typing import Optional, Dict, List, Any
import logging
import time
import random
from .config import settings, get_random_user_agent, get_random_delay

logger = logging.getLogger(__name__)


class BaseScraper:
    """基础爬虫类"""
    
    supplier_name: str = "Base"
    base_url: str = ""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    def start(self):
        """启动浏览器"""
        logger.info(f"启动 {self.supplier_name} 爬虫...")
        
        self.playwright = sync_playwright().start()
        
        # 配置浏览器启动参数
        launch_args = {
            "headless": settings.headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        }
        
        # 添加代理配置（如果有）
        if settings.proxy_server:
            launch_args["proxy"] = {
                "server": settings.proxy_server,
                "username": settings.proxy_username,
                "password": settings.proxy_password,
            }
        
        self.browser = self.playwright.chromium.launch(**launch_args)
        
        # 创建新页面
        self.page = self.browser.new_page(
            viewport={"width": 1920, "height": 1080},
            user_agent=get_random_user_agent()
        )
        
        # 应用 stealth 隐藏自动化特征
        stealth_sync(self.page)
        
        # 注入 JavaScript 隐藏 webdriver
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 覆盖 permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        logger.info(f"{self.supplier_name} 爬虫启动完成")
    
    def stop(self):
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info(f"{self.supplier_name} 爬虫已关闭")
    
    def random_delay(self, min_ms: int = None, max_ms: int = None):
        """随机延迟"""
        if min_ms is None:
            min_ms = settings.min_delay_ms
        if max_ms is None:
            max_ms = settings.max_delay_ms
        
        delay = random.randint(min_ms, max_ms)
        logger.debug(f"延迟 {delay}ms")
        time.sleep(delay / 1000)
    
    def search_compound(self, query: str) -> Optional[Dict[str, Any]]:
        """
        搜索化合物并返回价格信息
        
        Args:
            query: 化合物名称、SMILES 或 CAS 号
        
        Returns:
            价格信息字典，如果失败返回 None
        """
        raise NotImplementedError("子类必须实现 search_compound 方法")
    
    def parse_price_page(self) -> Optional[Dict[str, Any]]:
        """
        解析价格页面
        
        Returns:
            价格信息字典
        """
        raise NotImplementedError("子类必须实现 parse_price_page 方法")
    
    def take_screenshot(self, path: str = "screenshot.png"):
        """截图调试"""
        if self.page:
            self.page.screenshot(path=path, full_page=True)
            logger.info(f"截图已保存到 {path}")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
