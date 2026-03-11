"""
ChemPrice 服务封装
整合 Molport, ChemSpace, MCule 三个平台的价格查询
"""
from chemprice import PriceCollector
from typing import List, Dict, Optional, Any
import pandas as pd
import logging
from .config import settings

logger = logging.getLogger(__name__)


class ChemPriceService:
    """ChemPrice 价格查询服务"""
    
    def __init__(self):
        self.collector = PriceCollector()
        self._initialized = False
        self._api_keys_configured = False
    
    def initialize(self) -> bool:
        """
        初始化 ChemPrice，配置 API keys
        
        Returns:
            bool: 是否至少有一个 API key 配置成功
        """
        if self._initialized:
            return self._api_keys_configured
        
        self._initialized = True
        
        # 配置 Molport
        if settings.molport_api_key:
            self.collector.setMolportApiKey(settings.molport_api_key)
            logger.info("Molport API key 已配置")
        
        if settings.molport_username and settings.molport_password:
            self.collector.setMolportUsername(settings.molport_username)
            self.collector.setMolportPassword(settings.molport_password)
            logger.info("Molport 用户名密码已配置")
        
        # 配置 ChemSpace
        if settings.chemspace_api_key:
            self.collector.setChemSpaceApiKey(settings.chemspace_api_key)
            logger.info("ChemSpace API key 已配置")
        
        # 配置 MCule
        if settings.mcule_api_key:
            self.collector.setMCuleApiKey(settings.mcule_api_key)
            logger.info("MCule API key 已配置")
        
        # 检查是否至少有一个 API key
        self._api_keys_configured = any([
            settings.molport_api_key,
            (settings.molport_username and settings.molport_password),
            settings.chemspace_api_key,
            settings.mcule_api_key
        ])
        
        return self._api_keys_configured
    
    def check_api_keys(self) -> Dict[str, str]:
        """
        检查 API keys 状态
        
        Returns:
            各平台 API key 状态字典
        """
        if not self._initialized:
            self.initialize()
        
        status = {}
        
        # 检查 Molport
        if settings.molport_api_key or (settings.molport_username and settings.molport_password):
            status["Molport"] = "已配置"
        else:
            status["Molport"] = "未配置"
        
        # 检查 ChemSpace
        if settings.chemspace_api_key:
            status["ChemSpace"] = "已配置"
        else:
            status["ChemSpace"] = "未配置"
        
        # 检查 MCule
        if settings.mcule_api_key:
            status["MCule"] = "已配置"
        else:
            status["MCule"] = "未配置"
        
        return status
    
    def get_prices(self, smiles_list: List[str]) -> List[Dict[str, Any]]:
        """
        获取化合物价格列表
        
        Args:
            smiles_list: SMILES 字符串列表
        
        Returns:
            价格信息列表
        """
        if not self._initialized:
            self.initialize()
        
        if not self._api_keys_configured:
            logger.warning("没有配置任何 API key")
            return []
        
        try:
            # 使用 ChemPrice 收集价格
            all_prices = self.collector.collect(smiles_list)
            
            # 转换为字典列表
            results = []
            for _, row in all_prices.iterrows():
                results.append({
                    "smiles": row.get("Input Smiles", ""),
                    "source": row.get("Source", ""),
                    "supplier": row.get("Supplier Name", ""),
                    "purity": row.get("Purity", ""),
                    "amount": row.get("Amount", ""),
                    "measure": row.get("Measure", ""),
                    "price_usd": row.get("Price_USD", 0),
                    "currency": "USD"
                })
            
            logger.info(f"成功获取 {len(results)} 条价格信息")
            return results
        
        except Exception as e:
            logger.error(f"获取价格失败：{e}")
            return []
    
    def get_best_price(self, smiles: str) -> Optional[Dict[str, Any]]:
        """
        获取最优价格（最便宜）
        
        Args:
            smiles: SMILES 字符串
        
        Returns:
            最优价格信息
        """
        prices = self.get_prices([smiles])
        if not prices:
            return None
        
        # 按价格排序，返回最便宜的
        best = min(prices, key=lambda x: x.get("price_usd", float('inf')))
        return best


# 全局服务实例
chemprice_service = ChemPriceService()
