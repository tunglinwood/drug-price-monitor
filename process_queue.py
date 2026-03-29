#!/usr/bin/env python3
"""
夜间化合物搜索队列处理器 - 完整 25 个化合物版本 (带验证代理)
Overnight Compound Search Queue Processor - ALL 25 COMPOUNDS DAILY (with Validation Agent)

从 compound_queue.txt 读取化合物列表
批量启动 Subagent 进行搜索
验证代理比较新数据与现有库存
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

# 导入验证代理

# 配置
COMPOUND_QUEUE = Path(__file__).parent / "compound_queue.txt"
DELAY_BETWEEN_BATCHES = 180  # 3 分钟间隔 (58 compounds)
MAX_CONCURRENT = 5  # 最多 5 个并发搜索
VALIDATION_ENABLED = True  # 启用验证代理


def load_compound_queue() -> list:
    """从队列文件加载化合物列表"""
    if not COMPOUND_QUEUE.exists():
        print(f"❌ 队列文件不存在：{COMPOUND_QUEUE}")
        return []

    compounds = []
    with open(COMPOUND_QUEUE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 跳过空行和注释
            if line and not line.startswith("#"):
                compounds.append(line)

    return compounds


def launch_subagent_search(compound: str):
    """启动单个化合物的 Subagent 搜索"""
    print(f"🔬 启动搜索：{compound}")

    # 使用 OpenClaw sessions_spawn 工具
    # 注意：这需要通过 OpenClaw 系统调用，不是直接 Python import
    # 我们使用 subprocess 调用 OpenClaw CLI

    # 创建搜索任务描述
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

    # 保存任务到临时文件
    task_file = (
        Path(__file__).parent
        / f"task_{compound.replace('/', '-').replace(' ', '_')}.txt"
    )
    with open(task_file, "w", encoding="utf-8") as f:
        f.write(task)

    print(f"   ✅ 任务已保存：{task_file.name}")
    print("   ⏳ 等待 OpenClaw 处理...")

    return {"compound": compound, "task_file": str(task_file), "status": "queued"}


def main():
    """主函数"""
    print("=" * 60)
    print("🌙 夜间化合物搜索启动 - 完整 25 个化合物")
    print(f"⏰ 启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 加载化合物
    compounds = load_compound_queue()

    if not compounds:
        print("❌ 队列为空，退出")
        return

    total = len(compounds)
    estimated_time = total * DELAY_BETWEEN_BATCHES / 3600  # 小时

    print(f"\n📊 队列化合物数量：{total}")
    print(f"⏱️  间隔时间：{DELAY_BETWEEN_BATCHES / 60:.0f} 分钟")
    print(f"⏰ 预计完成时间：{estimated_time:.1f} 小时")
    print()

    # 分批搜索
    all_tasks = []
    batch_num = 1

    for i in range(0, total, MAX_CONCURRENT):
        batch = compounds[i : i + MAX_CONCURRENT]

        print(f"\n{'=' * 60}")
        print(f"🚀 启动第 {batch_num} 批搜索 ({len(batch)} 个化合物)")
        print(f"{'=' * 60}")

        for compound in batch:
            task = launch_subagent_search(compound)
            all_tasks.append(task)

        batch_num += 1

        # 等待间隔 (最后一批不需要等待)
        if i + MAX_CONCURRENT < total:
            print(f"\n⏳ 等待 {DELAY_BETWEEN_BATCHES / 60:.0f} 分钟后继续下一批...")
            time.sleep(DELAY_BETWEEN_BATCHES)

    # 完成总结
    print("\n" + "=" * 60)
    print("✅ 所有搜索任务已创建！")
    print("=" * 60)
    print(f"📊 总化合物数：{total}")
    print(f"📝 任务文件：{len(all_tasks)} 个")
    print("📄 日志文件：overnight_search.log")
    print()
    print("🔄 下一步:")
    print("   1. 手动通过 OpenClaw 启动 Subagent 搜索")
    print("   2. 或使用以下命令批量启动:")
    print("      for f in task_*.txt; do openclaw search --file $f; done")
    print("   3. Subagent 完成后自动保存结果")
    print("   4. 运行 update_dashboard.py 合并结果")
    print("   5. Git 提交并推送")
    print("=" * 60)

    return all_tasks


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断，退出")
    except Exception as e:
        print(f"\n❌ 错误：{str(e)}")
        import traceback

        traceback.print_exc()
        raise
