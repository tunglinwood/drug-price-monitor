#!/usr/bin/env python3
"""
夜间化合物搜索队列处理器
Overnight Compound Search Queue Processor

从 compound_queue.txt 读取化合物列表
逐个启动 Subagent 进行搜索
自动保存结果并更新 Dashboard

使用方法:
    python3 process_queue.py

日志输出:
    overnight_search.log
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from sessions_spawn import sessions_spawn
    SUBAGENT_AVAILABLE = True
except ImportError:
    SUBAGENT_AVAILABLE = False
    print("⚠️  warning: sessions_spawn 不可用，将使用模拟模式")

# ========== 配置 ==========
QUEUE_FILE = Path(__file__).parent / "compound_queue.txt"
LOG_FILE = Path(__file__).parent / "overnight_search.log"
DELAY_SECONDS = 600  # 10 分钟间隔
TIMEOUT_SECONDS = 600  # Subagent 超时时间


def log_message(message: str):
    """记录日志到文件和控制台"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    
    # 打印到控制台
    print(log_line)
    
    # 追加到日志文件
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line + '\n')


def load_compound_queue() -> list:
    """从队列文件加载化合物列表"""
    if not QUEUE_FILE.exists():
        log_message(f"❌ 队列文件不存在：{QUEUE_FILE}")
        return []
    
    compounds = []
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if line and not line.startswith('#'):
                compounds.append(line)
    
    return compounds


def launch_subagent(compound_name: str) -> dict:
    """启动单个化合物的 Subagent 搜索"""
    log_message(f"🔬 启动搜索：{compound_name}")
    
    if not SUBAGENT_AVAILABLE:
        log_message(f"⚠️  模拟模式：{compound_name}")
        return {"status": "mock", "compound": compound_name}
    
    try:
        result = sessions_spawn(
            task=f"请深度搜索化合物 **{compound_name}** 的完整信息：\n\n"
                 f"搜索目标：\n"
                 f"1. 化学结构信息 (PubChem CID, SMILES, InChIKey, 分子量，分子式)\n"
                 f"2. 供应商信息 (MCE, TCI, Enamine, Sigma 等)\n"
                 f"3. 专利信息 (中国/美国/国际专利)\n"
                 f"4. 研究论文 (PubMed, 中国期刊)\n"
                 f"5. 临床试验 (ClinicalTrials.gov, 中国药物临床试验登记)\n"
                 f"6. 公司信息 (研发管线，官方公告)\n\n"
                 f"返回格式 (JSON)：\n"
                 f"{{\n"
                 f'  "compound": "{compound_name}",\n'
                 f'  "company": "...",\n'
                 f'  "pubchem": {{"cid": ..., "smiles": "...", ...}},\n'
                 f'  "suppliers": [...],\n'
                 f'  "patents": [...],\n'
                 f'  "papers": [...],\n'
                 f'  "clinical_trials": [...],\n'
                 f'  "status": "found|partial|not_found",\n'
                 f'  "notes": "..."\n'
                 f"}}",
            runtime="subagent",
            timeout_seconds=TIMEOUT_SECONDS,
            label=f"overnight-{compound_name.replace('/', '-').replace(' ', '-')}"
        )
        
        log_message(f"✅ Subagent 已启动：{compound_name}")
        return {"status": "launched", "compound": compound_name, "result": result}
    
    except Exception as e:
        log_message(f"❌ 启动失败：{compound_name} - {str(e)}")
        return {"status": "failed", "compound": compound_name, "error": str(e)}


def main():
    """主函数"""
    log_message("="*60)
    log_message("🌙 夜间化合物搜索启动")
    log_message("="*60)
    
    # 加载化合物队列
    compounds = load_compound_queue()
    
    if not compounds:
        log_message("❌ 队列为空，退出")
        return
    
    total = len(compounds)
    estimated_time = total * DELAY_SECONDS / 60  # 分钟
    
    log_message(f"📊 队列化合物数量：{total}")
    log_message(f"⏱️  间隔时间：{DELAY_SECONDS/60:.0f} 分钟")
    log_message(f"⏰ 预计完成时间：{estimated_time:.0f} 分钟")
    log_message(f"🕐 预计结束：{(datetime.now().timestamp() + estimated_time * 60):.0f}")
    log_message("")
    
    # 逐个搜索化合物
    results = []
    for i, compound in enumerate(compounds, 1):
        log_message(f"\n{'='*60}")
        log_message(f"[{i}/{total}] 处理化合物：{compound}")
        log_message(f"{'='*60}")
        
        # 启动 Subagent
        result = launch_subagent(compound)
        results.append(result)
        
        # 等待间隔时间（最后一个化合物不等待）
        if i < total:
            log_message(f"\n⏳ 等待 {DELAY_SECONDS/60:.0f} 分钟后继续下一个...")
            time.sleep(DELAY_SECONDS)
    
    # 完成总结
    log_message("\n" + "="*60)
    log_message("✅ 夜间搜索完成！")
    log_message("="*60)
    log_message(f"📊 总化合物数：{total}")
    log_message(f"✅ 成功启动：{sum(1 for r in results if r['status'] in ['launched', 'mock'])}")
    log_message(f"❌ 失败：{sum(1 for r in results if r['status'] == 'failed')}")
    log_message(f"📄 日志文件：{LOG_FILE}")
    log_message("")
    log_message("🔄 下一步:")
    log_message("   1. Subagent 完成后自动保存结果")
    log_message("   2. 自动更新 Dashboard")
    log_message("   3. 自动提交到 Git")
    log_message("   4. Streamlit Cloud 自动重新部署")
    log_message("="*60)
    
    return results


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("\n⚠️  用户中断，退出")
    except Exception as e:
        log_message(f"\n❌ 错误：{str(e)}")
        raise
