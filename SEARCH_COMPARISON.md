# 爬虫方案对比：Cron vs Subagent

## 📊 当前实现分析

### 方案 A: Cron + 固定爬虫 (当前使用)

```python
# compound_monitor.py
def fetch_pubchem_data(compound_name):
    from pubchempy import get_compounds
    compounds = get_compounds(compound_name, 'name')
    # 固定逻辑，快速但深度有限
```

**优点:**
- ✅ **快速** - 60 秒完成 20 个化合物
- ✅ **稳定** - API 调用，不易失效
- ✅ **低成本** - 免费 API，无 token 消耗
- ✅ **可预测** - 每次执行结果一致

**缺点:**
- ❌ **深度有限** - 仅查询 PubChem
- ❌ **灵活性低** - 无法应对新数据源
- ❌ **覆盖率低** - 临床早期化合物找不到 (35% 成功率)
- ❌ **维护成本** - 网站更新需要手动修复爬虫

---

### 方案 B: OpenClaw Subagent (新方案)

```python
# subagent_deep_search.py
task = f"""
请深度搜索化合物 {compound_name}:
1. PubChem API
2. Google Patents
3. PubMed 论文
4. 供应商网站
5. 临床试验数据库
"""
sessions_spawn(task=task, runtime="subagent")
```

**优点:**
- ✅ **深度搜索** - 多数据源智能搜索
- ✅ **灵活性高** - 自主决定搜索策略
- ✅ **覆盖率高** - 可找到专利/论文中的化合物
- ✅ **智能决策** - 自动切换搜索策略

**缺点:**
- ❌ **慢** - 5-10 分钟/化合物
- ❌ **成本高** - 消耗 token
- ❌ **不稳定** - Subagent 可能超时/失败
- ❌ **不可预测** - 每次搜索结果可能不同

---

## 🎯 性能对比

| 指标 | Cron + 爬虫 | Subagent |
|------|------------|----------|
| **执行时间** | 60 秒 (20 个) | 100-200 分钟 (20 个) |
| **成功率** | 35% | 预计 60-70% |
| **数据深度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **成本** | 免费 | $0.5-2/次 |
| **稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **维护成本** | 中 (需更新爬虫) | 低 (AI 自适应) |

---

## 💡 推荐：混合方案

### 架构设计

```
┌──────────────────────────────────────┐
│  每日 Cron (轻量级)                   │
│  时间：每天 02:00                     │
│  耗时：60 秒                          │
│                                      │
│  - PubChem API 查询                  │
│  - 生成供应商链接                    │
│  - 记录基础数据                      │
│  - 标记"未找到"的化合物              │
└──────────────────────────────────────┘
              │
              ↓ (每周一次)
┌──────────────────────────────────────┐
│  Subagent 深度搜索 (重量级)           │
│  时间：每周日 03:00                   │
│  耗时：100-200 分钟                   │
│                                      │
│  - 搜索"未找到"的化合物              │
│  - 挖掘专利/论文数据                 │
│  - 深度爬取供应商网站                │
│  - 更新补充数据                      │
└──────────────────────────────────────┘
```

### 执行流程

```python
# 每日执行 (compound_monitor.py)
def daily_update():
    compounds = load_compounds()
    results = []
    
    for c in compounds:
        # 快速 PubChem 查询
        data = fetch_pubchem(c['name'])
        results.append(data)
    
    # 标记需要深度搜索的
    need_deep_search = [r for r in results if r['status'] == 'not_found']
    
    # 保存到数据库
    save_results(results)
    
    # 如果累积超过 10 个，触发周任务
    if len(need_deep_search) >= 10:
        trigger_weekly_search(need_deep_search)

# 每周执行 (subagent_deep_search.py)
def weekly_deep_search():
    compounds = load_not_found_compounds()
    
    for c in compounds:
        # Subagent 深度搜索
        result = sessions_spawn(
            task=f"深度搜索化合物：{c['name']}",
            runtime="subagent"
        )
        save_deep_result(result)
```

---

## 📋 实际测试建议

### 第一阶段：测试 Subagent 效果

