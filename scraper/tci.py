"""
TCI Chemicals 爬虫
https://www.tcichemicals.com/
"""
from typing import Optional, Dict, Any
import logging
import re
from .base import BaseScraper

logger = logging.getLogger(__name__)


class TCIScraper(BaseScraper):
    """TCI 爬虫"""
    
    supplier_name = "TCI Chemicals"
    base_url = "https://www.tcichemicals.com"
    
    def search_compound(self, query: str) -> Optional[Dict[str, Any]]:
        """
        搜索 TCI 化合物
        
        Args:
            query: 化合物名称、产品编号或 CAS 号
        
        Returns:
            价格信息字典
        """
        try:
            if not self.page:
                self.start()
            
            # TCI 支持多种搜索方式
            search_url = f"{self.base_url}/US/en/search?keyword={query}"
            logger.info(f"搜索 TCI: {query}")
            
            # 访问搜索页面
            self.page.goto(search_url, wait_until="networkidle", timeout=settings.timeout_ms)
            self.random_delay()
            
            # 检查是否有搜索结果
            product_links = self.page.query_selector_all(".product-item a")
            
            if not product_links:
                logger.warning(f"TCI 未找到化合物：{query}")
                return None
            
            # 获取第一个产品的链接
            first_product_url = product_links[0].get_attribute("href")
            
            if not first_product_url:
                return None
            
            # 访问产品页面
            if not first_product_url.startswith("http"):
                first_product_url = f"{self.base_url}{first_product_url}"
            
            logger.info(f"访问产品页面：{first_product_url}")
            self.page.goto(first_product_product_url, wait_until="networkidle", timeout=settings.timeout_ms)
            self.random_delay()
            
            # 解析价格信息
            return self.parse_price_page()
        
        except Exception as e:
            logger.error(f"TCI 搜索失败：{e}")
            self.take_screenshot(f"tci_error_{query.replace(' ', '_')}.png")
            return None
    
    def parse_price_page(self) -> Optional[Dict[str, Any]]:
        """解析 TCI 产品页面"""
        try:
            # 获取产品名称
            name = self.page.query_selector("h1.product-title")
            name_text = name.inner_text().strip() if name else ""
            
            # 获取产品编号
            product_no = self.page.query_selector(".product-number")
            product_no_text = product_no.inner_text().strip() if product_no else ""
            product_no_text = product_no_text.replace("Product Number:", "").strip()
            
            # 获取 CAS 号
            cas = self.page.query_selector(".cas-number")
            cas_text = cas.inner_text().strip() if cas else ""
            cas_text = cas_text.replace("CAS RN:", "").strip()
            
            # 获取价格信息
            prices = []
            
            # TCI 通常有多个规格
            size_options = self.page.query_selector_all(".size-option")
            
            for size_elem in size_options:
                try:
                    # 规格
                    size = size_elem.get_attribute("data-size") or size_elem.inner_text().strip()
                    
                    # 价格
                    price_elem = size_elem.query_selector(".price")
                    price_text = price_elem.inner_text().strip() if price_elem else ""
                    
                    # 提取价格数字
                    price_match = re.search(r'¥?([\d,]+\.?\d*)', price_text)
                    price_value = float(price_match.group(1).replace(',', '')) if price_match else 0
                    
                    # 库存状态
                    stock_elem = size_elem.query_selector(".stock")
                    stock = stock_elem.inner_text().strip() if stock_elem else "Available"
                    
                    prices.append({
                        "size": size,
                        "price": price_value,
                        "currency": "JPY",
                        "stock": stock,
                    })
                except Exception as e:
                    logger.debug(f"解析价格项失败：{e}")
                    continue
            
            # 如果没有找到具体价格
            if not prices:
                prices.append({
                    "size": "Multiple",
                    "price": 0,
                    "currency": "JPY",
                    "stock": "Inquire",
                })
            
            return {
                "supplier": self.supplier_name,
                "name": name_text,
                "product_number": product_no_text,
                "cas": cas_text,
                "url": self.page.url,
                "prices": prices,
                "currency": "JPY",
            }
        
        except Exception as e:
            logger.error(f"TCI 页面解析失败：{e}")
            return None
