"""
化合物监控系统 - 主控脚本
整合 Cron、Subagent 和报告生成
"""
import json
import csv
import logging
from datetime import datetime
from pathlib import Path
import argparse

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


def load_compounds(csv_path: str = "compounds.csv") -> list:
    """加载化合物列表"""
    compounds = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            compounds.append(row)
    logger.info(f"加载了 {len(compounds)} 个化合物")
    return compounds


def run_cron_monitor():
    """运行 Cron 日常监控"""
    logger.info("\n" + "="*60)
    logger.info("运行 Cron 日常监控")
    logger.info("="*60)
    
    from compound_monitor import CompoundMonitor
    
    monitor = CompoundMonitor()
    results = monitor.run_daily_update()
    
    return results.get('results', [])


def run_subagent_search(compounds: list, max_count: int = 5):
    """运行 Subagent 深度搜索"""
    logger.info("\n" + "="*60)
    logger.info(f"运行 Subagent 深度搜索 (最多 {max_count} 个化合物)")
    logger.info("="*60)
    
    from sessions_spawn import sessions_spawn
    
    # 选择需要深度搜索的化合物（Cron 未找到的）
    need_search = [c for c in compounds if c.get('status') == 'not_found'][:max_count]
    
    if not need_search:
        logger.info("没有需要深度搜索的化合物")
        return []
    
    # 构建搜索任务
    compound_names = [c['input_name'] for c in need_search]
    task = f"""
请深度搜索以下化合物信息：{', '.join(compound_names)}

对每个化合物搜索：
1. PubChem 数据 (CID, MW, Formula, SMILES, InChIKey)
2. 供应商信息 (MCE, TCI, Enamine, Sigma 等)
3. 专利信息 (Google Patents, WIPO)
4. 研究论文 (PubMed)
5. 临床试验状态 (ClinicalTrials.gov)

返回 JSON 格式：
{{
  "compounds": [
    {{
      "name": "化合物名",
      "pubchem": {{"cid": ..., "mw": ..., "formula": "...", "smiles": "...", "inchikey": "..."}},
      "suppliers": [{{"name": "...", "url": "...", "price": "..."}}],
      "patents": [{{"number": "...", "title": "...", "company": "..."}}],
      "papers": [{{"title": "...", "journal": "...", "pmid": "...", "year": ...}}],
      "clinical_trials": {{"status": "...", "identifier": "...", "sponsor": "..."}},
      "status": "found|partial|not_found",
      "notes": "..."
    }}
  ]
}}
"""
    
    try:
        result = sessions_spawn(
            task=task,
            mode="run",
            runtime="subagent",
            timeout_seconds=600,
            label=f"compound-search-{datetime.now().strftime('%Y%m%d')}"
        )
        
        logger.info(f"Subagent 任务已启动：{result}")
        return result
    
    except Exception as e:
        logger.error(f"Subagent 启动失败：{e}")
        return []


def generate_reports(cron_results: list, subagent_results: list):
    """生成所有格式的报告"""
    logger.info("\n" + "="*60)
    logger.info("生成报告")
    logger.info("="*60)
    
    from report_generator import ReportGenerator
    
    generator = ReportGenerator()
    
    # 合并结果
    merged = generator.merge_results(cron_results, subagent_results)
    
    # 生成所有报告
    dashboard = generator.save_all_reports(merged)
    
    return dashboard


def send_discord_notification(dashboard: dict):
    """发送 Discord 通知"""
    logger.info("\n" + "="*60)
    logger.info("发送 Discord 通知")
    logger.info("="*60)
    
    from report_generator import ReportGenerator
    
    generator = ReportGenerator()
    discord_msg = generator.generate_discord_message(dashboard)
    
    # 保存消息到文件（实际使用时通过 Discord API 发送）
    output_dir = Path("monitor_output")
    discord_path = output_dir / "discord_notification.txt"
    
    with open(discord_path, 'w', encoding='utf-8') as f:
        f.write(discord_msg)
    
    logger.info(f"Discord 消息已保存到：{discord_path}")
    logger.info(f"\n{discord_msg}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='化合物监控系统')
    parser.add_argument('--mode', choices=['daily', 'deep', 'full'], default='daily',
                       help='运行模式：daily(日常), deep(深度), full(完整)')
    parser.add_argument('--max-subagent', type=int, default=5,
                       help='Subagent 最大搜索化合物数')
    parser.add_argument('--no-report', action='store_true',
                       help='不生成报告')
    parser.add_argument('--no-discord', action='store_true',
                       help='不发送 Discord 通知')
    
    args = parser.parse_args()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"化合物监控系统启动")
    logger.info(f"运行模式：{args.mode}")
    logger.info(f"时间：{datetime.now().isoformat()}")
    logger.info(f"{'='*60}\n")
    
    # 1. 加载化合物
    compounds = load_compounds()
    
    cron_results = []
    subagent_results = []
    
    # 2. 根据模式运行
    if args.mode in ['daily', 'full']:
        # Cron 日常监控
        cron_result = run_cron_monitor()
        cron_results = cron_result if isinstance(cron_result, list) else []
    
    if args.mode in ['deep', 'full']:
        # Subagent 深度搜索
        subagent_result = run_subagent_search(cron_results, args.max_subagent)
        # 注意：Subagent 结果是异步的，需要等待完成事件
    
    # 3. 生成报告
    if not args.no_report:
        dashboard = generate_reports(cron_results, subagent_results)
        
        # 打印摘要
        logger.info("\n" + "="*60)
        logger.info("报告生成完成！")
        logger.info("="*60)
        logger.info(f"总化合物数：{dashboard['summary']['total_compounds']}")
        logger.info(f"找到信息：{dashboard['summary']['found']}")
        logger.info(f"未找到：{dashboard['summary']['not_found']}")
        logger.info(f"成功率：{dashboard['summary']['success_rate']}")
        logger.info(f"有论文：{dashboard['summary']['with_papers']}")
        logger.info(f"有专利：{dashboard['summary']['with_patents']}")
    
    # 4. 发送 Discord 通知
    if not args.no_discord and args.mode in ['daily', 'full']:
        send_discord_notification(dashboard)
    
    logger.info(f"\n{'='*60}")
    logger.info("监控完成！")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
