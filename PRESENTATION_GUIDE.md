# 🎯 化合物监控系统 - 完整使用指南

## 📋 呈现方式总览

系统提供 **5 种呈现方式**，满足不同场景需求：

```
┌─────────────────────────────────────────────┐
│  化合物监控数据                              │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│  ReportGenerator (报告生成器)                │
└─────────────────────────────────────────────┘
         ↓         ↓         ↓         ↓
    ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
    │ JSON │  │  MD  │  │ HTML │  │Discord│
    │Dashboard│  │报告  │  │邮件  │  │消息  │
    └──────┘  └──────┘  └──────┘  └──────┘
```

---

## 🚀 快速开始

### 方式 1：日常监控（Cron）

```bash
# 每天自动执行（已设置 Cron）
python main_monitor.py --mode daily
```

**输出：**
- ✅ `monitor_output/latest_dashboard.json` - JSON 数据
- ✅ `monitor_output/latest_report.md` - Markdown 报告
- ✅ `monitor_output/discord_notification.txt` - Discord 消息

### 方式 2：深度搜索（Subagent）

```bash
# 手动触发深度搜索
python main_monitor.py --mode deep --max-subagent 5
```

**耗时：** 约 5-10 分钟/化合物

### 方式 3：完整监控（推荐）

```bash
# Cron + Subagent 混合模式
python main_monitor.py --mode full --max-subagent 3
```

**流程：**
1. 先运行 Cron 日常监控（60 秒）
2. 对未找到的化合物运行 Subagent（5-10 分钟/个）
3. 合并结果生成报告

---

## 📊 呈现格式详解

### 1️⃣ **JSON Dashboard** - 程序化处理

**文件：** `monitor_output/latest_dashboard.json`

**用途：**
- Web 界面数据源
- 第三方系统集成
- 数据分析

**结构示例：**

```json
{
  "summary": {
    "total_compounds": 20,
    "found": 10,
    "not_found": 10,
    "success_rate": "50.0%",
    "with_papers": 2,
    "with_patents": 1,
    "last_update": "2026-03-11T15:00:00"
  },
  "compounds": [
    {
      "name": "SAL0112",
      "status": "partial",
      "status_emoji": "⚠️",
      "pubchem_cid": null,
      "molecular_weight": null,
      "clinical_stage": "临床 II 期",
      "papers_count": 2,
      "patents_count": 1,
      "papers": [
        {
          "title": "Pharmacodynamic and pharmacokinetic...",
          "journal": "Biomed Pharmacother",
          "pmid": "38925019",
          "year": 2024,
          "url": "https://pubmed.ncbi.nlm.nih.gov/38925019/"
        }
      ],
      "supplier_urls": {
        "MCE": "https://www.medchemexpress.com/catalog.html?q=SAL0112"
      }
    }
  ]
}
```

**查看方式：**

```bash
# 使用 jq 查看摘要
cat monitor_output/latest_dashboard.json | jq '.summary'

# 查看特定化合物
cat monitor_output/latest_dashboard.json | jq '.compounds[] | select(.name=="SAL0112")'

# 查看所有有论文的化合物
cat monitor_output/latest_dashboard.json | jq '.compounds[] | select(.papers_count > 0)'
```

---

### 2️⃣ **Markdown 报告** - 阅读和分享

**文件：** `monitor_output/latest_report.md`

**用途：**
- GitHub/GitLab 文档
- 团队分享
- 打印存档

**预览示例：**

```markdown
# 🧪 化合物监控报告

**更新时间:** 2026-03-11T15:00:00

## 📊 摘要

| 指标 | 数值 |
|------|------|
| 总化合物数 | 20 |
| 找到信息 | 10 |
| 未找到 | 10 |
| 成功率 | 50.0% |
| 有论文 | 2 |
| 有专利 | 1 |

## 📋 化合物详情

### ⚠️ SAL0112

**基本信息:**
- 状态：partial
- 临床阶段：临床 II 期

**相关论文:**
- Pharmacodynamic and pharmacokinetic profiles...
  - *Biomed Pharmacother* (2024)
  - PMID: [38925019](https://pubmed.ncbi.nlm.nih.gov/38925019/)

**供应商链接:**
- MCE: [链接](https://...)

---
```

**查看方式：**

