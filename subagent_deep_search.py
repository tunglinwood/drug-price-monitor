"""
使用 OpenClaw Subagent 进行深度化合物搜索
比固定爬虫更智能、更深入
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from sessions_spawn import sessions_spawn
from sessions_list import sessions_list
from sessions_history import sessions_history

logger = logging.getLogger(__name__)


class SubagentDeepSearch:
    """使用 Subagent 进行深度化合物搜索"""
    
    def __init__(self):
        self.output_dir = Path("monitor_output")
        self.output_dir.mkdir(exist_ok=True)
    
    def search_compound_deep(self, compound_name: str, smiles: str = None) -> dict:
        """
        使用 Subagent 深度搜索化合物
        
        Args:
            compound_name: 化合物名称
            smiles: SMILES 字符串（可选）
        
        Returns:
            完整的化合物信息
        """
        logger.info(f"启动 Subagent 深度搜索：{compound_name}")
        
        # 构建搜索任务
        task = f"""
请深度搜索以下化合物信息：

**化合物名称**: {compound_name}
**SMILES**: {smiles or "未知"}

**搜索目标**:
1. PubChem CID、分子量、分子式
2. 化学结构（SMILES、InChIKey）
3. 供应商信息（MCE, TCI, Enamine, Sigma 等）
4. 专利信息（Google Patents, WIPO）
5. 研究论文（PubMed, Google Scholar）
6. 临床试验状态（ClinicalTrials.gov）

**搜索策略**:
- 先用 PubChem API 查询
- 如果找不到，搜索专利数据库
- 检查供应商网站是否有售
- 查找相关研究论文
- 汇总所有信息

**返回格式** (JSON):
```json
{{
  "name": "{compound_name}",
  "pubchem": {{"cid": ..., "mw": ..., "formula": ...}},
  "suppliers": [{{"name": "MCE", "url": "...", "price": "..."}}],
  "patents": [{{"number": "...", "title": "..."}}],
  "papers": [{{"title": "...", "journal": "..."}}],
  "clinical_trials": "...",
  "status": "found|partial|not_found"
}}
```
"""
        
        #  spawn Subagent
        try:
            result = sessions_spawn(
                task=task,
                mode="run",
                runtime="subagent",
                timeout_seconds=600,  # 10 分钟超时
            )
            
            logger.info(f"Subagent 任务已启动：{result}")
            return result
        
        except Exception as e:
            logger.error(f"Subagent 启动失败：{e}")
            return None
    
    def run_weekly_deep_search(self, compounds: list) -> dict:
        """
        每周执行一次深度搜索
        
        Args:
            compounds: 化合物列表
        
        Returns:
            搜索结果汇总
        """
        logger.info(f"开始每周深度搜索，共 {len(compounds)} 个化合物")
        
        results = []
        
        for compound in compounds:
            name = compound.get('chem_name', '')
            smiles = compound.get('SMILES', '')
            
            logger.info(f"\n搜索化合物：{name}")
            
            # 启动 Subagent 搜索
            result = self.search_compound_deep(name, smiles)
            
            if result:
                results.append({
                    "compound": name,
                    "search_time": datetime.now().isoformat(),
                    "result": result,
                })
            
            # 避免并发太高
            import time
            time.sleep(2)
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"deep_search_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "search_time": datetime.now().isoformat(),
                "total_compounds": len(compounds),
                "results": results,
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"深度搜索结果已保存到：{output_path}")
        
        return {
            "summary": {
                "total": len(compounds),
                "searched": len(results),
            },
            "output": str(output_path),
        }


if __name__ == "__main__":
    import csv
    
    # 加载化合物
    compounds = []
    with open('compounds.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            compounds.append(row)
    
    # 只测试前 3 个
    test_compounds = compounds[:3]
    
    # 运行深度搜索
    searcher = SubagentDeepSearch()
    result = searcher.run_weekly_deep_search(test_compounds)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
