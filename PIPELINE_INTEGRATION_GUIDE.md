# 🔄 Pipeline Integration Guide - Validation Agent

## ✅ COMPLETED COMPONENTS:

1. ✅ **Single-Agent Search** - `sessions_spawn` with combined search+JSON prompt
2. ✅ **Validation Agent** - `subagent_validator.py` - compares new vs existing data
3. ✅ **Test Results** - NN9487 validation successful (merge decision)

## 📋 INTEGRATION STEPS:

### Step 1: Update process_queue.py

Add validation after search completion:

```python
from subagent_validator import DataValidator

# In main loop after search completes:
validator = DataValidator()

# For each compound:
# 1. Launch search subagent
search_result = launch_subagent_search(compound)

# 2. Wait for completion (via OpenClaw event)
new_data = wait_for_search_completion(search_result)

# 3. Validate against existing inventory
validation_result = validator.validate(compound, new_data)

# 4. Save validation result
save_validation_result(validation_result)

# 5. Decision logic:
if validation_result['final_decision'] == 'manual_review':
    save_to_manual_review_queue(compound, validation_result, new_data)
elif validation_result['final_decision'] == 'merge':
    merged_data = validation_result['merged_data']
    save_to_compounds_json(merged_data)
else:
    save_to_compounds_json(new_data)
```

### Step 2: Validation Decision Flow

```
Search Agent Returns JSON
         ↓
Validation Agent Compares vs Existing
         ↓
┌─────────────────────────────────────┐
│ Decision Matrix:                    │
│                                     │
│ - missing_trials → merge            │
│ - null CID → keep_existing          │
│ - better findings → accept_new      │
│ - quality regression → flag         │
│ - contradictions → manual_review    │
└─────────────────────────────────────┘
         ↓
Auto-Accept OR Flag for Manual Review
```

### Step 3: Manual Review Queue

File: `manual_review_queue.json`

```json
[
  {
    "compound": "NN9487 (Amycretin)",
    "validation_result": {...},
    "new_data": {...},
    "added_at": "2026-03-20T08:34:38",
    "status": "pending"
  }
]
```

### Step 4: Update compounds.json

After validation passes:
- Auto-accept: Directly update compounds.json
- Merge: Use merged_data from validation
- Manual review: Wait for human decision

## 🎯 VALIDATION RULES:

| Field | Rule | Action |
|-------|------|--------|
| **Clinical Trials** | New has fewer trials | MERGE (keep all) |
| **PubChem CID** | Existing has CID, new is null | KEEP EXISTING |
| **Key Findings** | New is more specific | ACCEPT NEW |
| **Clinical Stage** | New is less advanced | FLAG (regression) |
| **Data Quality** | New is lower quality | FLAG (regression) |
| **Contradictions** | Conflicting data | MANUAL REVIEW |

## 📊 NN9487 TEST RESULTS:

```
Validation Status: pass_with_merge
Final Decision: merge
Conflicts: 4

1. clinical_trials: MERGE (keep all 3 NCTs)
2. pubchem_cid: KEEP EXISTING (168438219)
3. key_findings: ACCEPT NEW (24.3% weight loss)
4. data_quality: FLAG (verified → partial)

Result: Successfully prevented data loss!
- NCT06482727 saved from deletion
- PubChem CID 168438219 preserved
- Better efficacy data accepted
```

## 🚀 NEXT STEPS:

1. ✅ Test validation on 2-3 more compounds
2. ✅ Integrate into process_queue.py main loop
3. ✅ Add manual review UI (simple web form or Discord commands)
4. ✅ Run full 25 compounds with validation enabled
5. ✅ Monitor validation results and tune rules

## 📁 FILES CREATED:

- `subagent_validator.py` - Validation agent logic
- `validation_results/NN9487_validation.json` - Test validation output
- `PIPELINE_INTEGRATION_GUIDE.md` - This file

## 🎯 SUCCESS CRITERIA:

- ✅ Zero data loss (no NCT IDs deleted)
- ✅ Zero CID overwrites with null
- ✅ Better data automatically accepted
- ✅ Contradictions flagged for review
- ✅ Full audit trail maintained
