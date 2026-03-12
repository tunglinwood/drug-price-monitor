#!/usr/bin/env python3
"""
夜间化合物搜索队列处理器 - 完整 25 个化合物版本
Overnight Compound Search Queue Processor - ALL 25 COMPOUNDS DAILY

从 compound_queue.txt 读取化合物列表
批量启动 Subagent 进行搜索
自动保存结果并更新 Dashboard

使用方法:
    python3 process_queue.py
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from sessions_spawn import sessions_spawn

# 配置
COMPOUND_QUEUE = Path(__file__).parent / "compound_queue.txt"
DELAY_BETWEEN_BATCHES = 300  # 5 分钟间隔
MAX_CONCURRENT = 5  # 最多 5 个并发搜索

def load_compound_queue() -> list:
    """从队列文件加载化合物列表"""
    if not COMPOUND_QUEUE.exists():
        print(f"❌ 队列文件不存在：{COMPOUND_QUEUE}")
        return []
    
    compounds = []
    with open(COMPOUND_QUEUE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if line and not line.startswith('#'):
                compounds.append(line)
    
    return compounds


def launch_batch_search(compounds: list, batch_num: int):
    """批量启动 Subagent 搜索"""
    print(f"\n{'='*60}")
    print(f"🚀 启动第 {batch_num} 批搜索 ({len(compounds)} 个化合物)")
    print(f"{'='*60}")
    
    sessions = []
    for i, compound in enumerate(compounds, 1):
        print(f"[{i}/{len(compounds)}] 🔬 启动搜索：{compound}")
        
        try:
            # 构建搜索任务
            task = f"""请深度搜索化合物 **{compound}** 的完整信息：

**搜索目标：**
1. 化学结构信息 - PubChem CID, SMILES, InChIKey, MW, Formula
2. 供应商信息 - MCE, TCI, Enamine, Sigma
3. 专利信息 - CN/US/WO 专利
4. 研究论文 - PubMed 论文 (PMID, DOI, 期刊)
5. 🏥 临床试验信息 (重要！) - ClinicalTrials.gov NCT 编号，中国药物临床试验登记号
6. 公司信息 - 公司官网研发管线

**返回格式**（严格 JSON）：
```json
{{
  "compound": "{compound}",
  "company": "...",
  "pubchem": {{"cid": ..., "smiles": "...", "mw": ..., "formula": "..."}},
  "suppliers": [...],
  "patents": [...],
  "papers": [...],
  "clinical_trials": [
    {{
      "registry": "ClinicalTrials.gov",
      "trial_id": "NCT 编号",
      "phase": "试验阶段",
      "status": "招募中/已完成",
      "indication": "适应症",
      "enrollment": 受试者人数，
      "url": "https://clinicaltrials.gov/ct2/show/NCT..."
    }}
  ],
  "status": "found|partial|not_found",
  "notes": "..."
}}
```

**注意：** 必须搜索临床试验数据库，找到具体 NCT 编号！
"""
            
            result = sessions_spawn(
                task=task,
                runtime="subagent",
                timeout_seconds=600,
                label=f"daily-{compound.replace('/', '-').replace(' ', '-')}"
            )
            
            sessions.append({
                'compound': compound,
                'session': result
            })
            print(f"   ✅ Subagent 已启动")
            
        except Exception as e:
            print(f"   ❌ 启动失败：{str(e)}")
            sessions.append({
                'compound': compound,
                'error': str(e)
            })
    
    return sessions


def main():
    """主函数"""
    print("="*60)
    print("🌙 夜间化合物搜索启动 - 完整 25 个化合物")
    print("="*60)
    
    # 加载化合物
    compounds = load_compound_queue()
    
    if not compounds:
        print("❌ 队列为空，退出")
        return
    
    total = len(compounds)
    estimated_time = total * DELAY_BETWEEN_BATCHES / 3600  # 小时
    
    print(f"\n📊 队列化合物数量：{total}")
    print(f"⏱️  间隔时间：{DELAY_BETWEEN_BATCHES/60:.0f} 分钟")
    print(f"⏰ 预计完成时间：{estimated_time:.1f} 小时")
    print(f"🕐 预计结束：{datetime.now().timestamp() + estimated_time * 3600:.0f}")
    print()
    
    # 分批搜索 (每批 5 个化合物)
    all_sessions = []
    batch_num = 1
    
    for i in range(0, total, MAX_CONCURRENT):
        batch = compounds[i:i+MAX_CONCURRENT]
        sessions = launch_batch_search(batch, batch_num)
        all_sessions.extend(sessions)
        batch_num += 1
        
        # 等待间隔 (最后一批不需要等待)
        if i + MAX_CONCURRENT < total:
            print(f"\n⏳ 等待 {DELAY_BETWEEN_BATCHES/60:.0f} 分钟后继续下一批...")
            time.sleep(DELAY_BETWEEN_BATCHES)
    
    # 完成总结
    print("\n" + "="*60)
    print("✅ 所有 Subagent 搜索已启动！")
    print("="*60)
    print(f"📊 总化合物数：{total}")
    print(f"🚀 启动成功：{sum(1 for s in all_sessions if 'session' in s)}")
    print(f"❌ 启动失败：{sum(1 for s in all_sessions if 'error' in s)}")
    print(f"📄 日志文件：overnight_search.log")
    print()
    print("🔄 下一步:")
    print("   1. Subagent 完成后自动保存结果")
    print("   2. 等待所有搜索完成 (约 2-3 小时)")
    print("   3. 手动运行 Dashboard 更新脚本")
    print("   4. Git 提交并推送")
    print("="*60)
    
    return all_sessions


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断，退出")
    except Exception as e:
        print(f"\n❌ 错误：{str(e)}")
        raise
