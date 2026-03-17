"""
Subagent 结果自动收集器 - TWO-STEP APPROACH
Step 1: Collect unstructured search results from subagent completion
Step 2: Spawn NEW subagent to extract structured JSON from unstructured data
"""
import json
from datetime import datetime
from pathlib import Path

class SubagentResultCollector:
    """Subagent 结果收集器"""
    
    def __init__(self, results_dir: str = "subagent_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
    
    def save_unstructured_result(self, compound_name: str, search_output: str) -> str:
        """保存非结构化搜索结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{compound_name.replace('/', '_')}_{timestamp}_raw.txt"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(search_output)
        
        print(f"✅ 已保存 {compound_name} 原始搜索结果：{filepath}")
        return str(filepath)
    
    def spawn_extraction_subagent(self, compound_name: str, raw_text_path: str):
        """
        Step 2: Spawn NEW subagent to extract structured data from unstructured search results
        
        This subagent reads the raw search output and extracts:
        - PubChem CID, SMILES, InChIKey, IUPAC
        - Clinical trials (NCT IDs, CTR IDs with URLs)
        - Patents
        - PubMed papers
        - Suppliers
        - Company info
        """
        from sessions_spawn import sessions_spawn
        
        extraction_task = f"""You are a data extraction specialist. Read the search results file and extract structured information.

**Input File**: {raw_text_path}

**Extract the following into STRICT JSON format:**

```json
{{
  "compound": "{compound_name}",
  "company": "Company name in English and Chinese",
  "stage": "Clinical stage (e.g., Phase 1, Phase 2, Approved, Preclinical, Terminated)",
  
  "chemical_identifiers": {{
    "pubchem_cid": "CID number or null if not found",
    "smiles": "SMILES string or null if proprietary/not found",
    "inchikey": "InChIKey or null if proprietary/not found",
    "iupac": "IUPAC name or null if proprietary/not found",
    "molecular_weight": "MW or null",
    "notes": "Any notes about chemical structure (e.g., 'peptide - proprietary')"
  }},
  
  "clinical_trials": [
    {{
      "registry": "ClinicalTrials.gov OR China CTR",
      "trial_id": "NCT number OR CTR number",
      "phase": "Phase 1/2/3",
      "status": "Active/Recruiting/Completed/Terminated",
      "url": "Full URL to trial page"
    }}
  ],
  
  "patents": [
    {{
      "number": "Patent number (CN/US/WO)",
      "status": "Granted/Pending/Withdrawn",
      "title": "Patent title"
    }}
  ],
  
  "pubmed_papers": [
    {{
      "pmid": "PubMed ID",
      "title": "Paper title",
      "year": "Publication year"
    }}
  ],
  
  "suppliers": [
    {{
      "name": "Supplier name (MCE/TCI/Enamine/Sigma)",
      "available": true/false,
      "catalog_number": "Catalog number or null"
    }}
  ],
  
  "key_findings": "Summary of key findings (weight loss %, deals, discontinuations, etc.)",
  
  "data_quality": "verified|partial|not_found",
  "notes": "Any additional notes or limitations"
}}
```

**IMPORTANT RULES:**
1. Only extract data that was ACTUALLY FOUND in the search results
2. If something wasn't found, use null (not "pending" or "unknown")
3. For clinical trials, ONLY include trials with VERIFIED NCT/CTR IDs
4. If a compound is TERMINATED/DISCONTINUED, mark stage clearly
5. Return ONLY the JSON, no other text
"""
        
        try:
            result = sessions_spawn(
                task=extraction_task,
                mode="run",
                runtime="subagent",
                label=f"extract-{compound_name.replace('/', '-')}",
                timeout_seconds=300,  # 5 minutes for extraction
            )
            
            print(f"✅ Extraction subagent spawned for {compound_name}: {result.get('childSessionKey', 'unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Failed to spawn extraction subagent: {e}")
            return None
    
    def save_structured_result(self, compound_name: str, structured_data: dict):
        """保存结构化结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{compound_name.replace('/', '_')}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        # 添加元数据
        structured_data['_metadata'] = {
            'compound': compound_name,
            'search_timestamp': timestamp,
            'extracted_at': datetime.now().isoformat(),
            'method': 'two_step_extraction'
        }
        
        # 保存结果
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已保存 {compound_name} 结构化结果：{filepath}")
        return filepath
    
    def get_all_structured_results(self) -> list:
        """获取所有结构化结果（排除_raw.txt 文件）"""
        results = []
        
        for filepath in sorted(self.results_dir.glob("*.json")):
            if '_raw' not in str(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    results.append(result)
        
        return results
    
    def compile_to_csv(self, output_path: str = "compounds.csv"):
        """Compile all structured results to compounds.csv"""
        import csv
        
        results = self.get_all_structured_results()
        
        if not results:
            print("❌ No structured results to compile")
            return
        
        # CSV fieldnames
        fieldnames = ['chem_name', 'SMILES', 'InChIKey', 'IUPAC', 'Company', 'Stage', 'clinical_trials', 'Notes']
        
        rows = []
        for result in results:
            compound_name = result.get('compound', '')
            chem = result.get('chemical_identifiers', {})
            trials = result.get('clinical_trials', [])
            
            # Format clinical trials for CSV
            if trials:
                trial_strs = []
                for t in trials:
                    if t.get('trial_id'):
                        trial_strs.append(f"{t.get('trial_id')}|{t.get('phase', '')}|{t.get('status', '')}|{t.get('url', '')}")
                clinical_trials = ';'.join(trial_strs)
            else:
                clinical_trials = 'No trials registered'
            
            # Format notes
            notes = result.get('key_findings', result.get('notes', ''))
            
            row = {
                'chem_name': compound_name,
                'SMILES': chem.get('smiles', '') or '',
                'InChIKey': chem.get('inchikey', '') or '',
                'IUPAC': chem.get('iupac', '') or '',
                'Company': result.get('company', ''),
                'Stage': result.get('stage', ''),
                'clinical_trials': clinical_trials,
                'Notes': notes
            }
            rows.append(row)
        
        # Write CSV
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"✅ Compiled {len(rows)} compounds to {output_path}")
        return len(rows)


if __name__ == "__main__":
    # 测试
    collector = SubagentResultCollector()
    
    # 示例：保存非结构化搜索结果
    raw_search = """
    I'll conduct a comprehensive search for NN9487...
    web_search: {"query": "NN9487 PubChem CID..."}
    Found PubChem CID 168438219
    Clinical trials: NCT05369390, NCT06064006
    Weight loss: 13.1% at 12 weeks
    """
    
    raw_path = collector.save_unstructured_result("NN9487", raw_search)
    
    # Step 2: Spawn extraction subagent
    extraction_result = collector.spawn_extraction_subagent("NN9487", raw_path)
    
    print(f"\n📊 Extraction subagent: {extraction_result}")
