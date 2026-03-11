# Drug Price API - 化合物自动询价服务

基于 [ChemPrice](https://chemprice.readthedocs.io/) 的化合物价格查询 API，整合 **Molport**, **ChemSpace**, **MCule** 三大平台，覆盖 **100+ 化学品供应商**。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd drug-price-api
pip install -r requirements.txt
```

### 2. 配置 API Keys

复制环境变量模板并填入你的 API keys：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Molport (二选一)
MOLPORT_API_KEY=your-molport-api-key
# 或
MOLPORT_USERNAME=your-username
MOLPORT_PASSWORD=your-password

# ChemSpace
CHEMSPACE_API_KEY=your-chemspace-api-key

# MCule
MCULE_API_KEY=your-mcule-api-key
```

**申请链接：**
- Molport: https://www.molport.com/shop/user-api-keys
- ChemSpace: https://chem-space.com/contacts
- MCule: https://mcule.com/contact/

### 3. 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python
python -m app.main
```

访问 http://localhost:8000/docs 查看 API 文档

---

## 📡 API Endpoints

### 1. 查询化合物价格

**POST /api/v1/price**

```bash
curl -X POST "http://localhost:8000/api/v1/price" \
  -H "Content-Type: application/json" \
  -d '{"compound": "Aspirin"}'
```

**GET /api/v1/price/{compound}**

```bash
curl "http://localhost:8000/api/v1/price/Aspirin"
```

**响应示例：**

```json
{
  "compound": "Aspirin",
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "name": "2-acetyloxybenzoic acid",
  "molecular_weight": 180.16,
  "formula": "C9H8O4",
  "prices": [
    {
      "smiles": "CC(=O)Oc1ccccc1C(=O)O",
      "source": "Molport",
      "supplier": "ChemDiv, Inc.",
      "purity": ">95%",
      "amount": 100,
      "measure": "mg",
      "price_usd": 25.50,
      "currency": "USD"
    }
  ],
  "best_price": {
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "source": "Molport",
    "supplier": "ChemDiv, Inc.",
    "purity": ">95%",
    "amount": 100,
    "measure": "mg",
    "price_usd": 25.50,
    "currency": "USD"
  },
  "total_results": 15,
  "query_time_ms": 1250.5
}
```

### 2. 查询化合物信息

**GET /api/v1/compound/{query}**

```bash
curl "http://localhost:8000/api/v1/compound/Paracetamol"
```

### 3. 名称转 SMILES

**GET /api/v1/smiles/{compound_name}**

```bash
curl "http://localhost:8000/api/v1/smiles/Caffeine"
```

### 4. 健康检查

**GET /health**

```bash
curl "http://localhost:8000/health"
```

---

## 🛠️ 技术栈

- **FastAPI** - 高性能 API 框架
- **ChemPrice** - 化学品价格聚合库
- **PubChemPy** - PubChem API 客户端（化合物名称→SMILES）
- **Pydantic** - 数据验证

---

## 📝 支持的化合物输入格式

1. **常见名称**: `Aspirin`, `Paracetamol`, `Caffeine`
2. **IUPAC 名称**: `2-acetyloxybenzoic acid`
3. **SMILES**: `CC(=O)Oc1ccccc1C(=O)O`
4. **CAS 号**: 部分支持（通过 PubChem）

---

## 🔒 注意事项

1. **API Keys**: 三个平台的 API key 都是**免费**的，但需要注册申请
2. **速率限制**: 各平台可能有查询频率限制，建议添加缓存
3. **价格准确性**: 价格来自供应商，可能有延迟，实际价格以供应商网站为准
4. **生产部署**: 建议使用 Docker 部署，配置合适的超时和重试策略

---

## 🚧 后续优化建议

1. **添加缓存** - Redis 缓存查询结果
2. **批量查询** - 支持一次查询多个化合物
3. **价格历史** - 记录价格变化趋势
4. **更多供应商** - 直接集成 MCE、Sigma 等
5. **货币转换** - 支持多货币显示
6. **库存状态** - 实时库存检查

---

## 📄 许可证

MIT License

---

## 🔗 相关资源

- [ChemPrice 文档](https://chemprice.readthedocs.io/)
- [PubChem](https://pubchem.ncbi.nlm.nih.gov/)
- [Molport](https://www.molport.com/)
- [ChemSpace](https://chem-space.com/)
- [MCule](https://mcule.com/)
