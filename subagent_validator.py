"""
数据验证代理 - 比较新搜索数据与现有库存数据
Data Validation Agent - Compare newly searched data against existing inventory

工作流程：
1. 搜索代理 → 保存原始搜索结果到文本文件
2. 提取代理 → 从原始文本提取结构化 JSON
3. 验证代理 → 比较提取的 JSON vs 现有库存
"""

import json
from datetime import datetime
from pathlib import Path


class DataValidator:
    """验证新搜索数据的质量并防止数据丢失"""

    def __init__(self, inventory_path: str = "compounds.json"):
        self.inventory_path = Path(inventory_path)
        self.inventory_data = self._load_inventory()

    def _load_inventory(self) -> dict:
        """加载现有库存数据"""
        if not self.inventory_path.exists():
            return {"compounds": []}

        with open(self.inventory_path, encoding="utf-8") as f:
            return json.load(f)

    def _find_existing_compound(self, compound_name: str) -> dict | None:
        """在库存中查找现有化合物数据"""
        compounds = self.inventory_data.get("compounds", [])
        for comp in compounds:
            if compound_name.lower() in comp.get("chem_name", "").lower():
                return comp
        return None

    def _compare_clinical_trials(self, existing: list, new: list) -> dict:
        """比较临床试验数据"""
        existing_ids = {t.get("trial_id") for t in existing if t.get("trial_id")}
        new_ids = {t.get("trial_id") for t in new if t.get("trial_id")}

        missing_in_new = existing_ids - new_ids
        added_in_new = new_ids - existing_ids

        if len(missing_in_new) > 0:
            return {
                "field": "clinical_trials",
                "existing_value": f"{len(existing)} NCT IDs",
                "new_value": f"{len(new)} NCT IDs",
                "recommendation": "merge",
                "reason": f"New data missing {len(missing_in_new)} trial(s): {', '.join(missing_in_new)} - merge to prevent data loss",
                "missing_trials": list(missing_in_new),
                "added_trials": list(added_in_new),
            }
        elif len(added_in_new) > 0:
            return {
                "field": "clinical_trials",
                "existing_value": f"{len(existing)} NCT IDs",
                "new_value": f"{len(new)} NCT IDs",
                "recommendation": "accept_new",
                "reason": f"New data has {len(added_in_new)} additional trial(s)",
                "added_trials": list(added_in_new),
            }
        else:
            return {
                "field": "clinical_trials",
                "existing_value": f"{len(existing)} NCT IDs",
                "new_value": f"{len(new)} NCT IDs",
                "recommendation": "accept_new",
                "reason": "Same trials found",
            }

    def _compare_chemical_identifiers(self, existing: dict, new: dict) -> list:
        """比较化学标识符"""
        conflicts = []

        # Check PubChem CID
        existing_cid = existing.get("pubchem_cid")
        new_cid = new.get("pubchem_cid")

        if existing_cid and not new_cid:
            conflicts.append(
                {
                    "field": "chemical_identifiers.pubchem_cid",
                    "existing_value": existing_cid,
                    "new_value": None,
                    "recommendation": "keep_existing",
                    "reason": "Don't overwrite verified CID with null",
                }
            )
        elif new_cid and not existing_cid:
            conflicts.append(
                {
                    "field": "chemical_identifiers.pubchem_cid",
                    "existing_value": None,
                    "new_value": new_cid,
                    "recommendation": "accept_new",
                    "reason": "New data has CID",
                }
            )
        elif existing_cid and new_cid and existing_cid != new_cid:
            conflicts.append(
                {
                    "field": "chemical_identifiers.pubchem_cid",
                    "existing_value": existing_cid,
                    "new_value": new_cid,
                    "recommendation": "manual_review",
                    "reason": "CONFLICT: Different CID values - requires verification",
                }
            )

        return conflicts

    def _compare_key_findings(self, existing: str, new: str) -> dict:
        """比较关键发现"""
        # Simple heuristic: longer and more specific is usually better
        existing_len = len(existing) if existing else 0
        new_len = len(new) if new else 0

        if new_len > existing_len * 1.5:  # New is 50% longer
            return {
                "field": "key_findings",
                "existing_value": existing[:50] + "..."
                if existing_len > 50
                else existing,
                "new_value": new[:50] + "..." if new_len > 50 else new,
                "recommendation": "accept_new",
                "reason": "New data is more detailed and specific",
            }
        elif existing_len > new_len * 1.5:  # Existing is 50% longer
            return {
                "field": "key_findings",
                "existing_value": existing[:50] + "..."
                if existing_len > 50
                else existing,
                "new_value": new[:50] + "..." if new_len > 50 else new,
                "recommendation": "keep_existing",
                "reason": "Existing data is more detailed",
            }
        else:
            return {
                "field": "key_findings",
                "existing_value": existing[:50] + "..."
                if existing_len > 50
                else existing,
                "new_value": new[:50] + "..." if new_len > 50 else new,
                "recommendation": "accept_new",
                "reason": "Similar detail level, prefer newer data",
            }

    def _compare_data_quality(self, existing: str, new: str) -> dict:
        """比较数据质量等级"""
        quality_rank = {
            "verified": 3,
            "partial": 2,
            "pending_verification": 1,
            "pending": 1,
        }

        existing_rank = quality_rank.get(existing, 0)
        new_rank = quality_rank.get(new, 0)

        if new_rank < existing_rank:
            return {
                "field": "data_quality",
                "existing_value": existing,
                "new_value": new,
                "recommendation": "flag",
                "reason": f"Quality regression: {existing} → {new}",
            }
        elif new_rank > existing_rank:
            return {
                "field": "data_quality",
                "existing_value": existing,
                "new_value": new,
                "recommendation": "accept_new",
                "reason": f"Quality improvement: {existing} → {new}",
            }
        else:
            return {
                "field": "data_quality",
                "existing_value": existing,
                "new_value": new,
                "recommendation": "accept_new",
                "reason": "Same quality level",
            }

    def validate(self, compound_name: str, new_data: dict) -> dict:
        """
        验证新搜索数据

        Args:
            compound_name: 化合物名称
            new_data: 新搜索的数据（结构化 JSON）

        Returns:
            验证结果字典
        """
        existing = self._find_existing_compound(compound_name)

        if not existing:
            # No existing data - accept new data
            return {
                "compound": compound_name,
                "validation_status": "pass",
                "conflicts": [],
                "final_decision": "use_new",
                "notes": "No existing data - accepting new data",
                "validation_timestamp": datetime.now().isoformat(),
            }

        # Compare fields
        conflicts = []

        # 1. Clinical trials
        existing_trials = existing.get("clinical_trials", [])
        new_trials = new_data.get("clinical_trials", [])
        if existing_trials or new_trials:
            conflicts.append(self._compare_clinical_trials(existing_trials, new_trials))

        # 2. Chemical identifiers
        existing_chem = existing.get("chemical_identifiers", {})
        new_chem = new_data.get("chemical_identifiers", {})
        conflicts.extend(self._compare_chemical_identifiers(existing_chem, new_chem))

        # 3. Key findings
        existing_findings = existing.get("key_findings", "")
        new_findings = new_data.get("key_findings", "")
        if existing_findings or new_findings:
            conflicts.append(
                self._compare_key_findings(existing_findings, new_findings)
            )

        # 4. Data quality
        existing_quality = existing.get("data_quality", "pending")
        new_quality = new_data.get("data_quality", "pending")
        conflicts.append(self._compare_data_quality(existing_quality, new_quality))

        # Determine overall status
        recommendations = [c.get("recommendation") for c in conflicts]

        if "manual_review" in recommendations:
            validation_status = "manual_review"
            final_decision = "manual_review"
        elif "keep_existing" in recommendations and "accept_new" not in recommendations:
            validation_status = "pass"
            final_decision = "use_existing"
        elif "merge" in recommendations:
            validation_status = "pass_with_merge"
            final_decision = "merge"
        else:
            validation_status = "pass"
            final_decision = "use_new"

        # Create merged data if needed
        merged_data = None
        if final_decision == "merge":
            merged_data = existing.copy()
            # Merge clinical trials
            if any(c["field"] == "clinical_trials" for c in conflicts):
                trial_conflict = next(
                    c for c in conflicts if c["field"] == "clinical_trials"
                )
                if trial_conflict.get("missing_trials"):
                    # Keep existing trials (they have more)
                    merged_data["clinical_trials"] = existing_trials

            # Keep existing CID if new is null
            if any(
                c["field"] == "chemical_identifiers.pubchem_cid"
                and c["recommendation"] == "keep_existing"
                for c in conflicts
            ):
                merged_data["chemical_identifiers"] = existing_chem

            # Accept new key findings if better
            if any(
                c["field"] == "key_findings" and c["recommendation"] == "accept_new"
                for c in conflicts
            ):
                merged_data["key_findings"] = new_findings

        return {
            "compound": compound_name,
            "validation_status": validation_status,
            "conflicts": conflicts,
            "final_decision": final_decision,
            "merged_data": merged_data,
            "notes": f"Validation completed with {len(conflicts)} field comparison(s)",
            "validation_timestamp": datetime.now().isoformat(),
        }


