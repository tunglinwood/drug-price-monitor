"""
化合物监控结果整理和呈现系统
整合 Cron 和 Subagent 的结果，生成多种格式的报告
"""
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "monitor_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def merge_results(self, cron_results: List[Dict], subagent_results: List[Dict]) -> List[Dict]:
        """
        合并 Cron 和 Subagent 的结果
        
        Args:
            cron_results: Cron 每日监控结果
            subagent_results: Subagent 深度搜索结果
        
        Returns:
            合并后的完整结果
        """
        merged = {}
        
        # 1. 先加入 Cron 结果
        for r in cron_results:
            name = r.get('input_name', '')
            merged[name] = {
                "name": name,
                "input_data": {
                    "smiles": r.get('input_smiles', ''),
                    "inchikey": r.get('input_inchikey', ''),
                    "iupac": r.get('input_iupac', ''),
                },
                "pubchem": r.get('pubchem_data'),
                "suppliers": r.get('suppliers', {}),
                "status": r.get('status', 'unknown'),
                "last_cron_update": r.get('update_time'),
                "deep_search": None,
            }
        
        # 2. 用 Subagent 结果补充
        for r in subagent_results:
            name = r.get('name', '')
            
            if name in merged:
                # 补充深度搜索数据
                merged[name]['deep_search'] = r
                merged[name]['deep_search']['search_time'] = datetime.now().isoformat()
                
                # 如果 Subagent 找到了而 Cron 没找到，更新状态
                if r.get('status') == 'found' and merged[name]['status'] == 'not_found':
                    merged[name]['status'] = 'partial'
            else:
                # Cron 结果中没有，是新增的化合物
                merged[name] = {
                    "name": name,
                    "input_data": {},
                    "pubchem": None,
                    "suppliers": {},
                    "status": r.get('status', 'unknown'),
                    "last_cron_update": None,
                    "deep_search": r,
                }
        
        return list(merged.values())
    
    def generate_dashboard_json(self, merged_results: List[Dict]) -> Dict:
        """生成 Dashboard JSON 数据"""
        
        # 统计信息
        total = len(merged_results)
        found = sum(1 for r in merged_results if r['status'] in ['success', 'partial'])
        not_found = sum(1 for r in merged_results if r['status'] == 'not_found')
        with_papers = sum(1 for r in merged_results if (r.get('deep_search') or {}).get('papers', []))
        with_patents = sum(1 for r in merged_results if (r.get('deep_search') or {}).get('patents', []))
        
        dashboard = {
            "summary": {
                "total_compounds": total,
                "found": found,
                "not_found": not_found,
                "success_rate": f"{found/total*100:.1f}%" if total > 0 else "0%",
                "with_papers": with_papers,
                "with_patents": with_patents,
                "last_update": datetime.now().isoformat(),
            },
            "compounds": [],
        }
        
        for r in merged_results:
            compound = {
                "name": r['name'],
                "status": r['status'],
                "status_emoji": "✅" if r['status'] == 'success' else "⚠️" if r['status'] == 'partial' else "❌",
                "pubchem_cid": r.get('pubchem', {}).get('cid') if r.get('pubchem') else None,
                "molecular_weight": r.get('pubchem', {}).get('molecular_weight') if r.get('pubchem') else None,
                "clinical_stage": r.get('deep_search', {}).get('clinical_trials', {}).get('status') if r.get('deep_search') else None,
                "papers_count": len(r.get('deep_search', {}).get('papers', [])) if r.get('deep_search') else 0,
                "patents_count": len(r.get('deep_search', {}).get('patents', [])) if r.get('deep_search') else 0,
                "last_cron_update": r.get('last_cron_update'),
                "last_deep_search": r.get('deep_search', {}).get('search_time') if r.get('deep_search') else None,
            }
            
            # 添加供应商链接
            if r.get('suppliers'):
                compound['supplier_urls'] = {
                    k: v.get('url') for k, v in r['suppliers'].items()
                }
            
            # 添加论文信息
            deep_search = r.get('deep_search') or {}
            if deep_search.get('papers'):
                compound['papers'] = [
                    {
                        "title": p.get('title', ''),
                        "journal": p.get('journal', ''),
                        "pmid": p.get('pmid', ''),
                        "year": p.get('year', ''),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{p.get('pmid', '')}/"
                    }
                    for p in deep_search['papers']
                ]
            
            dashboard['compounds'].append(compound)
        
        return dashboard
    
    def generate_markdown_report(self, dashboard: Dict) -> str:
        """生成 Markdown 报告"""
        
        md = []
        md.append("# 🧪 化合物监控报告")
        md.append(f"\n**更新时间:** {dashboard['summary']['last_update']}\n")
        
        # 摘要
        md.append("## 📊 摘要\n")
        md.append("| 指标 | 数值 |")
        md.append("|------|------|")
        md.append(f"| 总化合物数 | {dashboard['summary']['total_compounds']} |")
        md.append(f"| 找到信息 | {dashboard['summary']['found']} |")
        md.append(f"| 未找到 | {dashboard['summary']['not_found']} |")
        md.append(f"| 成功率 | {dashboard['summary']['success_rate']} |")
        md.append(f"| 有论文 | {dashboard['summary']['with_papers']} |")
        md.append(f"| 有专利 | {dashboard['summary']['with_patents']} |\n")
        
        # 化合物列表
        md.append("## 📋 化合物详情\n")
        
        for c in dashboard['compounds']:
            md.append(f"### {c['status_emoji']} {c['name']}\n")
            
            # 基本信息
            md.append("**基本信息:**")
            md.append(f"- 状态：{c['status']}")
            if c['pubchem_cid']:
                md.append(f"- PubChem CID: [{c['pubchem_cid']}](https://pubchem.ncbi.nlm.nih.gov/compound/{c['pubchem_cid']})")
            if c['molecular_weight']:
                md.append(f"- 分子量：{c['molecular_weight']}")
            if c['clinical_stage']:
                md.append(f"- 临床阶段：{c['clinical_stage']}")
            md.append("")
            
            # 论文
            if c.get('papers'):
                md.append("**相关论文:**")
                for paper in c['papers']:
                    md.append(f"- {paper['title']}")
                    md.append(f"  - *{paper['journal']}* ({paper['year']})")
                    md.append(f"  - PMID: [{paper['pmid']}]({paper['url']})")
                md.append("")
            
            # 供应商
            if c.get('supplier_urls'):
                md.append("**供应商链接:**")
                for supplier, url in c['supplier_urls'].items():
                    md.append(f"- {supplier}: [{url}]({url})")
                md.append("")
            
            md.append("---\n")
        
        return "\n".join(md)
    
    def generate_discord_message(self, dashboard: Dict) -> str:
        """生成 Discord 消息格式"""
        
        msg = []
        msg.append("🧪 **化合物监控报告**")
        msg.append(f"更新时间：{dashboard['summary']['last_update'][:10]}\n")
        
        # 摘要
        msg.append("📊 **摘要**")
        msg.append(f"总化合物：{dashboard['summary']['total_compounds']}")
        msg.append(f"✅ 找到：{dashboard['summary']['found']}")
        msg.append(f"❌ 未找到：{dashboard['summary']['not_found']}")
        msg.append(f"成功率：{dashboard['summary']['success_rate']}")
        msg.append(f"📄 有论文：{dashboard['summary']['with_papers']}")
        msg.append(f"📜 有专利：{dashboard['summary']['with_patents']}\n")
        
        # 重点化合物（有论文的）
        compounds_with_papers = [c for c in dashboard['compounds'] if c.get('papers_count', 0) > 0]
        
        if compounds_with_papers:
            msg.append("🎯 **重点发现**")
            for c in compounds_with_papers:
                msg.append(f"{c['status_emoji']} **{c['name']}**")
                msg.append(f"  临床阶段：{c['clinical_stage'] or '未知'}")
                if c.get('papers'):
                    for paper in c['papers'][:2]:  # 最多显示 2 篇
                        msg.append(f"  📄 {paper['title'][:80]}...")
                        msg.append(f"     {paper['journal']} ({paper['year']})")
                msg.append("")
        
        # 未找到的化合物
        not_found = [c for c in dashboard['compounds'] if c['status'] == 'not_found']
        if not_found:
            msg.append("⚠️ **未找到的化合物**")
            msg.append(", ".join([c['name'] for c in not_found]))
        
        return "\n".join(msg)
    
    def generate_email_html(self, dashboard: Dict) -> str:
        """生成邮件 HTML"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .summary table {{ width: 100%; border-collapse: collapse; }}
        .summary td {{ padding: 8px; border-bottom: 1px solid #bdc3c7; }}
        .compound {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .compound.success {{ border-left: 4px solid #27ae60; }}
        .compound.partial {{ border-left: 4px solid #f39c12; }}
        .compound.not_found {{ border-left: 4px solid #e74c3c; }}
        .paper {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .footer {{ margin-top: 30px; color: #7f8c8d; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>🧪 化合物监控报告</h1>
    <p><strong>更新时间:</strong> {dashboard['summary']['last_update']}</p>
    
    <div class="summary">
        <h2>📊 摘要</h2>
        <table>
            <tr><td>总化合物数</td><td>{dashboard['summary']['total_compounds']}</td></tr>
            <tr><td>找到信息</td><td>{dashboard['summary']['found']}</td></tr>
            <tr><td>未找到</td><td>{dashboard['summary']['not_found']}</td></tr>
            <tr><td>成功率</td><td>{dashboard['summary']['success_rate']}</td></tr>
            <tr><td>有论文</td><td>{dashboard['summary']['with_papers']}</td></tr>
            <tr><td>有专利</td><td>{dashboard['summary']['with_patents']}</td></tr>
        </table>
    </div>
    
    <h2>📋 化合物详情</h2>
"""
        
        for c in dashboard['compounds']:
            status_class = c['status']
            status_emoji = c['status_emoji']
            
            html += f"""
    <div class="compound {status_class}">
        <h3>{status_emoji} {c['name']}</h3>
        <p><strong>状态:</strong> {c['status']}</p>
"""
            
            if c['pubchem_cid']:
                html += f'<p><strong>PubChem CID:</strong> <a href="https://pubchem.ncbi.nlm.nih.gov/compound/{c["pubchem_cid"]}">{c["pubchem_cid"]}</a></p>'
            
            if c['molecular_weight']:
                html += f'<p><strong>分子量:</strong> {c["molecular_weight"]}</p>'
            
            if c['clinical_stage']:
                html += f'<p><strong>临床阶段:</strong> {c["clinical_stage"]}</p>'
            
            if c.get('papers'):
                html += '<h4>相关论文:</h4>'
                for paper in c['papers']:
                    html += f"""
        <div class="paper">
            <p><strong>{paper['title']}</strong></p>
            <p><em>{paper['journal']}</em> ({paper['year']})</p>
            <p>PMID: <a href="{paper['url']}">{paper['pmid']}</a></p>
        </div>
"""
            
            html += "    </div>\n"
        
        html += f"""
    <div class="footer">
        <p>此报告由化合物监控系统自动生成</p>
        <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def save_all_reports(self, merged_results: List[Dict]):
        """保存所有格式的报告"""
        
        # 1. 生成 Dashboard JSON
        dashboard = self.generate_dashboard_json(merged_results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 2. 保存 Dashboard JSON
        dashboard_path = self.output_dir / f"dashboard_{timestamp}.json"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
        # 3. 保存 Markdown 报告
        md_content = self.generate_markdown_report(dashboard)
        md_path = self.output_dir / f"report_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # 4. 保存 Discord 消息
        discord_msg = self.generate_discord_message(dashboard)
        discord_path = self.output_dir / f"discord_{timestamp}.txt"
        with open(discord_path, 'w', encoding='utf-8') as f:
            f.write(discord_msg)
        
        # 5. 保存邮件 HTML
        email_html = self.generate_email_html(dashboard)
        email_path = self.output_dir / f"email_{timestamp}.html"
        with open(email_path, 'w', encoding='utf-8') as f:
            f.write(email_html)
        
        # 6. 保存最新结果（覆盖）
        latest_dashboard = self.output_dir / "latest_dashboard.json"
        with open(latest_dashboard, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
        latest_md = self.output_dir / "latest_report.md"
        with open(latest_md, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"报告已保存到 {self.output_dir}")
        logger.info(f"  - Dashboard JSON: {dashboard_path}")
        logger.info(f"  - Markdown 报告：{md_path}")
        logger.info(f"  - Discord 消息：{discord_path}")
        logger.info(f"  - 邮件 HTML: {email_path}")
        
        return dashboard


if __name__ == "__main__":
    # 测试
    generator = ReportGenerator()
    
    # 示例数据
    cron_results = [
        {
            "input_name": "THDBH110",
            "status": "success",
            "pubchem_data": {"cid": 44588632, "molecular_weight": 823.9},
            "suppliers": {"MCE": {"url": "https://..."}},
        }
    ]
    
    subagent_results = [
        {
            "name": "SAL0112",
            "status": "partial",
            "clinical_trials": {"status": "临床 II 期"},
            "papers": [
                {
                    "title": "Pharmacodynamic and pharmacokinetic profiles...",
                    "journal": "Biomed Pharmacother",
                    "pmid": "38925019",
                    "year": 2024
                }
            ],
        }
    ]
    
    merged = generator.merge_results(cron_results, subagent_results)
    dashboard = generator.save_all_reports(merged)
    
    print(f"生成完成！化合物数：{dashboard['summary']['total_compounds']}")
