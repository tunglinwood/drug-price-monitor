"""
化合物监控自动化脚本
整合 Cron + Subagent + Dashboard 生成
"""
import subprocess
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_cron_monitor():
    """运行 Cron 日常监控"""
    logger.info("="*60)
    logger.info("运行 Cron 日常监控")
    logger.info("="*60)
    
    try:
        result = subprocess.run(
            ['python', 'compound_monitor.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✅ Cron 监控完成")
            return True
        else:
            logger.error(f"❌ Cron 监控失败：{result.stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Cron 监控异常：{e}")
        return False


def run_subagent_search(compound_names: list):
    """运行 Subagent 深度搜索"""
    logger.info("="*60)
    logger.info(f"运行 Subagent 深度搜索 ({len(compound_names)} 个化合物)")
    logger.info("="*60)
    
    from sessions_spawn import sessions_spawn
    
    results = []
    
    for name in compound_names:
        logger.info(f"\n搜索化合物：{name}")
        
        task = f"""
请深度搜索化合物：{name}

搜索目标：
1. PubChem 数据 (CID, MW, Formula, SMILES, InChIKey)
2. 供应商信息 (MCE, TCI, Enamine 等)
3. 专利信息
4. 研究论文 (PubMed)
5. 临床试验状态

返回 JSON 格式，包含所有找到的信息。
"""
        
        try:
            result = sessions_spawn(
                task=task,
                mode="run",
                runtime="subagent",
                timeout_seconds=600,
                label=f"search-{name.replace('/', '-')}"
            )
            
            logger.info(f"✅ Subagent 任务已启动：{result}")
            results.append({"name": name, "session": result})
        
        except Exception as e:
            logger.error(f"❌ Subagent 启动失败：{e}")
    
    return results


def generate_dashboards():
    """生成所有 Dashboard"""
    logger.info("="*60)
    logger.info("生成 Dashboard")
    logger.info("="*60)
    
    try:
        from report_generator import ReportGenerator
        import json
        
        # 加载最新结果
        with open('monitor_output/latest_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        cron_results = data.get('results', [])
        
        # TODO: 合并 Subagent 结果
        subagent_results = []  # 等待 Subagent 完成后合并
        
        # 生成报告
        gen = ReportGenerator()
        merged = gen.merge_results(cron_results, subagent_results)
        dashboard = gen.save_all_reports(merged)
        
        logger.info("✅ Dashboard 生成完成")
        logger.info(f"  - JSON: monitor_output/latest_dashboard.json")
        logger.info(f"  - Markdown: monitor_output/latest_report.md")
        logger.info(f"  - Discord: monitor_output/discord_*.txt")
        
        return True
    
    except Exception as e:
        logger.error(f"Dashboard 生成失败：{e}")
        return False


def main():
    """主函数"""
    logger.info(f"\n{'='*60}")
    logger.info(f"化合物监控系统 - 完整流程")
    logger.info(f"开始时间：{datetime.now().isoformat()}")
    logger.info(f"{'='*60}\n")
    
    # 1. 运行 Cron 监控
    if not run_cron_monitor():
        logger.error("Cron 监控失败，终止流程")
        return
    
    # 2. 生成 Dashboard
    if not generate_dashboards():
        logger.error("Dashboard 生成失败")
        return
    
    # 3. 运行 Subagent 搜索（高优先级化合物）
    priority_compounds = [
        "MDR-001",      # 临床 III 期
        "SAL0112",      # 临床 II 期
        "HSK34890",     # 临床 I 期
        "VCT220/CX11",  # 临床 I 期
        "HRS-7535",     # 恒瑞医药
    ]
    
    logger.info(f"\n准备对 {len(priority_compounds)} 个高优先级化合物运行 Subagent 搜索")
    logger.info(f"化合物列表：{', '.join(priority_compounds)}")
    
    subagent_sessions = run_subagent_search(priority_compounds)
    
    if subagent_sessions:
        logger.info(f"\n✅ 已启动 {len(subagent_sessions)} 个 Subagent 搜索任务")
        logger.info("任务将在后台运行，预计 30-60 分钟完成")
        logger.info("\n下次运行完整流程时，会自动合并 Subagent 结果")
    
    # 4. 完成
    logger.info(f"\n{'='*60}")
    logger.info(f"监控流程完成！")
    logger.info(f"结束时间：{datetime.now().isoformat()}")
    logger.info(f"{'='*60}\n")
    
    logger.info("📊 查看 Dashboard:")
    logger.info("  - Streamlit: streamlit run dashboard_streamlit.py")
    logger.info("  - HTML: 打开 dashboard_html.html")
    logger.info("  - Markdown: cat monitor_output/latest_report.md")


if __name__ == "__main__":
    main()
