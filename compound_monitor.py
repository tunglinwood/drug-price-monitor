"""
化合物每日监控系统
自动从 PubChem 和其他网站爬取化合物信息，每日更新
"""
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from pubchempy import get_compounds
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('compound_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompoundMonitor:
    """化合物监控器"""
    
    def __init__(self, csv_path: str = "compounds.csv", output_dir: str = "monitor_output"):
        self.csv_path = Path(csv_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # PubChem API 基础 URL
        self.pubchem_base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; CompoundMonitor/1.0)"
        }
    
    def load_compounds(self) -> List[Dict[str, str]]:
        """加载化合物列表"""
        compounds = []
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                compounds.append(row)
        
        logger.info(f"加载了 {len(compounds)} 个化合物")
        return compounds
    
    def fetch_pubchem_data(self, compound_name: str) -> Optional[Dict[str, Any]]:
        """
        从 PubChem 获取化合物数据
        
        Args:
            compound_name: 化合物名称
        
        Returns:
            化合物信息字典
        """
        try:
            logger.info(f"查询 PubChem: {compound_name}")
            
            # 使用 PubChemPy 查询
            try:
                compounds = get_compounds(compound_name, 'name')
                
                if not compounds:
                    logger.warning(f"PubChem 未找到：{compound_name}")
                    return None
                
                c = compounds[0]
                
                data = {
                    "cid": c.cid,
                    "name": c.iupac_name or c.synonyms[0] if c.synonyms else compound_name,
                    "smiles": c.isomeric_smiles or c.smiles,
                    "inchikey": c.inchikey,
                    "molecular_weight": c.molecular_weight,
                    "molecular_formula": c.molecular_formula,
                    "synonyms": c.synonyms[:10] if c.synonyms else [],
                    "source": "PubChem",
                    "update_time": datetime.now().isoformat(),
                }
                
                logger.info(f"PubChem 查询成功：{data['name']}")
                return data
            
            except Exception as e:
                logger.error(f"PubChemPy 查询失败：{e}")
                
                # 备用方案：直接使用 REST API
                return self._fetch_pubchem_rest(compound_name)
        
        except Exception as e:
            logger.error(f"PubChem 查询失败：{e}")
            return None
    
    def _fetch_pubchem_rest(self, compound_name: str) -> Optional[Dict[str, Any]]:
        """使用 PubChem REST API 查询（备用方案）"""
        try:
            # 获取 CID
            cid_url = f"{self.pubchem_base_url}/compound/name/{compound_name}/cid/json"
            response = requests.get(cid_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            cid_data = response.json()
            if not cid_data.get('IdentifierList', {}).get('CID'):
                return None
            
            cid = cid_data['IdentifierList']['CID'][0]
            
            # 获取详细信息
            info_url = f"{self.pubchem_base_url}/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IsomericSMILES,InChIKey,IUPACName/json"
            response = requests.get(info_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            info_data = response.json()
            props = info_data.get('PropertyTable', {}).get('Properties', [{}])[0]
            
            return {
                "cid": cid,
                "name": props.get('IUPACName', compound_name),
                "smiles": props.get('IsomericSMILES'),
                "inchikey": props.get('InChIKey'),
                "molecular_weight": props.get('MolecularWeight'),
                "molecular_formula": props.get('MolecularFormula'),
                "synonyms": [],
                "source": "PubChem REST",
                "update_time": datetime.now().isoformat(),
            }
        
        except Exception as e:
            logger.error(f"PubChem REST API 失败：{e}")
            return None
    
    def check_supplier_websites(self, compound_name: str, smiles: str = None) -> Dict[str, Any]:
        """
        检查供应商网站（简化的版本）
        
        Args:
            compound_name: 化合物名称
            smiles: SMILES 字符串
        
        Returns:
            供应商信息
        """
        suppliers = {}
        
        # 这里可以集成之前写的爬虫系统
        # 为了简单，先返回占位数据
        
        suppliers['MCE'] = {
            "available": "unknown",
            "url": f"https://www.medchemexpress.com/catalog.html?q={compound_name}",
            "check_time": datetime.now().isoformat(),
        }
        
        suppliers['TCI'] = {
            "available": "unknown",
            "url": f"https://www.tcichemicals.com/US/en/search?keyword={compound_name}",
            "check_time": datetime.now().isoformat(),
        }
        
        suppliers['Enamine'] = {
            "available": "unknown",
            "url": f"https://enamine.net/chemicals/search?query={compound_name}",
            "check_time": datetime.now().isoformat(),
        }
        
        return suppliers
    
    def process_compound(self, compound: Dict[str, str]) -> Dict[str, Any]:
        """
        处理单个化合物
        
        Args:
            compound: 化合行信息
        
        Returns:
            完整的化合物信息
        """
        name = compound.get('chem_name', '')
        
        logger.info(f"\n{'='*60}")
        logger.info(f"处理化合物：{name}")
        logger.info(f"{'='*60}")
        
        result = {
            "input_name": name,
            "input_smiles": compound.get('SMILES', ''),
            "input_inchikey": compound.get('InChIKey', ''),
            "input_iupac": compound.get('IUPAC', ''),
            "pubchem_data": None,
            "suppliers": {},
            "status": "pending",
        }
        
        # 1. 从 PubChem 获取数据
        pubchem_data = self.fetch_pubchem_data(name)
        
        if pubchem_data:
            result["pubchem_data"] = pubchem_data
            result["status"] = "success"
        else:
            # 如果原始数据有 SMILES，尝试用 SMILES 查询
            if compound.get('SMILES'):
                logger.info(f"尝试用 SMILES 查询：{compound['SMILES'][:50]}...")
                try:
                    compounds = get_compounds(compound['SMILES'], 'smiles')
                    if compounds:
                        c = compounds[0]
                        result["pubchem_data"] = {
                            "cid": c.cid,
                            "name": c.iupac_name or name,
                            "smiles": c.isomeric_smiles or c.smiles,
                            "inchikey": c.inchikey,
                            "molecular_weight": c.molecular_weight,
                            "molecular_formula": c.molecular_formula,
                            "source": "PubChem (by SMILES)",
                            "update_time": datetime.now().isoformat(),
                        }
                        result["status"] = "success"
                except Exception as e:
                    logger.error(f"SMILES 查询失败：{e}")
            
            if result["status"] == "pending":
                result["status"] = "not_found"
        
        # 2. 检查供应商网站
        smiles = None
        if result.get("pubchem_data"):
            smiles = result["pubchem_data"].get("smiles")
        if not smiles:
            smiles = compound.get('SMILES')
        
        result["suppliers"] = self.check_supplier_websites(name, smiles)
        
        return result
    
    def run_daily_update(self) -> Dict[str, Any]:
        """
        执行每日更新
        
        Returns:
            更新结果摘要
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"开始每日更新：{datetime.now().isoformat()}")
        logger.info(f"{'='*60}\n")
        
        # 加载化合物
        compounds = self.load_compounds()
        
        # 处理每个化合物
        results = []
        success_count = 0
        not_found_count = 0
        
        for i, compound in enumerate(compounds, 1):
            logger.info(f"\n进度：{i}/{len(compounds)}")
            
            result = self.process_compound(compound)
            results.append(result)
            
            if result["status"] == "success":
                success_count += 1
            else:
                not_found_count += 1
            
            # 避免请求过快
            if i < len(compounds):
                import time
                time.sleep(1)
        
        # 生成报告
        summary = {
            "update_time": datetime.now().isoformat(),
            "total_compounds": len(compounds),
            "success": success_count,
            "not_found": not_found_count,
            "success_rate": f"{success_count/len(compounds)*100:.1f}%",
        }
        
        # 保存结果
        self.save_results(results, summary)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"更新完成！")
        logger.info(f"总计：{len(compounds)} | 成功：{success_count} | 未找到：{not_found_count}")
        logger.info(f"成功率：{summary['success_rate']}")
        logger.info(f"{'='*60}\n")
        
        return {"summary": summary, "results": results}
    
    def save_results(self, results: List[Dict], summary: Dict):
        """保存结果到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存完整 JSON
        json_path = self.output_dir / f"monitor_results_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "results": results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"结果已保存到：{json_path}")
        
        # 2. 保存 CSV 摘要
        csv_path = self.output_dir / f"monitor_summary_{timestamp}.csv"
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "化合物名称", "状态", "PubChem CID", "分子量", "分子式", 
                "SMILES 来源", "MCE 链接", "TCI 链接", "Enamine 链接"
            ])
            
            for r in results:
                pubchem = r.get("pubchem_data") or {}
                suppliers = r.get("suppliers") or {}
                
                writer.writerow([
                    r.get("input_name"),
                    r.get("status"),
                    pubchem.get("cid"),
                    pubchem.get("molecular_weight"),
                    pubchem.get("molecular_formula"),
                    pubchem.get("source"),
                    suppliers.get("MCE", {}).get("url"),
                    suppliers.get("TCI", {}).get("url"),
                    suppliers.get("Enamine", {}).get("url"),
                ])
        
        logger.info(f"摘要已保存到：{csv_path}")
        
        # 3. 更新最新结果（覆盖）
        latest_json = self.output_dir / "latest_results.json"
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "results": results,
                "last_update": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # 4. 生成 Markdown 报告（简化版）
        md_path = self.output_dir / f"monitor_report_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# 化合物监控日报\n\n")
            f.write(f"**更新时间:** {summary['update_time']}\n\n")
            f.write(f"## 摘要\n\n")
            f.write(f"| 指标 | 数值 |\n|------|------|\n")
            f.write(f"| 总化合物数 | {summary['total_compounds']} |\n")
            f.write(f"| 成功查询 | {summary['success']} |\n")
            f.write(f"| 未找到 | {summary['not_found']} |\n")
            f.write(f"| 成功率 | {summary['success_rate']} |\n\n")


if __name__ == "__main__":
    monitor = CompoundMonitor()
    monitor.run_daily_update()
