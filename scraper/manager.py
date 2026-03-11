"""
供应商爬虫管理器
统一管理所有供应商爬虫
"""
from typing import List, Dict, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import BaseScraper
from .mce import MCEScraper
from .tci import TCIScraper
from .enamine import EnamineScraper

logger = logging.getLogger(__name__)


class SupplierScraperManager:
    """供应商爬虫管理器"""
    
    def __init__(self, suppliers: Optional[List[str]] = None):
        """
        初始化爬虫管理器
        
        Args:
            suppliers: 要启用的供应商列表，None 表示全部
        """
        self.suppliers = suppliers or ["mce", "tci", "enamine"]
        self.scrapers: Dict[str, BaseScraper] = {}
        self._init_scrapers()
    
    def _init_scrapers(self):
        """初始化爬虫实例"""
        scraper_classes = {
            "mce": MCEScraper,
            "tci": TCIScraper,
            "enamine": EnamineScraper,
        }
        
        for supplier_key in self.suppliers:
            if supplier_key in scraper_classes:
                self.scrapers[supplier_key] = scraper_classes[supplier_key]()
                logger.info(f"初始化爬虫：{supplier_key}")
    
    def search_all(self, query: str, max_workers: int = 3) -> List[Dict[str, Any]]:
        """
        并行搜索所有供应商
        
        Args:
            query: 化合物查询
            max_workers: 最大并发数
        
        Returns:
            所有供应商的价格信息列表
        """
        results = []
        
        def search_supplier(supplier_key: str, scraper: BaseScraper):
            try:
                logger.info(f"开始搜索 {supplier_key}: {query}")
                result = scraper.search_compound(query)
                if result:
                    logger.info(f"{supplier_key} 搜索成功")
                    return result
                else:
                    logger.warning(f"{supplier_key} 未找到结果")
                    return None
            except Exception as e:
                logger.error(f"{supplier_key} 搜索失败：{e}")
                return None
            finally:
                scraper.stop()
        
        # 并行搜索
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(search_supplier, key, scraper): key
                for key, scraper in self.scrapers.items()
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    if result:
                        results.append(result)
                except Exception as e:
                    supplier = futures[future]
                    logger.error(f"{supplier} 搜索超时或失败：{e}")
        
        return results
    
    def search_sequential(self, query: str) -> List[Dict[str, Any]]:
        """
        顺序搜索所有供应商
        
        Args:
            query: 化合物查询
        
        Returns:
            所有供应商的价格信息列表
        """
        results = []
        
        for supplier_key, scraper in self.scrapers.items():
            try:
                logger.info(f"搜索 {supplier_key}: {query}")
                result = scraper.search_compound(query)
                if result:
                    results.append(result)
                    logger.info(f"{supplier_key} 搜索成功")
                else:
                    logger.warning(f"{supplier_key} 未找到结果")
            except Exception as e:
                logger.error(f"{supplier_key} 搜索失败：{e}")
            finally:
                scraper.stop()
        
        return results
    
    def get_best_price(self, query: str) -> Optional[Dict[str, Any]]:
        """
        获取最优价格
        
        Args:
            query: 化合物查询
        
        Returns:
            最优价格信息
        """
        all_prices = self.search_sequential(query)
        
        if not all_prices:
            return None
        
        # 找出最低价格
        best = None
        best_price = float('inf')
        
        for result in all_prices:
            for price_info in result.get("prices", []):
                price = price_info.get("price", 0)
                if price > 0 and price < best_price:
                    best_price = price
                    best = {
                        "supplier": result.get("supplier"),
                        "name": result.get("name"),
                        "size": price_info.get("size"),
                        "price": price,
                        "currency": price_info.get("currency", "USD"),
                        "stock": price_info.get("stock", "Unknown"),
                        "url": result.get("url"),
                    }
        
        return best
    
    def cleanup(self):
        """清理所有爬虫"""
        for scraper in self.scrapers.values():
            try:
                scraper.stop()
            except Exception as e:
                logger.error(f"清理爬虫失败：{e}")