```bash
# 测试 3 个化合物
python subagent_deep_search.py

# 查看结果
cat monitor_output/deep_search_*.json | jq '.results[] | {compound: .compound, status: .result.status}'
```

**评估指标:**
- 成功率提升多少？
- 平均耗时多少？
- Token 消耗多少？
- 数据质量如何？

### 第二阶段：决定集成策略

**如果 Subagent 成功率 > 60%:**
- ✅ 集成到每周任务
- ✅ 仅搜索"未找到"的化合物
- ✅ 设置预算上限

**如果 Subagent 成功率 < 60%:**
- ❌ 继续使用 Cron 方案
- ❌ 优化现有爬虫
- ❌ 考虑商业 API

---

## 🔧 实现建议

### 1. 修改每日监控

```python
# compound_monitor.py
def run_daily_update():
    results = []
    need_deep_search = []
    
    for compound in compounds:
        result = process_compound(compound)
        results.append(result)
        
        # 标记需要深度搜索的
        if result['status'] == 'not_found':
            need_deep_search.append(compound)
    
    # 保存结果
    save_results(results)
    
    # 累积到一定数量后触发深度搜索
    if len(need_deep_search) >= 5:
        logger.info(f"累积 {len(need_deep_search)} 个未找到化合物，触发深度搜索")
        trigger_subagent_search(need_deep_search)
```

### 2. 设置 Subagent 预算

```python
# 限制 Subagent 使用
MAX_SUBAGENT_PER_WEEK = 10  # 每周最多 10 次
MAX_TOKEN_PER_SEARCH = 50000  # 每次最多 5 万 token

def trigger_subagent_search(compounds):
    # 检查预算
    if weekly_count >= MAX_SUBAGENT_PER_WEEK:
        logger.warning("本周 Subagent 配额已用完")
        return
    
    # 只搜索优先级高的
    priority_compounds = select_priority(compounds, limit=5)
    
    for c in priority_compounds:
        sessions_spawn(
            task=f"深度搜索：{c['name']}",
            timeout_seconds=600,
        )
```

### 3. 结果合并

```python
def merge_results(cron_results, subagent_results):
    """合并 Cron 和 Subagent 的结果"""
    merged = {}
    
    # 先加入 Cron 结果
    for r in cron_results:
        merged[r['name']] = r
    
    # 用 Subagent 结果补充
    for r in subagent_results:
        name = r['compound']
        if name in merged:
            # 合并数据
            merged[name]['deep_search'] = r['result']
            merged[name]['status'] = r['result'].get('status', 'partial')
    
    return list(merged.values())
```

---

## 📊 成本估算

### Cron 方案
```
每日执行：免费
每月成本：$0
```

### Subagent 方案
```
每次搜索：~2000-5000 tokens
Token 成本：$0.002-0.01/次
每周 10 次：$0.02-0.1/周
每月成本：$0.1-0.4
```

### 混合方案
```
每日 Cron: $0
每周 Subagent (10 次): $0.1-0.4
每月总成本：$0.4-1.6
```

---

## ✅ 最终建议

**对于你的需求，我建议：**

1. **继续使用当前 Cron 方案** - 日常监控
2. **手动触发 Subagent** - 针对重要但未找到的化合物
3. **不要全自动 Subagent** - 成本高，时间长
4. **考虑商业 API** - 如果有预算，SciFinder 更可靠

**执行命令:**

```bash
# 每日自动 (Cron)
python compound_monitor.py  # 已在 Cron 中

# 手动深度搜索特定化合物
python subagent_deep_search.py  # 手动执行
```

---

## 📝 总结

| 方案 | 适合场景 | 推荐度 |
|------|---------|--------|
| **Cron + 爬虫** | 日常监控，快速检查 | ⭐⭐⭐⭐⭐ |
| **Subagent** | 深度研究，重要化合物 | ⭐⭐⭐⭐ |
| **混合方案** | 最佳平衡 | ⭐⭐⭐⭐⭐ |
| **商业 API** | 企业级需求，有预算 | ⭐⭐⭐⭐ |

**当前部署:**
- ✅ Cron 已设置（每日 02:00）
- ✅ Subagent 脚本已准备好
- ⏳ 等待你决定是否启用混合方案

需要我帮你设置混合方案吗？🚀
