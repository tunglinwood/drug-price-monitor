# 化合物每日监控系统

自动从 PubChem 和其他供应商网站爬取化合物信息，每日更新。

## 📋 功能特性

- ✅ **自动查询 PubChem** - 获取化合物基本信息（SMILES、分子量、分子式等）
- ✅ **支持多种输入** - 化合物名称、SMILES、CAS 号
- ✅ **供应商网站检查** - MCE、TCI、Enamine 等
- ✅ **每日自动更新** - Cron 或 Systemd Timer
- ✅ **多种输出格式** - JSON、CSV、Markdown 报告
- ✅ **日志记录** - 完整执行日志

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
cd drug-price-api
pip install -r requirements.txt
pip install python-crontab  # 用于定时任务
```

### 2️⃣ 准备化合物列表

将你的 CSV 文件放到项目目录：

```bash
cp /path/to/your/compounds.csv ./compounds.csv
```

**CSV 格式要求：**

```csv
chem_name,SMILES,InChIKey,IUPAC
THDBH110,CC(C)[C@@H](...),GEMWRCXJLPOQSU-BLNBCHBNSA-N,4-({(S)-2-...
AZD5004,O=C(N1[C@H](...),JMKBTILBGROESC-LITSAYRRSA-N,3-[1-[2-[...
```

### 3️⃣ 手动运行测试

```bash
# 运行一次监控
python compound_monitor.py

# 查看输出
ls -la monitor_output/
```

### 4️⃣ 设置每日自动执行

**方式 A：使用 Cron（推荐）**

```bash
# 设置 cron 任务（每天凌晨 2 点执行）
python setup_scheduler.py cron

# 查看已设置的任务
crontab -l
```

**方式 B：使用 Systemd Timer（Linux）**

```bash
# 创建 service 和 timer
python setup_scheduler.py systemd

# 启用并启动
systemctl --user daemon-reload
systemctl --user enable compound-monitor.timer
systemctl --user start compound-monitor.timer

# 查看状态
systemctl --user status compound-monitor.timer
```

---

## 📁 输出文件

执行后会在 `monitor_output/` 目录生成以下文件：

```
monitor_output/
├── latest_results.json          # 最新结果（覆盖更新）
├── monitor_results_20260311_020000.json  # 历史 JSON
├── monitor_summary_20260311_020000.csv   # 历史 CSV 摘要
└── monitor_report_20260311_020000.md     # Markdown 报告
```

### 输出示例

**JSON 格式：**

```json
{
  "summary": {
    "update_time": "2026-03-11T02:00:00",
    "total_compounds": 20,
    "success": 15,
    "not_found": 5,
    "success_rate": "75.0%"
  },
  "results": [
    {
      "input_name": "THDBH110",
      "status": "success",
      "pubchem_data": {
        "cid": 123456,
        "name": "4-({(S)-2-...",
        "smiles": "CC(C)[C@@H](...",
        "molecular_weight": 616.01,
        "molecular_formula": "C33H24ClF2N3O5"
      },
      "suppliers": {
        "MCE": {"url": "https://..."},
        "TCI": {"url": "https://..."},
        "Enamine": {"url": "https://..."}
      }
    }
  ]
}
```

---

## ⚙️ 配置选项

编辑 `compound_monitor.py` 修改配置：

```python
# 化合物列表路径
csv_path = "compounds.csv"

# 输出目录
output_dir = "monitor_output"

# PubChem API 配置
pubchem_base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# 请求延迟（避免被封）
time.sleep(1)  # 每个化合物间隔 1 秒
```

---

## 📊 查看结果

### 查看最新结果

```bash
# JSON 格式
cat monitor_output/latest_results.json | jq '.summary'

# CSV 格式
cat monitor_output/monitor_summary_*.csv | tail -20
```

### 查看日志

```bash
# 实时查看日志
tail -f compound_monitor.log

# 查看错误
grep ERROR compound_monitor.log
```

---

## 🔧 高级用法

### 1. 集成爬虫系统

编辑 `compound_monitor.py` 中的 `check_supplier_websites` 方法：

```python
from scraper.manager import SupplierScraperManager

def check_supplier_websites(self, compound_name, smiles=None):
    manager = SupplierScraperManager()
    results = manager.search_sequential(compound_name)
    manager.cleanup()
    return results
```

### 2. 发送邮件通知

添加邮件发送功能：

```python
import smtplib
from email.mime.text import MIMEText

def send_email_report(summary, results):
    msg = MIMEText(f"成功：{summary['success']}/{summary['total_compounds']}")
    msg['Subject'] = '化合物监控日报'
    msg['From'] = 'monitor@example.com'
    msg['To'] = 'you@example.com'
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'pass')
        server.send_message(msg)
```

### 3. 推送到 Discord/Slack

```python
import requests

def send_discord_notification(summary):
    webhook_url = "YOUR_DISCORD_WEBHOOK"
    
    payload = {
        "content": f"📊 化合物监控完成\n"
                  f"总计：{summary['total_compounds']}\n"
                  f"成功：{summary['success']}\n"
                  f"成功率：{summary['success_rate']}"
    }
    
    requests.post(webhook_url, json=payload)
```

---

## ⚠️ 注意事项

### 1. PubChem 速率限制

- PubChem 限制每秒请求数
- 建议设置延迟：`time.sleep(1)`
- 大量查询时考虑使用 API key

### 2. 化合物名称问题

- 有些化合物在 PubChem 中可能找不到
- 建议使用 SMILES 查询更准确
- 研发代号（如 HSK34890）可能无收录

### 3. 供应商网站爬虫

- 网站结构可能变化
- 需要定期维护选择器
- 注意反爬措施

### 4. 数据存储

- 定期清理历史文件
- 考虑使用数据库（SQLite/PostgreSQL）
- 备份重要数据

---

## 🐛 故障排除

### Q: 化合物找不到
**A:** 
1. 检查名称拼写
2. 尝试使用 SMILES 查询
3. 可能是新化合物，PubChem 未收录

### Q: 请求被拒绝
**A:**
1. 增加延迟时间
2. 使用代理
3. 减少并发请求

### Q: Cron 任务不执行
**A:**
```bash
# 检查 cron 日志
grep CRON /var/log/syslog

# 检查 cron 服务状态
systemctl status cron

# 手动测试
python compound_monitor.py
```

---

## 📝 示例输出

### Markdown 报告示例

```markdown
# 化合物监控日报

**更新时间:** 2026-03-11 02:00:00

## 摘要

| 指标 | 数值 |
|------|------|
| 总化合物数 | 20 |
| 成功查询 | 15 |
| 未找到 | 5 |
| 成功率 | 75.0% |

## 成功查询的化合物

| 名称 | CID | 分子量 | 分子式 |
|------|-----|--------|--------|
| THDBH110 | 123456 | 616.01 | C33H24ClF2N3O5 |
| DA-302168S | 789012 | 589.04 | C32H22ClF2N3O3 |

## 未找到的化合物

- HSK34890
- SAL0112
- MDR-001
```

---

## 📄 许可证

MIT License

---

## 🔗 相关资源

- [PubChem API 文档](https://pubchemdocs.ncbi.nlm.nih.gov/programmatic-access)
- [PubChemPy 文档](https://pubchempy.readthedocs.io/)
- [Cron 教程](https://crontab.guru/)
