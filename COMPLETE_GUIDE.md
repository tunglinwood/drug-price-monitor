# 🎯 化合物监控系统 - 完整使用指南

## 📊 Dashboard 总览

系统提供 **3 种 Dashboard**，满足不同场景需求：

| Dashboard | 用途 | 打开方式 | 特点 |
|-----------|------|---------|------|
| **Streamlit** | 日常交互式查看 | `streamlit run dashboard_streamlit.py` | ⭐⭐⭐⭐⭐ 交互式，美观 |
| **HTML** | 浏览器查看/邮件发送 | 双击 `dashboard_html.html` | ⭐⭐⭐⭐ 静态，兼容性好 |
| **Markdown** | 文档/打印 | `cat monitor_output/latest_report.md` | ⭐⭐⭐ 简单，可打印 |

---

## 🚀 快速开始

### 方式 1：一键运行完整流程

```bash
cd ~/.openclaw/workspace/drug-price-api
python run_full_monitor.py
```

**执行内容：**
1. ✅ Cron 日常监控（PubChem 查询）
2. ✅ 生成所有 Dashboard
3. ✅ 启动 Subagent 深度搜索（5 个高优先级化合物）

**预计耗时：**
- Cron 监控：~70 秒
- Dashboard 生成：~5 秒
- Subagent 搜索：~30-60 分钟（后台运行）

---

### 方式 2：分开执行

#### A. 只运行 Cron 监控

```bash
python compound_monitor.py
```

#### B. 只生成 Dashboard

```bash
python -c "from report_generator import ReportGenerator; print('Dashboard 已生成')"
```

#### C. 手动触发 Subagent 搜索

```bash
# 对特定化合物搜索
python -c "
from sessions_spawn import sessions_spawn
sessions_spawn(
    task='深度搜索化合物：MDR-001',
    runtime='subagent',
    timeout_seconds=600
)
"
```

---

## 🖥️ 查看 Dashboard

### 1️⃣ Streamlit Dashboard（推荐）

**安装 Streamlit：**
```bash
pip install streamlit pandas
```

**启动 Dashboard：**
```bash
streamlit run dashboard_streamlit.py
```

**功能：**
- ✅ 交互式筛选/排序
- ✅ 实时刷新
- ✅ 导出 CSV/JSON
- ✅ 查看详细信息
- ✅ 自动刷新（可选）

**访问地址：** http://localhost:8501

---

### 2️⃣ HTML Dashboard

**打开方式：**
```bash
# Linux/Mac
xdg-open dashboard_html.html  # Linux
open dashboard_html.html      # Mac

# Windows
start dashboard_html.html

# 或直接双击文件
```

**功能：**
- ✅ 浏览器直接打开
- ✅ 筛选/搜索
- ✅ 点击查看详细信息
- ✅ 导出 JSON/CSV
- ✅ 响应式设计

---

### 3️⃣ Markdown 报告

**查看方式：**
```bash
# 终端查看
cat monitor_output/latest_report.md

# VSCode 查看
code monitor_output/latest_report.md

# 转换为 PDF
pandoc monitor_output/latest_report.md -o report.pdf
```

---

## 📁 文件结构

```
drug-price-api/
├── compounds.csv                    # 化合物列表 (24 个)
├── compound_monitor.py              # Cron 监控脚本
├── run_full_monitor.py              # 完整流程脚本 ⭐
├── dashboard_streamlit.py           # Streamlit Dashboard ⭐
├── dashboard_html.html              # HTML Dashboard ⭐
├── report_generator.py              # 报告生成器
├── main_monitor.py                  # 主控脚本
├── setup_scheduler.py               # Cron 设置
├── TRACKING_LIST.md                 # 追踪清单文档
├── PRESENTATION_GUIDE.md            # 呈现方式指南
└── monitor_output/                  # 输出目录
    ├── latest_dashboard.json        # JSON Dashboard
    ├── latest_report.md             # Markdown 报告
    ├── discord_*.txt                # Discord 通知
    ├── monitor_results_*.json       # 历史 JSON
    └── monitor_summary_*.csv        # 历史 CSV
```

---

