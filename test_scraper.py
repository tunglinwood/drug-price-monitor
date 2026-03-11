"""
供应商爬虫测试脚本
"""
import logging
import json
from scraper.manager import SupplierScraperManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_single_supplier():
    """测试单个供应商"""
    from scraper.mce import MCEScraper
    
    logger.info("=== 测试 MCE 爬虫 ===")
    
    with MCEScraper() as scraper:
        result = scraper.search_compound("Aspirin")
        
        if result:
            logger.info("搜索成功！")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            logger.warning("未找到结果")


def test_all_suppliers():
    """测试所有供应商"""
    logger.info("=== 测试所有供应商爬虫 ===")
    
    manager = SupplierScraperManager()
    
    try:
        # 测试化合物
        test_compounds = [
            "Aspirin",
            "Paracetamol",
            "Caffeine",
        ]
        
        for compound in test_compounds:
            logger.info(f"\n{'='*50}")
            logger.info(f"搜索化合物：{compound}")
            logger.info(f"{'='*50}")
            
            results = manager.search_sequential(compound)
            
            if results:
                logger.info(f"找到 {len(results)} 个供应商的结果")
                
                for result in results:
                    print(f"\n供应商：{result.get('supplier')}")
                    print(f"产品名称：{result.get('name')}")
                    print(f"URL: {result.get('url')}")
                    
                    prices = result.get('prices', [])
                    if prices:
                        print("价格信息:")
                        for price in prices:
                            print(f"  - {price.get('size')}: {price.get('price')} {price.get('currency')} ({price.get('stock')})")
            else:
                logger.warning("所有供应商都未找到结果")
            
            # 清理当前爬虫
            manager.cleanup()
            manager = SupplierScraperManager()
    
    finally:
        manager.cleanup()


def test_best_price():
    """测试获取最优价格"""
    logger.info("=== 测试获取最优价格 ===")
    
    manager = SupplierScraperManager()
    
    try:
        best = manager.get_best_price("Aspirin")
        
        if best:
            logger.info("找到最优价格！")
            print(json.dumps(best, indent=2, ensure_ascii=False))
        else:
            logger.warning("未找到价格信息")
    
    finally:
        manager.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "single":
            test_single_supplier()
        elif test_type == "all":
            test_all_suppliers()
        elif test_type == "best":
            test_best_price()
        else:
            print("用法：python test_scraper.py [single|all|best]")
    else:
        print("用法：python test_scraper.py [single|all|best]")
        print("\n示例:")
        print("  python test_scraper.py single  # 测试单个供应商")
        print("  python test_scraper.py all     # 测试所有供应商")
        print("  python test_scraper.py best    # 获取最优价格")
