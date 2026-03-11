# 🧪 化合物监控系统 - Streamlit Cloud 部署

## 📋 部署清单

### ✅ 已准备文件

- [x] `dashboard_streamlit.py` - Streamlit Dashboard 主程序
- [x] `requirements.txt` - Python 依赖
- [x] `.streamlit/config.toml` - Streamlit 配置
- [x] `.gitignore` - Git 忽略文件
- [x] `compounds.csv` - 化合物列表（示例）
- [x] `README.md` - 项目说明

### ⚠️ 需要注意的文件

**不要上传到 GitHub：**
- ❌ `.env` - 环境变量（包含 API keys）
- ❌ `monitor_output/` - 监控数据（包含敏感信息）
- ❌ `*.log` - 日志文件
- ❌ `scraper/` - 爬虫代码（Streamlit Cloud 无法使用）

---

## 🚀 部署步骤

### 1️⃣ 创建 GitHub 仓库

**方式 A：使用 GitHub 网页**

1. 访问 https://github.com/new
2. 仓库名：`drug-price-monitor`
3. 描述：`化合物监控系统 - Compound Price Monitoring System`
4. 选择 **Public**（公开）或 **Private**（私有）
5. 点击 **Create repository**

**方式 B：使用命令行**

```bash
cd ~/.openclaw/workspace/drug-price-api

# 修改默认分支为 main
git branch -M main

# 添加远程仓库（替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/drug-price-monitor.git

# 推送代码
git push -u origin main
```

---

### 2️⃣ 部署到 Streamlit Cloud

1. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io

2. **登录/注册**
   - 使用 GitHub 账号登录

3. **添加新应用**
   - 点击 **"New app"**

4. **配置应用**
   ```
   Repository: YOUR_USERNAME/drug-price-monitor
   Branch: main
   Main file path: dashboard_streamlit.py
   ```

5. **高级设置（可选）**
   ```
   Python Version: 3.10
   Memory: 1GB (免费)
   ```

6. **点击 Deploy!**

---

### 3️⃣ 等待部署完成

**部署过程：**
```
⏳ Building... (约 2-5 分钟)
✅ Running!
```

**访问地址：**
```
https://yourusername-drug-price-monitor-app-xxxxxx.streamlit.app
```

---

## ⚙️ 配置优化

### 使用公开数据

由于 Streamlit Cloud 无法访问本地文件，需要：

**1. 使用公开化合物数据**
```python
# dashboard_streamlit.py 修改
@st.cache_data
def load_data():
    # 从 GitHub 读取公开数据
    url = "https://raw.githubusercontent.com/YOUR_USERNAME/drug-price-monitor/main/compounds.csv"
    return pd.read_csv(url)
```

**2. 移除本地文件依赖**
```python
# 注释掉需要本地文件的代码
# from scraper.manager import SupplierScraperManager
# from sessions_spawn import sessions_spawn
```

**3. 使用示例数据**
```python
# 准备示例 dashboard 数据
SAMPLE_DATA = {
    "summary": {
        "total_compounds": 24,
        "found": 7,
        "not_found": 17,
        "success_rate": "29.2%"
    },
    "compounds": [...]
}
```

---

## 🔒 安全注意事项

### 公开仓库 vs 私有仓库

| 类型 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **公开** | 免费，易于分享 | 代码公开 | 开源项目 |
| **私有** | 代码私密 | Streamlit Cloud 免费版不支持 | 商业项目 |

**建议：**
- 🔓 **学习/演示** → 使用公开仓库
- 🔒 **商业/敏感数据** → 使用 VPS 部署（不用 Streamlit Cloud）

---

## 📊 数据更新策略

### 方案 A：手动更新（推荐）

```bash
# 1. 本地运行监控
python compound_monitor.py

# 2. 提交结果到 GitHub
git add monitor_output/latest_dashboard.json
git commit -m "Update: 2026-03-11 monitoring results"
git push

# 3. Streamlit Cloud 自动重新部署
```