def validate_nn9487_test():
    """Test validation with NN9487 data"""
    validator = DataValidator()

    # New data from single-agent search
    new_data = {
        "compound": "NN9487 (Amycretin)",
        "company": "Novo Nordisk A/S (诺和诺德)",
        "stage": "Phase 1b/2a",
        "chemical_identifiers": {
            "pubchem_cid": None,
            "smiles": None,
            "inchikey": None,
            "iupac": None,
            "molecular_weight": None,
            "notes": "Proprietary unimolecular GLP-1 and amylin receptor agonist peptide",
        },
        "clinical_trials": [
            {
                "registry": "ClinicalTrials.gov",
                "trial_id": "NCT06064006",
                "phase": "Phase 1b/2a",
                "status": "Active/Completed",
                "url": "https://clinicaltrials.gov/study/NCT06064006",
            },
            {
                "registry": "ClinicalTrials.gov",
                "trial_id": "NCT05369390",
                "phase": "Phase 1",
                "status": "Completed",
                "url": "https://clinicaltrials.gov/study/NCT05369390",
            },
        ],
        "patents": [],
        "pubmed_papers": [
            {
                "pmid": "40550231",
                "title": "Amycretin, a novel, unimolecular GLP-1 and amylin receptor agonist...",
                "year": "2025",
            },
            {
                "pmid": "40550229",
                "title": "Safety, tolerability, pharmacokinetics, and pharmacodynamics...",
                "year": "2025",
            },
            {
                "pmid": "40706446",
                "title": "The effect of amycretin... on body weight...",
                "year": "2025",
            },
            {
                "pmid": "41054801",
                "title": "Novel GLP-1-based Medications...",
                "year": "2026",
            },
            {
                "pmid": "41850421",
                "title": "Amycretin in obesity: Mechanisms, clinical efficacy...",
                "year": "2026",
            },
        ],
        "suppliers": [
            {"name": "MCE", "available": False},
            {"name": "TCI", "available": False},
            {"name": "Enamine", "available": False},
            {"name": "Sigma-Aldrich", "available": False},
        ],
        "key_findings": "NN9487 (Amycretin) is a novel unimolecular GLP-1 and amylin receptor agonist. Phase 1b/2a trials showed dose-dependent weight loss: 24.3% at 60mg (week 36), 22.0% at 20mg (week 36), 16.2% at 5mg (week 28), 9.7% at 1.25mg (week 20). Published in Lancet (July 2025).",
        "data_quality": "partial",
        "notes": "Chemical structure not publicly available. Clinical trial data verified from ClinicalTrials.gov and Lancet publications.",
    }

    # Run validation
    result = validator.validate("NN9487 (Amycretin)", new_data)

    # Save validation result
    output_path = Path("validation_results/NN9487_validation.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print("✅ NN9487 VALIDATION COMPLETE")
    print("=" * 70)
    print(f"\n📊 Validation Status: {result['validation_status']}")
    print(f"🎯 Final Decision: {result['final_decision']}")
    print(f"📋 Conflicts Found: {len(result['conflicts'])}")
    print(f"\n💾 Saved to: {output_path}")

    if result["conflicts"]:
        print("\n" + "=" * 70)
        print("🔍 CONFLICTS:")
        print("=" * 70)
        for i, conflict in enumerate(result["conflicts"], 1):
            print(f"\n{i}. Field: {conflict['field']}")
            print(f"   Existing: {conflict['existing_value']}")
            print(f"   New: {conflict['new_value']}")
            print(f"   Recommendation: {conflict['recommendation']}")
            print(f"   Reason: {conflict['reason']}")

    return result


if __name__ == "__main__":
    validate_nn9487_test()
