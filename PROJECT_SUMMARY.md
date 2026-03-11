# 🧪 化合物自动监控系统 - 完整部署指南

## ✅ 项目已完成

你的化合物每日监控系统已经搭建完成！

---

## 📁 项目结构

```
drug-price-api/
├── compounds.csv                    # 你的化合物列表 ⭐
├── compound_monitor.py              # 监控主程序 ⭐
├── setup_scheduler.py               # 定时任务设置 ⭐
├── MONITOR_README.md                # 监控文档
├── app/                             # FastAPI 主程序
│   ├── main.py                      # API endpoints
│   ├── config.py                    # 配置
│   ├── pubchem.py                   # PubChem API
│   └── chemprice_service.py         # ChemPrice 服务
├── scraper/                         # 供应商爬虫系统
│   ├── base.py                      # 基础爬虫类
│   ├── config.py                    # 爬虫配置
│   ├── mce.py                       # MCE 爬虫
│   ├── tci.py                       # TCI 爬虫
│   ├── enamine.py                   # Enamine 爬虫
│   └── manager.py                   # 爬虫管理器
├── test_scraper.py                  # 爬虫测试脚本
├── SCRAPER_README.md                # 爬虫文档
├── requirements.txt                 # Python 依赖
└── monitor_output/                  # 输出目录 ⭐
    ├── latest_results.json          # 最新结果
    ├── monitor_results_*.json       # 历史 JSON
    ├── monitor_summary_*.csv        # 历史 CSV
    └── monitor_report_*.md          # Markdown 报告
```

---

## 🚀 快速使用

### 1️⃣ 手动运行监控

```bash
cd ~/.openclaw/workspace/drug-price-api
python compound_monitor.py
```

### 2️⃣ 查看结果

```bash
# 查看最新结果
cat monitor_output/latest_results.json | jq '.summary'

# 查看 CSV 摘要
cat monitor_output/monitor_summary_*.csv

# 查看 Markdown 报告
cat monitor_output/monitor_report_*.md
```

### 3️⃣ 设置每日自动执行

**Linux/Mac - 使用 Cron:**

```bash
python setup_scheduler.py cron
crontab -l  # 验证已设置
```

**Linux - 使用 Systemd:**

```bash
python setup_scheduler.py systemd
systemctl --user daemon-reload
systemctl --user enable compound-monitor.timer
systemctl --user start compound-monitor.timer
systemctl --user status compound-monitor.timer
```

---

## 📊 测试结果

**首次运行结果：**

```
总计：20 个化合物
成功：7 个 (35%)
未找到：13 个

成功查询的化合物：
✅ THDBH110      - CID: 44588632, MW: 823.9
✅ AZD5004       - CID: 167350327, MW: 880.9
✅ LY3549492     - PubChem 直接找到
✅ LY3502970     - PubChem 直接找到
✅ DA-302168S    - 通过 SMILES 找到
✅ GZR18         - 通过 SMILES 找到
✅ HDM1002       - 通过 SMILES 找到
```

**未找到的化合物（临床早期，PubChem 未收录）：**
- HSK34890
- SAL0112
- MDR-001
- VCT220 / CX11
- 等等...

---

## 💡 提高成功率的方法

### 1. 添加 SMILES 数据

对于 PubChem 找不到的化合物，在 CSV 中添加 SMILES：

```csv
chem_name,SMILES,InChIKey,IUPAC
HSK34890,ClC1=CC=C(...),ZWQNIWWZDWNMQA-QFIPXVFZSA-N,(S)-2-(4-(...
```

### 2. 集成供应商爬虫

编辑 `compound_monitor.py` 的 `check_supplier_websites` 方法：

```python
from scraper.manager import SupplierScraperManager

def check_supplier_websites(self, compound_name, smiles=None):
    """使用爬虫检查供应商"""
    manager = SupplierScraperManager()
    results = manager.search_sequential(compound_name)
    manager.cleanup()
    return results
```