```bash
# 在终端查看
cat monitor_output/latest_report.md

# 在浏览器查看（需要 VSCode 或 Markdown 查看器）
code monitor_output/latest_report.md

# 转换为 PDF（需要 pandoc）
pandoc monitor_output/latest_report.md -o report.pdf
```

---

### 3️⃣ **HTML 邮件** - 邮件发送

**文件：** `monitor_output/email_*.html`

**用途：**
- 邮件订阅
- 美观展示
- 移动端阅读

**特点：**
- ✅ 响应式设计
- ✅ 颜色编码状态
- ✅ 可点击链接
- ✅ 适合邮件客户端

**发送方式：**

```python
# 使用 SMTP 发送
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 读取 HTML
with open('monitor_output/email_20260311_150000.html', 'r') as f:
    html_content = f.read()

# 创建邮件
msg = MIMEMultipart('alternative')
msg['Subject'] = '化合物监控报告 - 2026-03-11'
msg['From'] = 'monitor@example.com'
msg['To'] = 'you@example.com'

# 附加 HTML
msg.attach(MIMEText(html_content, 'html'))

# 发送
with smtplib.SMTP('smtp.example.com', 587) as server:
    server.starttls()
    server.login('user', 'pass')
    server.send_message(msg)
```

---

### 4️⃣ **Discord 消息** - 即时通知

**文件：** `monitor_output/discord_*.txt`

**用途：**
- Discord 频道通知
- Slack 消息
- 即时通讯

**格式示例：**

```
🧪 **化合物监控报告**
更新时间：2026-03-11

📊 **摘要**
总化合物：20
✅ 找到：10
❌ 未找到：10
成功率：50.0%
📄 有论文：2
📜 有专利：1

🎯 **重点发现**
⚠️ **SAL0112**
  临床阶段：临床 II 期
  📄 Pharmacodynamic and pharmacokinetic profiles...
     Biomed Pharmacother (2024)
  📄 Toxicology profile of a novel GLP-1...
     Toxicol Appl Pharmacol (2024)

⚠️ **未找到的化合物**
HSK34890, MDR-001, VCT220 / CX11
```

**发送方式：**

```python
# Discord Webhook
import requests

with open('monitor_output/discord_notification.txt', 'r') as f:
    message = f.read()

webhook_url = "YOUR_DISCORD_WEBHOOK_URL"

payload = {
    "content": message,
    "embeds": [{
        "title": "🧪 化合物监控报告",
        "color": 0x00ff00,
        "footer": {
            "text": f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }]
}

requests.post(webhook_url, json=payload)
```

---

### 5️⃣ **CSV 摘要** - Excel 分析

**文件：** `monitor_output/monitor_summary_*.csv`

**用途：**
- Excel 分析
- 数据透视表
- 趋势图表

**格式：**

```csv
化合物名称，状态，PubChem CID,分子量，分子式，SMILES 来源，MCE 链接，TCI 链接，Enamine 链接
THDBH110,success,44588632,823.9,C39H55F2N5O10S,PubChem (by SMILES),https://...,https://...,https://...
SAL0112,partial,,,,,,,
```

**查看方式：**

```bash
# 在终端查看
cat monitor_output/monitor_summary_*.csv

# 导入 Excel
# 或使用 Python pandas
import pandas as pd
df = pd.read_csv('monitor_output/monitor_summary_20260311_150000.csv')
print(df.describe())
```

---

## 🤖 自动化方案

### 方案 A：每日 Cron + 每周 Subagent

```bash
# Crontab 配置

# 每日凌晨 2 点 - Cron 日常监控
0 2 * * * cd /root/.openclaw/workspace/drug-price-api && python main_monitor.py --mode daily --no-discord >> compound_monitor.log 2>&1

# 每周日早上 3 点 - Subagent 深度搜索（前 5 个未找到的）
0 3 * * 0 cd /root/.openclaw/workspace/drug-price-api && python main_monitor.py --mode deep --max-subagent 5 --no-discord >> compound_monitor.log 2>&1

# 每周一早上 8 点 - 发送 Discord 通知
0 8 * * 1 cd /root/.openclaw/workspace/drug-price-api && python main_monitor.py --mode daily --no-report >> compound_monitor.log 2>&1
```

### 方案 B：完整自动化（推荐）

```bash
# Crontab 配置

# 每日凌晨 2 点 - 完整监控
0 2 * * * cd /root/.openclaw/workspace/drug-price-api && python main_monitor.py --mode full --max-subagent 3 >> compound_monitor.log 2>&1
```

