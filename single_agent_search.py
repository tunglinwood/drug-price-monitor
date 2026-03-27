"""
单代理搜索 - 返回原始搜索数据（非结构化）
Single Agent Search - Returns raw search data (unstructured)

搜索目标：
1. PubChem CID, SMILES, InChIKey, IUPAC
2. 临床试验 (NCT/CTR IDs)
3. 专利信息
4. PubMed 论文
5. 供应商信息
6. 公司研发管线

输出：原始搜索结果保存到文本文件
"""

from datetime import datetime
from pathlib import Path


def create_search_prompt(compound: str, company: str = "") -> str:
    """创建搜索任务提示（返回原始数据，不要 JSON）"""

    return f"""Comprehensive web search for {compound} {f"({company})" if company else ""}.

SEARCH FOR ALL AVAILABLE INFORMATION:

1. CHEMICAL IDENTIFIERS:
   - PubChem CID number
   - SMILES string
   - InChIKey
   - IUPAC name
   - Molecular weight
   - Molecular formula

2. CLINICAL TRIALS:
   - ClinicalTrials.gov NCT IDs
   - China Drug Trials CTR IDs
   - Trial phase (Phase 1/2/3)
   - Trial status (Active/Recruiting/Completed/Terminated)
   - Trial URLs
   - Indications

3. PATENTS:
   - CN (China) patent numbers
   - US patent numbers
   - WO (WIPO) patent numbers
   - Patent status (Granted/Pending/Withdrawn)

4. PUBLICATIONS:
   - PubMed papers (PMID, title, year)
   - Conference abstracts
   - Journal articles

5. SUPPLIERS:
   - MCE (MedChemExpress) availability
   - TCI Chemicals availability
   - Enamine availability
   - Sigma-Aldrich availability
   - Catalog numbers

6. COMPANY PIPELINE:
   - Development stage
   - Company name (English + Chinese)
   - Licensing deals
   - Recent announcements

7. EFFICACY DATA:
   - Weight loss percentages
   - Trial results
   - Dose-response data
   - Safety profile

SEARCH STRATEGY:
- Use multiple search queries for each category
- Visit ClinicalTrials.gov to verify NCT IDs
- Visit PubChem to verify CID
- Search both English and Chinese sources
- Look for recent data (2025-2026)

OUTPUT FORMAT - TWO PARTS:

==========================================
# PART 1: RAW SEARCH SNIPPETS (UNPROCESSED)
==========================================

For EACH search query, save the RAW snippets:

## Search Query: "NN9487 Amycretin PubChem"
[RAW GOOGLE SEARCH RESULTS]
1. [Title] ... [URL] ... [Snippet] ...
2. [Title] ... [URL] ... [Snippet] ...

## Search Query: "NN9487 site:clinicaltrials.gov"
[RAW CLINICALTRIALS.GOV RESULTS]
[Full trial details as shown on website]

## Search Query: "Amycretin PubMed 2025"
[RAW PUBMED RESULTS]
PMID: XXXXX | Title | Journal | Date | Abstract snippet

... (ALL raw search results for every query)

==========================================
# PART 2: ORGANIZED SUMMARY (PROCESSED)
==========================================

Then provide organized summary:

=== CHEMICAL IDENTIFIERS ===
...

=== CLINICAL TRIALS ===
...

=== KEY FINDINGS ===
...

This ensures NO data is lost - raw snippets preserved for re-extraction!
"""


def save_raw_search_results(
    compound: str, search_output: str, output_dir: str = "search_results"
) -> str:
    """保存原始搜索结果到文本文件"""

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Create filename from compound name
    safe_name = (
        compound.replace("/", "_").replace("(", "").replace(")", "").replace(" ", "_")
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}_raw.txt"

    # Save to file
    filepath = output_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Compound: {compound}\n")
        f.write(f"# Search Date: {datetime.now().isoformat()}\n")
        f.write(f"# {'=' * 70}\n\n")
        f.write(search_output)

    print(f"✅ Raw search results saved to: {filepath}")
    return str(filepath)


def load_raw_search_results(filepath: str) -> str:
    """从文本文件加载原始搜索结果"""
    with open(filepath, encoding="utf-8") as f:
        return f.read()


# Example usage for NN9487 test
if __name__ == "__main__":
    compound = "NN9487 (Amycretin)"
    company = "Novo Nordisk"

    # Create search prompt
    prompt = create_search_prompt(compound, company)

    print("=" * 70)
    print("SEARCH PROMPT FOR SINGLE AGENT:")
    print("=" * 70)
    print(prompt)
    print("=" * 70)
    print("\nThis prompt will be sent to sessions_spawn()")
    print("Raw search results will be saved to search_results/ directory")