### 3. 使用商业数据库

如果有预算，可以集成：
- CAS SciFinder
- Reaxys
- Cortellis

---

## ⏰ 定时任务配置

### Cron 时间表

```bash
# 每天凌晨 2 点执行
0 2 * * * cd /root/.openclaw/workspace/drug-price-api && /usr/bin/python3 compound_monitor.py >> compound_monitor.log 2>&1

# 每周一上午 9 点执行
0 9 * * 1 cd /root/.openclaw/workspace/drug-price-api && /usr/bin/python3 compound_monitor.py >> compound_monitor.log 2>&1
```

### 查看执行日志

```bash
# 实时查看日志
tail -f compound_monitor.log

# 查看错误
grep ERROR compound_monitor.log

# 查看成功更新
grep "更新完成" compound_monitor.log
```

---

## 📧 添加通知功能

### 邮件通知

```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification(summary):
    msg = MIMEText(f"""
    化合物监控完成
    
    总计：{summary['total_compounds']}
    成功：{summary['success']}
    未找到：{summary['not_found']}
    成功率：{summary['success_rate']}
    """)
    
    msg['Subject'] = '化合物监控日报'
    msg['From'] = 'monitor@example.com'
    msg['To'] = 'you@example.com'
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login('user', 'pass')
        server.send_message(msg)
```

### Discord/Slack 通知

```python
import requests

def send_discord_notification(summary):
    webhook_url = "YOUR_DISCORD_WEBHOOK"
    
    payload = {
        "embeds": [{
            "title": "📊 化合物监控完成",
            "color": 0x00ff00,
            "fields": [
                {"name": "总计", "value": str(summary['total_compounds']), "inline": True},
                {"name": "成功", "value": str(summary['success']), "inline": True},
                {"name": "成功率", "value": summary['success_rate'], "inline": True},
            ]
        }]
    }
    
    requests.post(webhook_url, json=payload)
```

---

## 🔧 常见问题

### Q: 为什么很多化合物找不到？
**A:** 
- 这些是临床早期化合物，PubChem 还未收录
- 解决方案：添加 SMILES 数据，或使用供应商爬虫

### Q: 如何加快查询速度？
**A:**
- 减少延迟时间（但有被封风险）
- 使用多线程（需谨慎）
- 购买商业 API

### Q: 如何备份数据？
**A:**
```bash
# 定期备份 monitor_output 目录
tar -czf monitor_backup_$(date +%Y%m%d).tar.gz monitor_output/
```

### Q: 如何查看历史趋势？
**A:**
```bash
# 合并所有 CSV 文件
cat monitor_output/monitor_summary_*.csv | grep -v "化合物名称" > all_history.csv
```

---

## 📈 下一步优化

1. **添加数据库支持**
   - SQLite/PostgreSQL 存储历史数据
   - 查询趋势分析

2. **集成更多数据源**
   - 供应商爬虫系统
   - 商业数据库 API
   - 专利数据库

3. **改进通知系统**
   - 邮件通知
   - Discord/Slack/微信
   - 价格变化告警

4. **Web 界面**
   - Flask/Django 管理界面
   - 数据可视化
   - 手动触发更新

---

## 📄 许可证

MIT License

---

## 🔗 相关资源

- [PubChem API 文档](https://pubchemdocs.ncbi.nlm.nih.gov/)
- [Cron 教程](https://crontab.guru/)
- [Playwright 文档](https://playwright.dev/python/)

---

## ✅ 完成清单

- [x] 化合物 CSV 导入
- [x] PubChem 自动查询
- [x] 支持 SMILES 查询
- [x] 多格式输出（JSON/CSV/MD）
- [x] 定时任务设置
- [x] 日志记录
- [ ] 供应商爬虫集成（可选）
- [ ] 邮件/消息通知（可选）
- [ ] 数据库存储（可选）
- [ ] Web 管理界面（可选）

---

**🎉 系统已就绪！开始自动监控你的化合物吧！**
