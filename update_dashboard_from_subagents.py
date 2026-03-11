"""
将 Subagent 搜索结果更新到 Dashboard
自动合并所有 Subagent 结果，生成最新 Dashboard
"""
import json
from datetime import datetime
from pathlib import Path

# Subagent 搜索结果（从完成的消息中复制）
SUBAGENT_RESULTS = [
    # MDR-001
    {
        "name": "MDR-001",
        "company": "德睿智药",
        "clinical_stage": "临床 III 期",
        "pubchem": {"cid": None, "smiles": None, "inchikey": None, "mw": None, "formula": None},
        "papers": [],
        "patents": [],
        "suppliers": [{"name": "MCE", "url": "https://www.medchemexpress.cn/search.html?q=MDR-001", "price": "询价"}],
        "clinical_trials": [],
        "notes": "中国首个 AI 设计 III 期创新药",
        "status": "partial"
    },
    # HSK34890
    {
        "name": "HSK34890",
        "company": "海思科",
        "clinical_stage": "临床 I 期",
        "pubchem": {"cid": None, "smiles": None, "inchikey": None, "mw": None, "formula": None},
        "papers": [],
        "patents": [{"number": "CN114591296A", "title": "GLP-1R 激动剂及其在医药上的应用", "date": "2022-06-07", "status": "Withdrawn"}],
        "suppliers": [],
        "clinical_trials": [{"status": "临床 I 期", "approval_date": "2023-08"}],
        "notes": "2023 年 8 月获批临床",
        "status": "partial"
    },
    # VCT220/CX11
    {
        "name": "VCT220/CX11",
        "company": "闻泰生物/箕星药业",
        "clinical_stage": "临床 I 期",
        "pubchem": {"cid": None, "smiles": None, "inchikey": None, "mw": None, "formula": None},
        "papers": [],
        "patents": [],
        "suppliers": [],
        "clinical_trials": [],
        "notes": "公开数据库无信息",
        "status": "not_found"
    },
    # HRS-7535
    {
        "name": "HRS-7535",
        "company": "恒瑞医药/山东盛迪",
        "clinical_stage": "临床 I 期",
        "pubchem": {"cid": None, "smiles": None, "inchikey": None, "mw": None, "formula": None},
        "papers": [
            {
                "pmid": "38100147",
                "title": "Safety, pharmacokinetics and pharmacodynamics of HRS-7535...",
                "journal": "Diabetes Obes Metab",
                "year": 2024,
                "doi": "10.1111/dom.15383",
                "url": "https://pubmed.ncbi.nlm.nih.gov/38100147/",
                "key_findings": "体重降低 6.63%，每日一次口服"
            }
        ],
        "patents": [],
        "suppliers": [],
        "clinical_trials": [{"phase": "Phase 1", "status": "completed", "results": "体重降低 6.63%"}],
        "notes": "Phase 1 完成，疗效显著",
        "status": "partial"
    },
    # SAL0112
    {
        "name": "SAL0112",
        "company": "信立泰",
        "clinical_stage": "临床 II 期",
        "pubchem": {"cid": None, "smiles": None, "inchikey": None, "mw": None, "formula": None},
        "papers": [
            {
                "pmid": "38925019",
                "title": "Pharmacodynamic and pharmacokinetic profiles of a novel GLP-1 receptor biased agonist-SAL0112",
                "journal": "Biomed Pharmacother",
                "year": 2024,
                "doi": "10.1016/j.biopha.2024.116965",
                "url": "https://pubmed.ncbi.nlm.nih.gov/38925019/"
            },
            {
                "pmid": "39395609",
                "title": "Toxicology profile of a novel GLP-1 receptor biased agonist-SAL0112 in nonhuman primates",
                "journal": "Toxicol Appl Pharmacol",
                "year": 2024,
                "doi": "10.1016/j.taap.2024.117125",
                "url": "https://pubmed.ncbi.nlm.nih.gov/39395609/"
            }
        ],
        "patents": [{"owner": "深圳信立泰药业", "status": "Patent owner confirmed"}],
        "suppliers": [],
        "clinical_trials": [{"status": "临床 II 期"}],
        "notes": "偏向性激动剂，心血管安全性优于 Danuglipron",
        "status": "partial"
    }
]


