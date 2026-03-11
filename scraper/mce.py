"""
MedChemExpress (MCE) 爬虫
https://www.medchemexpress.com/
"""
from typing import Optional, Dict, Any
import logging
import re
from .base import BaseScraper

logger = logging.getLogger(__name__)


class MCEScraper(BaseScraper):
    """MCE 爬虫"""
    
    supplier_name = "MedChemExpress"
    base_url = "https://www.medchemexpress.com"
    
    def search_compound(self, query: str) -> Optional[Dict[str, Any]]:
        """
        搜索 MCE 化合物
        
        Args:
            query: 化合物名称、SMILES 或 CAS 号
        
        Returns:
            价格信息字典
        """
        try:
            if not self.page:
                self.start()
            
            # 构建搜索 URL
            search_url = f"{self.base_url}/catalog.html?q={query}"
            logger.info(f"搜索 MCE: {query}")
            
            # 访问搜索页面
            self.page.goto(search_url, wait_until="networkidle", timeout=settings.timeout_ms)
            self.random_delay()
            
            # 检查是否有搜索结果
            product_links = self.page.query_selector_all(".product-list-item a")
            
            if not product_links:
                logger.warning(f"MCE 未找到化合物：{query}")
                return None
            
            # 获取第一个产品的链接
            first_product_url = product_links[0].get_attribute("href")
            
            if not first_product_url:
                return None
            
            # 访问产品页面
            if not first_product_url.startswith("http"):
                first_product_url = f"{self.base_url}{first_product_url}"
            
            logger.info(f"访问产品页面：{first_product_url}")
            self.page.goto(first_product_url, wait_until="networkidle", timeout=settings.timeout_ms)
            self.random_delay()
            
            # 解析价格信息
            return self.parse_price_page()
        
        except Exception as e:
            logger.error(f"MCE 搜索失败：{e}")
            self.take_screenshot(f"mce_error_{query.replace(' ', '_')}.png")
            return None
    
    def parse_price_page(self) -> Optional[Dict[str, Any]]:
        """解析 MCE 产品页面"""
        try:
            # 获取产品名称
            name = self.page.query_selector("h1.product-name")
            name_text = name.inner_text().strip() if name else ""
            
            # 获取 CAS 号
            cas = self.page.query_selector(".cas-number")
            cas_text = cas.inner_text().strip() if cas else ""
            cas_text = cas_text.replace("CAS No.:", "").strip()
            
            # 获取价格信息（MCE 通常显示多个规格）
            prices = []
            
            # 查找价格元素
            price_elements = self.page.query_selector_all(".product-price-item")
            
            for price_elem in price_elements:
                try:
                    # 规格
                    size_elem = price_elem.query_selector(".size")
                    size = size_elem.inner_text().strip() if size_elem else ""
                    
                    # 价格
                    price_elem_node = price_elem.query_selector(".price")
                    price_text = price_elem_node.inner_text().strip() if price_elem_node else ""
                    
                    # 提取价格数字
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price_value = float(price_match.group(1).replace(',', '')) if price_match else 0
                    
                    # 库存状态
                    stock_elem = price_elem.query_selector(".stock-status")
                    stock = stock_elem.inner_text().strip() if stock_elem else "In Stock"
                    
                    prices.append({
                        "size": size,
                        "price": price_value,
                        "currency": "USD",
                        "stock": stock,
                    })
                except Exception as e:
                    logger.debug(f"解析价格项失败：{e}")
                    continue
            
            # 如果没有找到具体价格，尝试找"询价"
            if not prices:
                inquiry = self.page.query_selector(".inquiry-button")
                if inquiry:
                    prices.append({
                        "size": "Multiple",
                        "price": 0,
                        "currency": "USD",
                        "stock": "Inquire",
                    })
            
            return {
                "supplier": self.supplier_name,
                "name": name_text,
                "cas": cas_text,
                "url": self.page.url,
                "prices": prices,
                "currency": "USD",
            }
        
        except Exception as e:
            logger.error(f"MCE 页面解析失败：{e}")
            return None