## ⚙️ 自动化设置

### 设置每日 Cron 任务

```bash
# 设置 Cron（每天凌晨 2 点）
python setup_scheduler.py cron

# 验证设置
crontab -l

# 查看 Cron 日志
tail -f /var/log/cron | grep compound
```

### 手动触发

```bash
# 每日监控
python compound_monitor.py

# 完整流程（包含 Subagent）
python run_full_monitor.py
```

---

## 📊 数据流

```
化合物列表 (compounds.csv)
    ↓
Cron 监控 (PubChem API)
    ↓
生成基础报告
    ↓
标记"未找到"的化合物
    ↓
Subagent 深度搜索
    ↓
合并结果
    ↓
生成 Dashboard
    ↓
┌──────────────┬──────────────┬──────────────┐
│  Streamlit   │    HTML      │  Markdown    │
│  Dashboard   │  Dashboard   │   报告       │
└──────────────┴──────────────┴──────────────┘
```

---

## 🎯 使用场景

### 场景 1：每天早上查看最新状态

```bash
# 打开 Streamlit Dashboard
streamlit run dashboard_streamlit.py

# 或查看 Discord 通知
cat monitor_output/discord_*.txt
```

### 场景 2：深度分析特定化合物

1. 打开 Streamlit Dashboard
2. 搜索化合物名称
3. 点击查看详细信息
4. 查看论文/专利/供应商链接

### 场景 3：导出报告给团队

```bash
# 导出 HTML（邮件发送）
# 打开 dashboard_html.html，另存为 PDF

# 导出 CSV（Excel 分析）
# 在 Streamlit 中点击"导出 CSV"

# 导出 JSON（程序处理）
# 在 Streamlit 中点击"导出 JSON"
```

### 场景 4：查看历史趋势

```bash
# 合并所有历史 CSV
cat monitor_output/monitor_summary_*.csv | grep -v "化合物名称" > all_history.csv

# 用 Excel 打开分析趋势
```

---

## 🔧 故障排除

### Q: Streamlit 无法启动
**A:**
```bash
# 检查安装
pip install streamlit pandas

# 检查端口占用
lsof -i :8501

# 使用其他端口
streamlit run dashboard_streamlit.py --server.port 8502
```

### Q: HTML Dashboard 无法打开
**A:**
```bash
# 检查文件是否存在
ls -la dashboard_html.html

# 用浏览器直接打开文件路径
file:///root/.openclaw/workspace/drug-price-api/dashboard_html.html
```

### Q: 数据不更新
**A:**
```bash
# 清除缓存（Streamlit）
# 在浏览器中按 Ctrl+R 强制刷新

# 重新运行监控
python compound_monitor.py
```

### Q: Subagent 搜索失败
**A:**
```bash
# 检查 sessions_spawn 导入
python -c "from sessions_spawn import sessions_spawn; print('OK')"

# 手动测试单个化合物
# 参考 run_full_monitor.py 中的 run_subagent_search 函数
```

---

## 📈 性能优化

### 加快搜索速度

1. **减少 Subagent 数量**
   ```python
   # 只搜索最优先的 3 个
   priority_compounds = ["MDR-001", "SAL0112", "HSK34890"]
   ```

2. **并行搜索**
   ```python
   # 同时启动多个 Subagent
   from concurrent.futures import ThreadPoolExecutor
   ```

3. **使用缓存**
   ```python
   # 避免重复搜索
   @st.cache_data
   def load_data():
       ...
   ```

---

## 🎊 总结

**你现在拥有：**

✅ **3 种 Dashboard** - Streamlit / HTML / Markdown  
✅ **自动化监控** - 每日 Cron + Subagent 深度搜索  
✅ **完整报告** - JSON / CSV / Discord 通知  
✅ **交互式界面** - 筛选/排序/导出/详情查看  

**开始使用：**

```bash
# 1. 运行完整监控
python run_full_monitor.py

# 2. 打开 Streamlit Dashboard
streamlit run dashboard_streamlit.py

# 3. 享受交互式监控体验！
```

---

**🎉 化合物监控系统已完全就绪！**

有任何问题随时询问！🚀
