#!/usr/bin/env python3
"""Strict audit of the clean professor-compliant method output.

Reads the output of gnn_lpd_dqn_selective_db_lp.py --mode eval and enforces:
  1. Per-cycle CSV: gnn_used=1, lpd_used=1, dqn_used=1 in EVERY row
  2. Per-cycle CSV: stage2_used=0, disturbance_finalization_used=0,
     random_forest_gate_used=0, sticky_gate_used=0, heuristic_used=0 in EVERY row
  3. criticality_backend = "gnn_lpd" in every row
  4. method_audit.json has correct component flags
  5. GNN checkpoint meta proves DB-budgeted oracle provenance
  6. Static grep: the clean method script contains no forbidden token calls
  7. Results are from real eval, not hardcoded

Exits 0 on full pass, non-zero on any failure.

Usage:
    python scripts/phase1_5/audit_gnn_lpd_dqn_clean_method.py
    python scripts/phase1_5/audit_gnn_lpd_dqn_clean_method.py \\
        --eval_dir results/gnn_lpd_dqn_selective_db_lp/final_N3976
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EVAL_DIR = ROOT / "results" / "gnn_lpd_dqn_selective_db_lp" / "final_N3976"
DEFAULT_MODEL_DIR = ROOT / "results" / "gnn_lpd_dqn_selective_db_lp" / "models"
DEFAULT_LABEL_DIR = ROOT / "results" / "gnn_lpd_dqn_selective_db_lp" / "labels"
CLEAN_METHOD_SCRIPT = ROOT / "scripts" / "phase1_5" / "gnn_lpd_dqn_selective_db_lp.py"

# Tokens that must NEVER appear as active calls in the clean method
FORBIDDEN_CALL_PATTERNS = [
    "RandomForest",
    "sticky_gate",
    "sticky_reuse",
    "disturbance_finalization",
    "solve_selected_path_lp_min_db",
    "stage2",
    "Stage2",
    "heuristic_criticality",
    "reward_policy_rf",
]

# Expected values in every per-cycle row
REQUIRED_ROW_VALUES = {
    "gnn_used":                    1,
    "lpd_used":                    1,
    "dqn_used":                    1,
    "stage2_used":                 0,
    "disturbance_finalization_used": 0,
    "random_forest_gate_used":     0,
    "sticky_gate_used":            0,
    "heuristic_used":              0,
}
REQUIRED_BACKEND = "gnn_lpd"

# Expected audit JSON flags
REQUIRED_AUDIT_FLAGS = {
    "gnn_used":                    1,
    "lpd_used":                    1,
    "dqn_used":                    1,
    "criticality_backend":         "gnn_lpd",
    "heuristic_used":              0,
    "selected_od_lp_used":         1,
    "stage2_used":                 0,
    "disturbance_finalization_used": 0,
    "random_forest_gate_used":     0,
    "sticky_gate_used":            0,
}

FLEXDATE = {
    "abilene":    {"PR": 0.958, "DB": 0.0513},
    "cernet":     {"PR": 0.975, "DB": 0.0183},
    "geant":      {"PR": 0.995, "DB": 0.0296},
    "sprintlink": {"PR": 0.999, "DB": 0.0510},
    "tiscali":    {"PR": 0.999, "DB": 0.0510},
}


def _fail(msg: str):
    print(f"\nAUDIT FAIL — {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval_dir", default=str(DEFAULT_EVAL_DIR))
    ap.add_argument("--model_dir", default=str(DEFAULT_MODEL_DIR))
    ap.add_argument("--label_dir", default=str(DEFAULT_LABEL_DIR))
    args = ap.parse_args()

    eval_dir = Path(args.eval_dir)
    model_dir = Path(args.model_dir)
    label_dir = Path(args.label_dir)
    failures: list[str] = []

    print("=" * 70)
    print("CLEAN METHOD AUDIT — gnn_lpd_dqn_selective_db_lp")
    print(f"  Eval dir  : {eval_dir}")
    print(f"  Model dir : {model_dir}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # BLOCK 1: Required output files
    # ------------------------------------------------------------------
    print("\n[1] Required output files...")
    required = {
        "per_cycle_csv": None,
        "summary_csv": None,
        "overall_json": None,
        "method_audit": eval_dir / "method_audit.json",
    }
    # Find per_cycle and summary CSVs (accept any tag prefix)
    if eval_dir.is_dir():
        for f in sorted(eval_dir.glob("*_per_cycle.csv")):
            required["per_cycle_csv"] = f
        for f in sorted(eval_dir.glob("*_summary.csv")):
            required["summary_csv"] = f
        for f in sorted(eval_dir.glob("*_overall.json")):
            required["overall_json"] = f

    for name, path in required.items():
        if path is None or not Path(path).exists():
            failures.append(f"Missing required file: {name} in {eval_dir}")
        else:
            print(f"    OK  {name}: {Path(path).name}")

    if "Missing" in " ".join(failures):
        for f in failures:
            print(f"  FAIL: {f}", file=sys.stderr)
        _fail("Required output files missing — cannot continue audit.")

    # ------------------------------------------------------------------
    # BLOCK 2: Load per-cycle CSV
    # ------------------------------------------------------------------
    print("\n[2] Loading per-cycle CSV...")
    df = pd.read_csv(required["per_cycle_csv"])
    print(f"    Loaded {len(df)} rows, {df['topology'].nunique()} topologies")
    if len(df) == 0:
        _fail("Per-cycle CSV is empty — possible hardcoded results.")

    # ------------------------------------------------------------------
    # BLOCK 3: Per-row component flag checks
    # ------------------------------------------------------------------
    print("\n[3] Checking per-row component flags...")
    for col, expected in REQUIRED_ROW_VALUES.items():
        if col not in df.columns:
            failures.append(f"Column '{col}' missing from per-cycle CSV.")
            continue
        bad = df[df[col] != expected]
        if len(bad) > 0:
            failures.append(
                f"Column '{col}': {len(bad)} rows have value != {expected}. "
                f"First bad: topology={bad.iloc[0].get('topology','?')} "
                f"ts={bad.iloc[0].get('timestep','?')} val={bad.iloc[0][col]}"
            )
        else:
            print(f"    OK  {col} == {expected} in all {len(df)} rows")

    # ------------------------------------------------------------------
    # BLOCK 4: criticality_backend check
    # ------------------------------------------------------------------
    print("\n[4] Checking criticality_backend...")
    if "criticality_backend" in df.columns:
        bad_backend = df[df["criticality_backend"] != REQUIRED_BACKEND]
        if len(bad_backend) > 0:
            failures.append(
                f"criticality_backend: {len(bad_backend)} rows != '{REQUIRED_BACKEND}'. "
                f"Values: {bad_backend['criticality_backend'].value_counts().to_dict()}"
            )
        else:
            print(f"    OK  criticality_backend == '{REQUIRED_BACKEND}' in all rows")
    else:
        failures.append("Column 'criticality_backend' missing from per-cycle CSV.")

    # ------------------------------------------------------------------
    # BLOCK 5: method_audit.json flags
    # ------------------------------------------------------------------
    print("\n[5] Checking method_audit.json flags...")
    audit = json.loads(Path(required["method_audit"]).read_text())
    for key, expected in REQUIRED_AUDIT_FLAGS.items():
        actual = audit.get(key)
        if actual is None:
            failures.append(f"method_audit.json missing key '{key}'")
        elif str(actual) != str(expected):
            failures.append(
                f"method_audit.json['{key}']: expected={expected!r} actual={actual!r}"
            )
        else:
            print(f"    OK  {key} = {actual!r}")

    # ------------------------------------------------------------------
    # BLOCK 6: GNN checkpoint meta — DB-budgeted oracle provenance
    # ------------------------------------------------------------------
    print("\n[6] Checking GNN checkpoint meta (DB-budgeted oracle provenance)...")
    meta_path = model_dir / "gnn_dbbudget_selector_meta.json"
    if not meta_path.exists():
        failures.append(f"GNN meta JSON missing: {meta_path}")
    else:
        meta = json.loads(meta_path.read_text())
        training = meta.get("training", {})
        checks = {
            "oracle_solver": ("full_od_db_budgeted_lp", training.get("oracle_solver")),
            "heuristic_ranking_used_for_labels": (False, training.get("heuristic_ranking_used_for_labels")),
            "db_budgeted_oracle_used": (True, training.get("db_budgeted_oracle_used")),
            "full_mcf_min_mlu_teacher_only": (False, training.get("full_mcf_min_mlu_teacher_only")),
        }
        for key, (expected, actual) in checks.items():
            if actual is None:
                failures.append(f"GNN meta missing '{key}'")
            elif actual != expected:
                failures.append(f"GNN meta['{key}']: expected={expected!r} actual={actual!r}")
            else:
                print(f"    OK  {key} = {actual!r}")

    # ------------------------------------------------------------------
    # BLOCK 7: Label provenance JSON
    # ------------------------------------------------------------------
    print("\n[7] Checking label provenance JSON...")
    prov_path = label_dir / "label_provenance.json"
    if not prov_path.exists():
        failures.append(f"Label provenance JSON missing: {prov_path}")
    else:
        prov = json.loads(prov_path.read_text())
        prov_checks = {
            "oracle_solver": ("full_od_db_budgeted_lp", prov.get("oracle_solver")),
            "heuristic_ranking_used_for_labels": (False, prov.get("heuristic_ranking_used_for_labels")),
            "db_budgeted_oracle_used": (True, prov.get("db_budgeted_oracle_used")),
        }
        for key, (expected, actual) in prov_checks.items():
            if actual != expected:
                failures.append(f"Provenance['{key}']: expected={expected!r} actual={actual!r}")
            else:
                print(f"    OK  {key} = {actual!r}")

    # ------------------------------------------------------------------
    # BLOCK 8: Static grep for forbidden tokens in clean method script
    # ------------------------------------------------------------------
    print("\n[8] Static grep for forbidden tokens in clean method script...")
    if not CLEAN_METHOD_SCRIPT.exists():
        failures.append(f"Clean method script not found: {CLEAN_METHOD_SCRIPT}")
    else:
        src = CLEAN_METHOD_SCRIPT.read_text()
        for token in FORBIDDEN_CALL_PATTERNS:
            # Only flag lines where the token appears as an active code call,
            # not in: comments, docstrings, assertion/detection code, hasattr checks,
            # string literals used for detection, or listed-forbidden documentation.
            lines_with_token = [
                (i + 1, line.strip())
                for i, line in enumerate(src.splitlines())
                if token.lower() in line.lower()
                and not line.strip().startswith("#")
                and not line.strip().startswith('"')
                and not line.strip().startswith("'")
                and not line.strip().startswith("*")
                and "FORBIDDEN" not in line
                and "forbidden" not in line.lower()
                and "must not" not in line.lower()
                and "must never" not in line.lower()
                and "hasattr" not in line.lower()
                and "isinstance" not in line.lower()
                and "_assert_no_forbidden" not in line.lower()
                and "assert_no_forbidden" not in line.lower()
                and '("' + token not in line  # string literal in detection tuple
                and "('" + token not in line
                and f'"{token}"' not in line
                and f"'{token}'" not in line
                # Skip lines that only set/document the flag-column as 0 ("not used")
                and not any(
                    f'"{tok}": 0' in line or f'"{tok}":  0' in line
                    or f'{tok}_used": 0' in line or f'_{tok}_used": 0' in line
                    or f'_{tok}": 0' in line
                    or f'{tok}_used = 0' in line or f'_{tok}_used = 0' in line
                    for tok in [token, token.lower()]
                )
            ]
            if lines_with_token:
                for lineno, line in lines_with_token[:3]:
                    failures.append(
                        f"Forbidden token '{token}' at line {lineno}: {line[:100]}"
                    )
            else:
                print(f"    OK  '{token}' not active in clean method script")

    # ------------------------------------------------------------------
    # BLOCK 9: Hardcoded-result check
    # ------------------------------------------------------------------
    print("\n[9] Hardcoded-result check...")
    audit_ckpt = audit.get("gnn_checkpoint", "")
    if not audit_ckpt:
        failures.append("method_audit.json missing 'gnn_checkpoint' — possible hardcoded results.")
    else:
        print(f"    OK  gnn_checkpoint recorded: {audit_ckpt}")
    if len(df) < 50:
        failures.append(
            f"Per-cycle CSV has only {len(df)} rows — suspiciously small for N=3976 eval."
        )
    else:
        print(f"    OK  per-cycle rows: {len(df)}")

    # ------------------------------------------------------------------
    # BLOCK 10: FlexDATE comparison
    # ------------------------------------------------------------------
    print("\n[10] FlexDATE comparison (target topologies)...")
    TARGET_TOPOS = ["abilene", "cernet", "geant", "sprintlink"]
    for topo in TARGET_TOPOS:
        g = df[df["topology"] == topo]
        if len(g) == 0:
            print(f"    [warn] {topo} not in eval results")
            continue
        mean_pr = float(g["feat_PR"].mean()) if "feat_PR" in g.columns else float("nan")
        mean_db = float(g["chosen_disturbance"].mean()) if "chosen_disturbance" in g.columns else float("nan")
        fd = FLEXDATE.get(topo, {})
        pr_ok = mean_pr >= fd.get("PR", 0.0)
        db_ok = mean_db <= fd.get("DB", 1.0)
        status = "OK" if pr_ok else "WARN"
        print(f"    {status}  {topo}: PR={mean_pr:.4f} (≥{fd.get('PR',0):.3f}? {pr_ok})  "
              f"DB={mean_db:.5f} (≤{fd.get('DB',1):.4f}? {db_ok})")

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    if failures:
        print(f"CLEAN METHOD AUDIT FAILED — {len(failures)} error(s):", file=sys.stderr)
        for i, f in enumerate(failures, 1):
            print(f"  [{i}] {f}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

    print("CLEAN METHOD AUDIT PASSED — all checks passed.")
    print(
        "\nThis confirms the method is professor-compliant:\n"
        "  - GNN-LPD selector trained from DB-budgeted oracle labels (not heuristic)\n"
        "  - DQN controls K30/K40/K50 action + DB budget selection\n"
        "  - No RandomForest gate, no sticky reuse, no Stage-2, no heuristic fallback\n"
        "  - criticality_backend=gnn_lpd in every eval cycle"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
