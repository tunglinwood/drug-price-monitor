# Subagent 搜索模板 - 包含临床试验搜索
# Subagent Search Template - WITH Clinical Trial Search

## 标准搜索任务模板

```python
task = f"""请深度搜索化合物 **{compound_name}** 的完整信息：

**背景信息：**
- 公司：{company}
- 类型：小分子 GLP-1 受体激动剂
- 临床阶段：{stage}
- 适应症：2 型糖尿病、肥胖

**搜索目标：**

1. **化学结构信息**
   - PubChem CID
   - SMILES 字符串
   - InChIKey
   - 分子量
   - 分子式

2. **供应商信息**
   - MCE (MedChemExpress)
   - TCI Chemicals
   - Enamine
   - Sigma-Aldrich
   - 其他供应商

3. **专利信息**
   - 中国/美国/国际专利
   - 专利号、申请日期

4. **研究论文**
   - PubMed 论文
   - 期刊名称、PMID、DOI

5. **🏥 临床试验信息** (重要！)
   - ClinicalTrials.gov 登记号 (NCT 编号)
   - 中国药物临床试验登记号
   - 试验阶段、状态、适应症
   - 受试者人数
   - 试验结果（如有）

6. **公司信息**
   - 公司官网研发管线
   - 投资者关系公告

**返回格式**（严格 JSON）：
```json
{{
  "compound": "{compound_name}",
  "company": "{company}",
  "pubchem": {{"cid": ..., "smiles": "...", ...}},
  "suppliers": [...],
  "patents": [...],
  "papers": [...],
  "clinical_trials": [
    {{
      "registry": "ClinicalTrials.gov",
      "trial_id": "NCT 编号",
      "phase": "试验阶段",
      "status": "招募中/已完成/终止",
      "indication": "适应症",
      "enrollment": 受试者人数，
      "url": "直接链接"
    }}
  ],
  "status": "found|partial|not_found",
  "notes": "..."
}}
```

**注意：**
- 必须搜索临床试验数据库
- 找到具体 NCT 编号，不是搜索链接
- 中国化合物同时搜索中英文数据库
"""
```

---

## 📋 **已搜索化合物的临床试验状态**

| 化合物 | 临床试验信息 | 状态 |
|--------|-------------|------|
| **NN9487** | ✅ NCT05369390, NCT06064006 | 已找到 |
| **BGM0504** | ✅ 2 项试验 | 已找到 |
| **HRS-7535** | ✅ 1 项试验 | 已找到 |
| **PF-06882961** | ✅ NCT05041896 (终止) | 已找到 |
| **其他 12 个** | ❌ 需要重新搜索 | 待搜索 |

---

## 🚀 **下一步行动**

**Option A: Re-search 12 compounds with clinical trials INCLUDED**
- Launch individual subagent for each
- Clinical trial search is PART of standard search
- Takes 10 min per compound
- Higher success rate

**Option B: Continue with remaining compounds**
- Keep current workflow
- Accept that some trial data may be missing
- Faster completion

**Option C: Manual curation**
- You provide trial IDs from your access
- I format and add to dashboard
- Most accurate

---

**Which do you prefer?** 🔬

**My recommendation:** **Option A** - Re-search with clinical trials included in each subagent search. This ensures comprehensive data!