def update_dashboard():
    """更新 Dashboard 数据"""
    
    # 加载现有 Dashboard
    dashboard_path = Path("monitor_output/latest_dashboard.json")
    
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            dashboard = json.load(f)
    else:
        # 创建新 Dashboard
        dashboard = {
            "summary": {},
            "compounds": []
        }
    
    # 合并 Subagent 结果
    existing_names = {c['name'] for c in dashboard.get('compounds', [])}
    
    for subagent_result in SUBAGENT_RESULTS:
        # 找到或创建化合物条目
        compound = next((c for c in dashboard['compounds'] if c.get('name') == subagent_result['name']), None)
        
        if compound is None:
            # 创建新条目
            compound = {
                "name": subagent_result['name'],
                "status": subagent_result['status'],
                "status_emoji": "⚠️" if subagent_result['status'] == 'partial' else "❌",
                "clinical_stage": subagent_result.get('clinical_stage'),
                "pubchem_cid": None,
                "molecular_weight": None,
                "papers_count": len(subagent_result.get('papers', [])),
                "patents_count": len(subagent_result.get('patents', [])),
                "supplier_urls": {s['name']: s['url'] for s in subagent_result.get('suppliers', [])},
                "papers": subagent_result.get('papers', []),
                "patents": subagent_result.get('patents', []),
                "clinical_trials": subagent_result.get('clinical_trials', []),
                "notes": subagent_result.get('notes', ''),
                "last_deep_search": datetime.now().isoformat()
            }
            dashboard['compounds'].append(compound)
        else:
            # 更新现有条目
            compound['status'] = subagent_result['status']
            compound['status_emoji'] = "⚠️" if subagent_result['status'] == 'partial' else "❌"
            compound['papers_count'] = len(subagent_result.get('papers', []))
            compound['patents_count'] = len(subagent_result.get('patents', []))
            compound['papers'] = subagent_result.get('papers', [])
            compound['patents'] = subagent_result.get('patents', [])
            compound['clinical_trials'] = subagent_result.get('clinical_trials', [])
            compound['notes'] = subagent_result.get('notes', '')
            compound['last_deep_search'] = datetime.now().isoformat()
    
    # 更新摘要
    total = len(dashboard['compounds'])
    found = sum(1 for c in dashboard['compounds'] if c['status'] in ['success', 'partial'])
    not_found = sum(1 for c in dashboard['compounds'] if c['status'] == 'not_found')
    with_papers = sum(1 for c in dashboard['compounds'] if c.get('papers_count', 0) > 0)
    with_patents = sum(1 for c in dashboard['compounds'] if c.get('patents_count', 0) > 0)
    
    dashboard['summary'] = {
        "total_compounds": total,
        "found": found,
        "not_found": not_found,
        "success_rate": f"{found/total*100:.1f}%" if total > 0 else "0%",
        "with_papers": with_papers,
        "with_patents": with_patents,
        "last_update": datetime.now().isoformat(),
        "last_subagent_update": datetime.now().isoformat()
    }
    
    # 保存更新后的 Dashboard
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, indent=2, ensure_ascii=False)
    
    print("="*60)
    print("✅ Dashboard 已更新！")
    print("="*60)
    print(f"\n📊 摘要:")
    print(f"  总化合物：{total}")
    print(f"  找到信息：{found}")
    print(f"  未找到：{not_found}")
    print(f"  成功率：{dashboard['summary']['success_rate']}")
    print(f"  有论文：{with_papers}")
    print(f"  有专利：{with_patents}")
    
    print(f"\n🔬 Subagent 搜索贡献:")
    print(f"  - MDR-001: 供应商信息")
    print(f"  - HSK34890: 专利信息")
    print(f"  - HRS-7535: 1 篇论文 + 临床数据")
    print(f"  - SAL0112: 2 篇论文")
    
    print(f"\n📁 文件已保存：{dashboard_path}")
    print(f"\n🚀 下一步:")
    print(f"  1. git add monitor_output/latest_dashboard.json")
    print(f"  2. git commit -m 'Update: Subagent 搜索结果'")
    print(f"  3. git push")
    print(f"  4. Streamlit Cloud 自动重新部署（2 分钟）")
    
    return dashboard


if __name__ == "__main__":
    update_dashboard()