---

## 📱 实际使用场景

### 场景 1：每天早上查看报告

```bash
# 1. 打开最新 Markdown 报告
cat monitor_output/latest_report.md

# 2. 或查看 Discord 消息
cat monitor_output/discord_notification.txt

# 3. 查看有论文的化合物
cat monitor_output/latest_dashboard.json | jq '.compounds[] | select(.papers_count > 0) | {name, papers}'
```

### 场景 2：深度研究特定化合物

```bash
# 对特定化合物运行 Subagent
python main_monitor.py --mode deep --max-subagent 1

# 查看深度搜索结果
cat monitor_output/latest_dashboard.json | jq '.compounds[] | select(.name=="SAL0112")'
```

### 场景 3：团队分享

```bash
# 生成 HTML 邮件
python main_monitor.py --mode daily

# 发送 HTML 邮件
python send_email.py  # 需要自己实现
```

### 场景 4：集成到 Web 界面

```javascript
// 前端读取 JSON Dashboard
fetch('/api/compound-dashboard')
  .then(response => response.json())
  .then(data => {
    console.log(`总化合物：${data.summary.total_compounds}`);
    console.log(`成功率：${data.summary.success_rate}`);
    
    // 渲染化合物列表
    data.compounds.forEach(compound => {
      renderCompound(compound);
    });
  });
```

---

## 🎨 自定义报告样式

### 修改 Markdown 模板

编辑 `report_generator.py` 中的 `generate_markdown_report()` 方法：

```python
def generate_markdown_report(self, dashboard: Dict) -> str:
    md = []
    md.append("# 🧪 化合物监控报告")
    md.append(f"\n**更新时间:** {dashboard['summary']['last_update']}\n")
    
    # 添加自定义部分
    md.append("## 🔬 重点化合物\n")
    
    # 只显示有论文的化合物
    compounds_with_papers = [c for c in dashboard['compounds'] if c.get('papers_count', 0) > 0]
    
    for c in compounds_with_papers:
        md.append(f"### {c['status_emoji']} {c['name']}")
        # ... 自定义内容
    
    return "\n".join(md)
```

### 修改 Discord 消息格式

编辑 `generate_discord_message()` 方法：

```python
def generate_discord_message(self, dashboard: Dict) -> str:
    msg = []
    
    # 自定义消息格式
    msg.append("🔬 **每日化合物监控**")
    msg.append(f"📅 日期：{dashboard['summary']['last_update'][:10]}")
    
    # 只报告重要发现
    important = [c for c in dashboard['compounds'] if c.get('papers_count', 0) > 0]
    
    if important:
        msg.append("\n🎯 **重要发现**")
        for c in important:
            msg.append(f"{c['status_emoji']} **{c['name']}** - {c['papers_count']} 篇论文")
    
    return "\n".join(msg)
```

---

## 📊 数据可视化（可选）

### 使用 Python 生成图表

```python
import matplotlib.pyplot as plt
import json

# 读取 Dashboard
with open('monitor_output/latest_dashboard.json', 'r') as f:
    data = json.load(f)

# 创建饼图
labels = ['找到', '未找到']
sizes = [data['summary']['found'], data['summary']['not_found']]
colors = ['#27ae60', '#e74c3c']

plt.figure(figsize=(8, 6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
plt.title('化合物监控状态')
plt.savefig('monitor_output/status_pie_chart.png')
plt.show()
```

---

## ✅ 总结

| 呈现方式 | 用途 | 优点 | 缺点 |
|---------|------|------|------|
| **JSON Dashboard** | 程序化 | 结构化，易集成 | 不适合阅读 |
| **Markdown** | 文档 | 易读，可打印 | 静态 |
| **HTML 邮件** | 邮件 | 美观，响应式 | 需要邮件服务器 |
| **Discord** | 即时通知 | 快速，互动 | 信息有限 |
| **CSV** | Excel | 可分析，图表 | 信息简化 |

**推荐使用组合：**
- 📱 **每日**：Discord 通知（快速了解）
- 📄 **每周**：Markdown 报告（详细阅读）
- 📊 **每月**：JSON + CSV（数据分析）

---

需要我帮你设置哪种呈现方式？或者需要添加其他格式吗？🚀
