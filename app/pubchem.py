"""
PubChem API 封装
用于将化合物名称/同义词转换为 SMILES 格式
免费 API，无需 API key
"""
import pubchempy as pcp
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def name_to_smiles(compound_name: str) -> Optional[str]:
    """
    将化合物名称转换为 SMILES 格式
    
    Args:
        compound_name: 化合物名称（如 "Aspirin", "Paracetamol"）
    
    Returns:
        SMILES 字符串，如果找不到则返回 None
    """
    try:
        # 使用 PubChem 搜索化合物
        compound = pcp.get_compounds(compound_name, 'name')[0]
        smiles = compound.isomeric_smiles or compound.smiles
        logger.info(f"化合物 '{compound_name}' → SMILES: {smiles}")
        return smiles
    except Exception as e:
        logger.error(f"转换化合物名称失败 '{compound_name}': {e}")
        return None


def smiles_to_name(smiles: str) -> Optional[str]:
    """
    将 SMILES 转换为化合物名称（反向查询）
    
    Args:
        smiles: SMILES 字符串
    
    Returns:
        化合物名称，如果找不到则返回 None
    """
    try:
        compound = pcp.get_compounds(smiles, 'smiles')[0]
        return compound.iupac_name or compound.synonyms[0] if compound.synonyms else None
    except Exception as e:
        logger.error(f"SMILES 转名称失败 '{smiles}': {e}")
        return None


def search_compound(query: str) -> Optional[dict]:
    """
    搜索化合物信息
    
    Args:
        query: 化合物名称或 SMILES
    
    Returns:
        包含化合物信息的字典
    """
    try:
        # 先尝试作为名称搜索
        compounds = pcp.get_compounds(query, 'name')
        if compounds:
            c = compounds[0]
            return {
                "cid": c.cid,
                "name": c.iupac_name or query,
                "smiles": c.isomeric_smiles or c.smiles,
                "synonyms": c.synonyms[:10] if c.synonyms else [],
                "molecular_weight": c.molecular_weight,
                "formula": c.molecular_formula
            }
        
        # 再尝试作为 SMILES 搜索
        compounds = pcp.get_compounds(query, 'smiles')
        if compounds:
            c = compounds[0]
            return {
                "cid": c.cid,
                "name": c.iupac_name or "Unknown",
                "smiles": c.isomeric_smiles or c.smiles,
                "synonyms": c.synonyms[:10] if c.synonyms else [],
                "molecular_weight": c.molecular_weight,
                "formula": c.molecular_formula
            }
        
        return None
    except Exception as e:
        logger.error(f"搜索化合物失败 '{query}': {e}")
        return None
