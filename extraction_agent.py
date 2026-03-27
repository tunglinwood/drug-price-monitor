"""
提取代理 - 从原始搜索结果中提取结构化 JSON
Extraction Agent - Extract structured JSON from raw search results

输入：原始搜索文本文件
输出：结构化 JSON
"""

import json
from datetime import datetime
from pathlib import Path


def create_extraction_prompt(raw_search_text: str, compound: str) -> str:
    """创建提取任务提示（从原始文本提取 JSON）"""

    return f"""You are a DATA EXTRACTION specialist.

READ the raw search results below and extract structured information into JSON format.

⚠️ CRITICAL INSTRUCTIONS:
1. READ the provided search results ONLY
2. DO NOT search the web (already done!)
3. DO NOT make up data
4. Use null for fields where data is not found
5. Extract ALL available data from the search results

**RAW SEARCH RESULTS TO EXTRACT FROM:**
```
{raw_search_text[:15000]}  # Limit to 15k chars to avoid token limits
```

**EXTRACT INTO THIS JSON FORMAT:**
```json
{{
  "compound": "{compound}",
  "company": "Company name in English and Chinese",
  "stage": "Clinical stage (e.g., Phase 1, Phase 2, Approved, Preclinical, Terminated)",
  
  "chemical_identifiers": {{
    "pubchem_cid": "CID number or null if not found",
    "smiles": "SMILES string or null if proprietary/not found",
    "inchikey": "InChIKey or null if proprietary/not found",
    "iupac": "IUPAC name or null if proprietary/not found",
    "molecular_weight": "MW or null",
    "notes": "Any notes about chemical structure"
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
  
  "key_findings": "Summary of key findings (weight loss %, deals, discontinuations, mechanism, etc.)",
  
  "data_quality": "verified|partial|not_found",
  "notes": "Any additional notes or limitations"
}}
```

**TIMEOUT: 60 seconds**
**Return ONLY JSON, no other text!**
"""


def extract_from_raw(
    raw_filepath: str, compound: str, output_dir: str = "extracted_json"
) -> str:
    """从原始搜索结果提取 JSON 并保存"""

    # Load raw search results
    raw_text = ""
    with open(raw_filepath, encoding="utf-8") as f:
        raw_text = f.read()

    # Create extraction prompt
    prompt = create_extraction_prompt(raw_text, compound)

    # Save prompt to file (for sessions_spawn)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create filename from compound name
    safe_name = (
        compound.replace("/", "_").replace("(", "").replace(")", "").replace(" ", "_")
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save extraction prompt
    prompt_filepath = output_path / f"{safe_name}_{timestamp}_extraction_prompt.txt"
    with open(prompt_filepath, "w", encoding="utf-8") as f:
        f.write(prompt)

    print(f"✅ Extraction prompt saved to: {prompt_filepath}")
    print(f"📝 Raw search file: {raw_filepath}")

    return str(prompt_filepath)


def save_extracted_json(
    compound: str, json_data: dict, output_dir: str = "extracted_json"
) -> str:
    """保存提取的 JSON 到文件"""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create filename from compound name
    safe_name = (
        compound.replace("/", "_").replace("(", "").replace(")", "").replace(" ", "_")
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}_extracted.json"

    # Save JSON
    filepath = output_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted JSON saved to: {filepath}")
    return str(filepath)


# Example usage
if __name__ == "__main__":
    # Example: Extract from NN9487 raw search results
    raw_file = "search_results/NN9487_Amycretin_20260320_092000_raw.txt"
    compound = "NN9487 (Amycretin)"

    print("=" * 70)
    print("EXTRACTION AGENT WORKFLOW:")
    print("=" * 70)
    print(f"1. Load raw search results: {raw_file}")
    print("2. Create extraction prompt")
    print("3. Spawn extraction subagent (60s timeout)")
    print("4. Save extracted JSON")
    print("=" * 70)

    # Create extraction prompt
    prompt_file = extract_from_raw(raw_file, compound)
    print(f"\n✅ Ready to spawn extraction subagent with: {prompt_file}")
