# 🔄 SEARCH + EXTRACTION + VALIDATION WORKFLOW

## 📋 NEW ARCHITECTURE (3-STEP PIPELINE)

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: SEARCH AGENT                                        │
│ Input: Compound name                                        │
│ Task: Comprehensive web search                              │
│ Output: Raw search results (text file)                      │
│ Runtime: ~3-5 min                                          │
│ File: search_results/{compound}_raw.txt                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: EXTRACTION AGENT                                    │
│ Input: Raw search text file                                 │
│ Task: Read text, extract structured JSON                    │
│ Output: Structured JSON                                     │
│ Runtime: ~30-60s                                           │
│ File: extracted_json/{compound}_extracted.json             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: VALIDATION AGENT                                    │
│ Input: Extracted JSON + Existing inventory                  │
│ Task: Compare new vs existing, detect gaps                  │
│ Output: Validation decision + merged data                   │
│ Runtime: ~5-10s                                            │
│ File: validation_results/{compound}_validation.json        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: DECISION                                            │
│ - pass → use_new                                            │
│ - pass_with_merge → merged_data                             │
│ - manual_review → flag for human review                     │
│ - use_existing → keep old data                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 FILE STRUCTURE

```
drug-price-api/
├── search_results/
│   ├── NN9487_Amycretin_20260320_092000_raw.txt
│   ├── SAL0112_20260320_093000_raw.txt
│   └── ...
├── extracted_json/
│   ├── NN9487_Amycretin_20260320_092500_extracted.json
│   ├── NN9487_Amycretin_20260320_092500_extraction_prompt.txt
│   └── ...
├── validation_results/
│   ├── NN9487_Amycretin_validation.json
│   └── ...
├── manual_review_queue.json
├── compounds.json (inventory)
├── single_agent_search.py (Step 1)
├── extraction_agent.py (Step 2)
└── subagent_validator.py (Step 3)
```

---

## 🔍 WHY SEPARATE SEARCH FROM EXTRACTION?

### OLD APPROACH (Single Agent):
```
Search Agent → Returns JSON ❌

Problems:
- Search distracted by JSON formatting
- Can't re-extract without re-searching
- Raw data lost
- Hard to debug extraction errors
```

### NEW APPROACH (3-Step):
```
Search → Raw Text → Extraction → JSON → Validation → Decision ✅

Benefits:
- Search focuses on finding data
- Raw data preserved for audit
- Can re-extract multiple times
- Extraction can be retried without re-searching
- Validation compares structured data
- Full audit trail
```

---

## 📊 EXAMPLE: NN9487 WORKFLOW

### Step 1: Search Agent
```
Input: "NN9487 (Amycretin), Novo Nordisk"
Task: Search web comprehensively
Output: search_results/NN9487_Amycretin_raw.txt

Content:
=== CHEMICAL IDENTIFIERS ===
PubChem CID: Not found in search
Notes: Proprietary peptide

=== CLINICAL TRIALS ===
Trial 1: NCT05369390
Phase: Phase 1
Status: Completed
URL: https://clinicaltrials.gov/study/NCT05369390

Trial 2: NCT06064006
Phase: Phase 1b/2a
Status: Active
URL: https://clinicaltrials.gov/study/NCT06064006

=== KEY FINDINGS ===
- 24.3% weight loss at 60mg (week 36)
- Published in Lancet, July 2025
```

### Step 2: Extraction Agent
```
Input: search_results/NN9487_Amycretin_raw.txt
Task: Extract structured JSON
Output: extracted_json/NN9487_extracted.json

Content:
{
  "compound": "NN9487 (Amycretin)",
  "clinical_trials": [
    {"trial_id": "NCT05369390", ...},
    {"trial_id": "NCT06064006", ...}
  ],
  "key_findings": "24.3% weight loss at 60mg...",
  ...
}
```

### Step 3: Validation Agent
```
Input: 
- extracted_json/NN9487_extracted.json (new)
- compounds.json (existing)

Comparison:
- New: 2 trials, Existing: 3 trials → MERGE
- New: null CID, Existing: 168438219 → KEEP EXISTING
- New: 24.3%, Existing: 13.1% → ACCEPT NEW

Output: validation_results/NN9487_validation.json

Decision: merge
Merged data: All 3 trials + CID 168438219 + 24.3% weight loss
```

---

## 🎯 VALIDATION DECISION MATRIX

| Scenario | Existing | New | Decision | Action |
|----------|----------|-----|----------|--------|
| **Missing trials** | 3 NCTs | 2 NCTs | merge | Keep all 3 trials |
| **Missing CID** | 168438219 | null | keep_existing | Retain existing CID |
| **Better findings** | "13.1%" | "24.3% at 60mg" | accept_new | Use new data |
| **Quality drop** | verified | partial | flag | Flag for review |
| **Contradiction** | "Triple agonist" | "Dual agonist" | manual_review | Human review |

---

## 🛠️ IMPLEMENTATION FILES

| File | Purpose | Lines |
|------|---------|-------|
| `single_agent_search.py` | Search agent (raw text output) | ~120 |
| `extraction_agent.py` | Extract JSON from raw text | ~140 |
| `subagent_validator.py` | Validate new vs existing | ~350 |
| `WORKFLOW_ARCHITECTURE.md` | This document | - |

---

## 🚀 USAGE EXAMPLE

```python
# Step 1: Search
from single_agent_search import create_search_prompt, save_raw_search_results

prompt = create_search_prompt("NN9487 (Amycretin)", "Novo Nordisk")
search_result = sessions_spawn(task=prompt, label="search-NN9487")
# Wait for completion...
save_raw_search_results("NN9487 (Amycretin)", search_result)

# Step 2: Extraction
from extraction_agent import extract_from_raw

prompt_file = extract_from_raw(
    "search_results/NN9487_Amycretin_raw.txt",
    "NN9487 (Amycretin)"
)
extraction_result = sessions_spawn(task=prompt_file, label="extract-NN9487")
# Wait for completion (60s timeout)...

# Step 3: Validation
from subagent_validator import DataValidator

validator = DataValidator()
validation_result = validator.validate(
    "NN9487 (Amycretin)",
    extraction_result
)

# Step 4: Decision
if validation_result['final_decision'] == 'merge':
    update_compounds_json(validation_result['merged_data'])
elif validation_result['final_decision'] == 'manual_review':
    save_to_manual_review_queue(validation_result)
```

---

## ✅ BENEFITS

| Benefit | Impact |
|---------|--------|
| **Raw data preserved** | Can re-extract anytime |
| **Separation of concerns** | Each agent does one thing well |
| **Retry extraction** | Without re-searching (saves time!) |
| **Audit trail** | Full search history saved |
| **Validation prevents loss** | Never overwrite good data |
| **Debuggable** | Can inspect each step |

---

## 🎯 NEXT STEPS

1. ✅ Search agent returns raw text
2. ✅ Extraction agent reads text, extracts JSON
3. ✅ Validation agent compares JSON vs existing
4. ⏳ Integrate into process_queue.py
5. ⏳ Add retry logic for failed extraction
6. ⏳ Add feedback loop (re-search missing fields)
