# 🤖 全自动 Dashboard 更新指南

## 📋 方案概述

**自动化流程：**
```
Subagent 完成
    ↓
自动保存结果 → subagent_results/
    ↓
自动更新 Dashboard → monitor_output/latest_dashboard.json
    ↓
自动提交到 GitHub
    ↓
自动推送到远程
    ↓
Streamlit Cloud 自动重新部署（2 分钟）
    ↓
Dashboard 实时更新 ✅
```

---

## 🚀 三种触发方式

### 方式 1：OpenClaw 自动触发（推荐）⭐⭐⭐

**配置 OpenClaw sessions_spawn 回调：**

```python
# 在 OpenClaw 配置中添加
from auto_integration import on_subagent_complete

# Subagent 完成后自动调用
sessions_spawn(
    task="深度搜索化合物...",
    runtime="subagent",
    on_complete=lambda result: on_subagent_complete("MDR-001", result)
)
```

**优点：** 完全自动化，无需人工干预

---

### 方式 2：命令行手动触发

```bash
# Subagent 完成后，手动运行
python auto_integration.py MDR-001 '{"compound": "MDR-001", "status": "partial", ...}'
```

**优点：** 灵活控制，适合测试

---

### 方式 3：GitHub Actions 定时触发

**自动每天凌晨 3 点更新：**

```yaml
# .github/workflows/auto-update-dashboard.yml
on:
  schedule:
    - cron: '0 3 * * *'  # 每天 03:00 UTC
```

**优点：** 定期批量更新

---

## 📁 文件结构

```
drug-price-monitor/
├── .github/
│   └── workflows/
│       └── auto-update-dashboard.yml  # GitHub Actions 配置
├── subagent_results/                   # Subagent 结果目录
│   ├── MDR-001_20260311_200100.json
│   ├── SAL0112_20260311_200500.json
│   └── ...
├── monitor_output/
│   └── latest_dashboard.json          # Dashboard 数据（自动更新）
├── subagent_collector.py              # 结果收集器
├── update_dashboard_from_subagents.py # Dashboard 更新脚本
├── auto_integration.py                # 自动化集成脚本
└── AUTO_UPDATE_GUIDE.md               # 本文档
```

---

## 🔧 配置选项

### 环境变量

```bash
# .env 文件（可选）

# 是否自动推送
AUTO_PUSH=true

# GitHub Token（用于自动推送）
GITHUB_TOKEN=your_token_here

# 保留结果天数
KEEP_RESULTS_DAYS=7
```

---

## 📊 使用示例

### 示例 1：单个化合物搜索

```python
# 启动 Subagent 搜索
from sessions_spawn import sessions_spawn
from auto_integration import on_subagent_complete

result = sessions_spawn(
    task="深度搜索化合物 MDR-001...",
    runtime="subagent",
    timeout_seconds=600
)

# Subagent 完成后自动处理
# （OpenClaw 会自动调用 on_subagent_complete）
```

### 示例 2：批量搜索

```python
# 批量启动多个 Subagent
compounds = ["MDR-001", "SAL0112", "HSK34890"]

for compound in compounds:
    sessions_spawn(
        task=f"深度搜索化合物 {compound}...",
        runtime="subagent",
        label=f"deep-search-{compound}"
    )

# 所有结果会自动收集并更新 Dashboard
```

---

## 🎯 完整工作流

### 步骤 1：启动 Subagent 搜索

```bash
# 方式 A：使用 OpenClaw
python -c "
from sessions_spawn import sessions_spawn
sessions_spawn(
    task='深度搜索化合物 MDR-001...',
    runtime='subagent',
    timeout_seconds=600
)
"

# 方式 B：手动添加任务
# 在 OpenClaw 界面中直接启动
```

### 步骤 2：等待 Subagent 完成

```
⏳ Subagent 搜索中...
预计时间：5-10 分钟
```

### 步骤 3：自动处理（无需人工）

