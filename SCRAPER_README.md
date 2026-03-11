# 供应商爬虫系统

基于 Playwright + Stealth 的化学品供应商价格爬虫系统。

## 📦 安装

### 1. 安装 Python 依赖

```bash
cd drug-price-api
pip install -r requirements.txt
```

### 2. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 3. 配置环境变量（可选）

编辑 `.env` 文件：

```env
# 爬虫配置
HEADLESS=true
TIMEOUT_MS=30000
MIN_DELAY_MS=2000
MAX_DELAY_MS=5000

# 代理配置（可选，用于绕过反爬）
PROXY_SERVER=http://proxy-server:port
PROXY_USERNAME=user
PROXY_PASSWORD=pass
```

---

## 🚀 快速开始

### 测试单个供应商

```bash
python test_scraper.py single
```

### 测试所有供应商

```bash
python test_scraper.py all
```

### 获取最优价格

```bash
python test_scraper.py best
```

---

## 📋 支持的供应商

| 供应商 | 状态 | 难度 | 备注 |
|--------|------|------|------|
| **MCE (MedChemExpress)** | ✅ 已实现 | ⭐⭐⭐ | Cloudflare 防护 |
| **TCI Chemicals** | ✅ 已实现 | ⭐⭐⭐ | 基础防护 |
| **Enamine** | ✅ 已实现 | ⭐⭐⭐ | 需要处理 JavaScript |

---

## 💻 代码示例

### 使用爬虫管理器

```python
from scraper.manager import SupplierScraperManager

# 创建管理器
manager = SupplierScraperManager()

try:
    # 搜索化合物
    results = manager.search_sequential("Aspirin")
    
    # 打印结果
    for result in results:
        print(f"供应商：{result['supplier']}")
        print(f"产品：{result['name']}")
        print(f"价格：{result['prices']}")
        
finally:
    manager.cleanup()
```

### 使用单个爬虫

```python
from scraper.mce import MCEScraper

with MCEScraper() as scraper:
    result = scraper.search_compound("Aspirin")
    
    if result:
        print(result)
```

### 并行搜索

```python
from scraper.manager import SupplierScraperManager

manager = SupplierScraperManager()

# 并行搜索所有供应商（更快）
results = manager.search_all("Aspirin", max_workers=3)
```

---

## 🛡️ 反反爬措施

本爬虫系统已实现以下反反爬措施：

### 1. Stealth 模式
```python
# 隐藏 webdriver 特征
stealth_sync(page)

# 注入 JavaScript
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

### 2. User-Agent 随机化
```python
# 每次请求使用不同的 User-Agent
user_agent = get_random_user_agent()
```

### 3. 随机延迟
```python
# 请求间随机延迟 2-5 秒
self.random_delay()
```

### 4. 代理支持
```env
# 在.env 中配置代理
PROXY_SERVER=http://proxy-server:port
PROXY_USERNAME=user
PROXY_PASSWORD=pass
```

---

## ⚠️ 注意事项

### 1. 法律风险
- 请遵守目标网站的 Terms of Service
- 仅用于学术/内部研究
- 不要转售爬取的数据

### 2. 速率限制
- 默认延迟：2-5 秒/请求
- 建议不要高频访问
- 使用代理池降低封禁风险

### 3. 维护成本
- 网站结构变化会导致爬虫失效
- 需要定期更新选择器
- 反爬措施升级需要应对

### 4. 稳定性
- Cloudflare 防护可能偶尔拦截
- 建议实现重试机制
- 准备备选数据源

---

## 🔧 添加新供应商

### 1. 创建爬虫类

```python
# scraper/new_supplier.py
from .base import BaseScraper

class NewSupplierScraper(BaseScraper):
    supplier_name = "New Supplier"
    base_url = "https://example.com"
    
    def search_compound(self, query: str):
        # 实现搜索逻辑
        pass
    
    def parse_price_page(self):
        # 实现解析逻辑
        pass
```

### 2. 注册到管理器

```python
# scraper/manager.py
from .new_supplier import NewSupplierScraper

scraper_classes = {
    "mce": MCEScraper,
    "tci": TCIScraper,
    "enamine": EnamineScraper,
    "new_supplier": NewSupplierScraper,  # 添加新供应商
}
```

---

## 📊 性能对比

| 方式 | 速度 | 成功率 | 成本 |
|------|------|--------|------|
| **ChemPrice API** | 快 | 80% | 免费 |
| **自建爬虫** | 中 | 60-70% | 代理费用 |
| **商业 API** | 快 | 90%+ | $50-200/月 |

---

## 🐛 常见问题

### Q: 爬虫被 Cloudflare 拦截
**A:** 
1. 使用代理
2. 增加延迟
3. 使用商业 API（ScraperAPI）

### Q: 价格信息解析失败
**A:**
1. 网站结构可能已更新
2. 检查选择器是否正确
3. 截图调试：`scraper.take_screenshot()`

### Q: 浏览器启动失败
**A:**
```bash
# 重新安装 Playwright
playwright install chromium --force

# 检查依赖
playwright install-deps chromium
```

---

## 📝 下一步优化

1. **添加更多供应商**
   - Sigma-Aldrich
   - OTAVA
   - ChemDiv

2. **使用商业 API**
   - ScraperAPI
   - ScrapingBee

3. **添加缓存**
   - Redis 缓存查询结果
   - 减少重复请求

4. **监控和告警**
   - 爬虫失败告警
   - 价格变化监控

---

## 📄 许可证

MIT License

---

## 🔗 相关资源

- [Playwright 文档](https://playwright.dev/python/)
- [playwright-stealth](https://github.com/AtuboDad/playwright-stealth)
- [ScraperAPI](https://www.scraperapi.com/)