### 方案 B：GitHub Actions 自动更新

创建 `.github/workflows/daily-update.yml`：

```yaml
name: Daily Compound Monitor

on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨 2 点
  workflow_dispatch:  # 手动触发

jobs:
  update:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run monitor
      run: |
        python compound_monitor.py
    
    - name: Commit and push
      run: |
        git config --global user.name 'GitHub Actions'
        git config --global user.email 'actions@github.com'
        git add monitor_output/
        git commit -m "Auto-update: $(date +%Y-%m-%d)"
        git push
```

---

## 🎯 快速部署命令

```bash
# 1. 切换到 main 分支
cd ~/.openclaw/workspace/drug-price-api
git branch -M main

# 2. 添加所有文件
git add .

# 3. 提交
git commit -m "Deploy to Streamlit Cloud"

# 4. 添加远程仓库（替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/drug-price-monitor.git

# 5. 推送
git push -u origin main

# 6. 访问 https://share.streamlit.io 部署
```

---

## 📱 访问 Dashboard

**部署成功后访问：**
```
https://YOUR_USERNAME-drug-price-monitor-app-XXXXXX.streamlit.app
```

**功能：**
- ✅ 查看 24 个化合物状态
- ✅ 筛选/排序
- ✅ 查看详细信息
- ✅ 导出 CSV/JSON
- ❌ 无法运行 Subagent（需要本地环境）

---

## ⚠️ 限制和注意事项

### Streamlit Cloud 限制

| 限制 | 免费计划 | 付费计划 |
|------|---------|---------|
| **内存** | 1GB | 8GB |
| **CPU** | 共享 | 独占 |
| **存储** | 临时 | 持久 |
| **运行时间** | 休眠 | 24/7 |
| **私有仓库** | ❌ | ✅ |

### 无法使用的功能

- ❌ Subagent 搜索（需要 OpenClaw）
- ❌ 爬虫系统（需要 Playwright）
- ❌ 本地文件写入
- ❌ Cron 定时任务
- ❌ 访问外部 API（部分限制）

### 可以使用的功能

- ✅ 查看 Dashboard
- ✅ 筛选/排序数据
- ✅ 导出 CSV/JSON
- ✅ 查看化合物详情
- ✅ 查看论文信息

---

## 🔄 数据更新流程

```
本地运行监控
    ↓
生成最新数据
    ↓
推送到 GitHub
    ↓
Streamlit Cloud 自动重新部署（约 2 分钟）
    ↓
Dashboard 显示最新数据
```

**更新频率建议：**
- 🔵 **每日更新** - GitHub Actions 自动
- 🟢 **手动更新** - 有重要数据时推送

---

## 🎊 完成检查清单

- [ ] GitHub 仓库已创建
- [ ] 代码已推送
- [ ] Streamlit Cloud 已部署
- [ ] Dashboard 可访问
- [ ] 数据可正常显示
- [ ] 导出功能正常
- [ ] 筛选功能正常

---

## 📞 遇到问题？

### 常见问题

**Q: 部署失败**
```bash
# 检查 requirements.txt
cat requirements.txt

# 检查 Python 版本
python --version

# 查看 Streamlit Cloud 日志
# https://share.streamlit.io → 你的应用 → Settings → Logs
```

**Q: 数据不显示**
```bash
# 确保 dashboard_streamlit.py 能读取数据
# 使用公开的 GitHub raw URL
```

**Q: 页面加载慢**
```python
# 使用 @st.cache_data 装饰器
@st.cache_data
def load_data():
    ...
```

---

## 🚀 下一步

**部署完成后：**

1. ✅ 分享 Dashboard URL 给团队
2. ✅ 设置每日自动更新（GitHub Actions）
3. ✅ 考虑升级到付费计划（如需私有仓库）
4. ✅ 监控使用情况和性能

---

**🎉 准备就绪！开始部署吧！**

需要我帮你创建 GitHub 仓库吗？🚀