```
✅ Subagent 完成
📥 保存结果到 subagent_results/MDR-001_*.json
🔄 更新 Dashboard
📤 提交到 Git
🚀 推送到 GitHub
⏳ Streamlit Cloud 重新部署中...
✅ Dashboard 已更新
```

### 步骤 4：查看更新后的 Dashboard

```
https://tunglinwood-drug-price-monitor-g2n6ki5f2v8xczavexxlvd.streamlit.app
```

---

## 🔍 监控和调试

### 查看 Subagent 结果

```bash
# 查看所有结果文件
ls -la subagent_results/

# 查看特定结果
cat subagent_results/MDR-001_*.json | jq
```

### 查看 Dashboard 数据

```bash
# 查看 Dashboard JSON
cat monitor_output/latest_dashboard.json | jq '.summary'

# 查看有论文的化合物
cat monitor_output/latest_dashboard.json | jq '.compounds[] | select(.papers_count > 0)'
```

### 查看 Git 状态

```bash
# 查看变更
git status

# 查看提交历史
git log --oneline -10
```

---

## ⚙️ 高级配置

### 配置自动推送

```bash
# 设置 Git 远程仓库
git remote add origin https://github.com/tunglinwood/drug-price-monitor.git

# 配置自动推送
export AUTO_PUSH=true

# 或使用 .env 文件
echo "AUTO_PUSH=true" >> .env
```

### 配置 GitHub Token（可选）

```bash
# 创建 Personal Access Token
# https://github.com/settings/tokens

# 添加为环境变量
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

### 配置结果保留策略

```python
# 在 subagent_collector.py 中修改
collector.clear_old_results(keep_days=7)  # 保留 7 天
```

---

## 📈 性能优化

### 批量更新

```bash
# 收集所有 Subagent 结果后一次性更新
python -c "
from subagent_collector import SubagentResultCollector
from update_dashboard_from_subagents import update_dashboard

collector = SubagentResultCollector()
results = collector.get_all_results()

print(f'共收集 {len(results)} 个结果')
update_dashboard()
"
```

### 增量更新

```bash
# 只更新有新结果的化合物
python auto_integration.py --incremental
```

---

## 🐛 故障排除

### Q: Dashboard 没有自动更新？

**A:** 检查以下几点：
1. Subagent 结果是否保存到 `subagent_results/` 目录
2. `update_dashboard_from_subagents.py` 是否正常运行
3. Git 提交是否成功
4. GitHub Actions 是否触发

```bash
# 检查日志
cat subagent_results/*.json
python update_dashboard_from_subagents.py
git log --oneline -5
```

### Q: Streamlit Cloud 没有重新部署？

**A:** 检查：
1. GitHub 推送是否成功
2. Streamlit Cloud 仓库连接是否正常
3. 查看 Streamlit Cloud 部署日志

### Q: Subagent 结果格式错误？

**A:** 确保 JSON 格式正确：
```bash
# 验证 JSON
cat result.json | jq
```

---

## 📊 监控仪表板

### GitHub Actions 状态

访问：https://github.com/tunglinwood/drug-price-monitor/actions

### Streamlit Cloud 部署状态

访问：https://share.streamlit.io → 你的应用 → Logs

---

## 🎊 完成检查清单

- [ ] ✅ 创建 subagent_results 目录
- [ ] ✅ 配置 subagent_collector.py
- [ ] ✅ 配置 update_dashboard_from_subagents.py
- [ ] ✅ 配置 auto_integration.py
- [ ] ✅ 配置 GitHub Actions
- [ ] ✅ 测试单个化合物更新
- [ ] ✅ 测试批量更新
- [ ] ✅ 验证 Streamlit Cloud 自动部署
- [ ] ✅ 配置监控和告警

---

## 🚀 下一步

**系统已就绪！现在可以：**

1. ✅ 启动 Subagent 搜索
2. ✅ 等待自动更新 Dashboard
3. ✅ 查看 Streamlit Cloud 上的最新数据
4. ✅ 分享 URL 给团队

---

**🎉 全自动 Dashboard 更新系统已部署完成！**

有任何问题随时询问！🚀
