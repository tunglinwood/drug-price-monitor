"""
Enamine 爬虫
https://enamine.net/
"""
from typing import Optional, Dict, Any
import logging
import re
from .base import BaseScraper

logger = logging.getLogger(__name__)


class EnamineScraper(BaseScraper):
    """Enamine 爬虫"""
    
    supplier_name = "Enamine"
    base_url = "https://enamine.net"
    
    def search_compound(self, query: str) -> Optional[Dict[str, Any]]:
        """
        搜索 Enamine 化合物
        
        Args:
            query: 化合物名称、SMILES 或 Enamine ID
        
        Returns:
            价格信息字典
        """
        try:
            if not self.page:
                self.start()
            
            # Enamine 搜索
            search_url = f"{self.base_url}/chemicals/search?query={query}"
            logger.info(f"搜索 Enamine: {query}")
            
            # 访问搜索页面
            self.page.goto(search_url, wait_until="networkidle", timeout=settings.timeout_ms)
            self.random_delay(3000, 6000)
            
            # 等待搜索结果加载
            self.page.wait_for_selector(".product-card", timeout=10000)
            
            # 检查是否有搜索结果
            product_links = self.page.query_selector_all(".product-card a")
            
            if not product_links:
                logger.warning(f"Enamine 未找到化合物：{query}")
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
            logger.error(f"Enamine 搜索失败：{e}")
            self.take_screenshot(f"enamine_error_{query.replace(' ', '_')}.png")
            return None
    
    def parse_price_page(self) -> Optional[Dict[str, Any]]:
        """解析 Enamine 产品页面"""
        try:
            # 获取产品名称
            name = self.page.query_selector("h1.product-name")
            name_text = name.inner_text().strip() if name else ""
            
            # 获取 Enamine ID
            enamine_id = self.page.query_selector(".enamine-id")
            id_text = enamine_id.inner_text().strip() if enamine_id else ""
            
            # 获取 SMILES
            smiles = self.page.query_selector(".smiles-string")
            smiles_text = smiles.get_attribute("data-smiles") or (smiles.inner_text().strip() if smiles else "")
            
            # 获取价格信息
            prices = []
            
            # Enamine 通常有多个规格
            size_options = self.page.query_selector_all(".size-selector option")
            
            for size_elem in size_options:
                try:
                    size = size_elem.get_attribute("value")
                    if not size:
                        continue
                    
                    # 获取该规格的价格
                    price_elem = self.page.query_selector(f".price[data-size='{size}']")
                    price_text = price_elem.inner_text().strip() if price_elem else ""
                    
                    # 提取价格数字
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price_value = float(price_match.group(1).replace(',', '')) if price_match else 0
                    
                    # 库存状态
                    stock_elem = self.page.query_selector(f".stock[data-size='{size}']")
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
            
            # 如果没有找到具体价格
            if not prices:
                # 尝试获取"Add to cart"按钮旁的价格
                price_elem = self.page.query_selector(".price-main")
                if price_elem:
                    price_text = price_elem.inner_text().strip()
                    price_match = re.search(r'\$?([\d,]+\.?\d*)', price_text)
                    price_value = float(price_match.group(1).replace(',', '')) if price_match else 0
                    
                    prices.append({
                        "size": "Standard",
                        "price": price_value,
                        "currency": "USD",
                        "stock": "In Stock",
                    })
            
            return {
                "supplier": self.supplier_name,
                "name": name_text,
                "enamine_id": id_text,
                "smiles": smiles_text,
                "url": self.page.url,
                "prices": prices,
                "currency": "USD",
            }
        
        except Exception as e:
            logger.error(f"Enamine 页面解析失败：{e}")
            return None
