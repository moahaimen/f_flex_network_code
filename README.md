# Clean GNN-LPD-DQN Traffic Engineering

This repository delivers the **final clean GNN-LPD-DQN traffic-engineering method**
together with its committed evidence artifacts. This is the only method that
constitutes the final result. The heuristic baselines from the earlier phases
(Top-K, bottleneck, OSPF/ECMP) and any RandomForest / sticky-gate / Stage-2
variants are **not** part of the final method — see
[Background / legacy utilities](#background--legacy-utilities--not-the-final-clean-method).

## Method

```
Traffic matrix + topology
  -> DB-budgeted LP-distilled GNN-LPD critical-OD selector
  -> DQN controller chooses K / action / DB budget
  -> selected critical ODs -> one-stage selected-flow DB-budgeted LP
  -> noncritical ODs remain on ECMP or previous routing
  -> capped K escalation if PR/MLU guard fails (K30 -> K40 -> K50)
  -> full-OD fallback only after the selected-K cap fails
```

Excluded by design and verified by the compliance audit: heuristic criticality,
RandomForest gate, sticky-gate reuse, Stage-2 DB LP, disturbance-finalization LP.

## First-run command (Windows)

After cloning, from the repository root:

```bat
python -m venv .venv && .venv\Scripts\activate && python -m pip install --upgrade pip && pip install -r requirements.txt && python scripts\phase1_5\windows_smoke_test.py
```

macOS / Linux:

```bash
python3 -m venv .venv && source .venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt && python scripts/phase1_5/windows_smoke_test.py
```

Expected final line:

```
READY FOR STUDENT RUN
```

Full Windows instructions: **[README_WINDOWS_RUN.md](README_WINDOWS_RUN.md)**.

## Report files

| File | Description |
|---|---|
| [STUDENT_PROFESSOR_FINAL_REPORT.pdf](STUDENT_PROFESSOR_FINAL_REPORT.pdf) | Final report (PDF) |
| [STUDENT_PROFESSOR_FINAL_REPORT.docx](STUDENT_PROFESSOR_FINAL_REPORT.docx) | Final report (Word) |
| [FINAL_REPORT.md](FINAL_REPORT.md) | Method summary (Markdown) |
| [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | Full pipeline + dataset + audit provenance |

## Evidence CSV locations

| Evidence | Path | Rows |
|---|---|---|
| Full evaluation | `results/gnn_lpd_dqn_selective_db_lp/final_N3976/per_cycle.csv` | 3,976 |
| Per-topology summary | `results/gnn_lpd_dqn_selective_db_lp/final_N3976/per_topology_summary.csv` | 8 |
| Failure validation | `results/gnn_lpd_dqn_selective_db_lp/failure_validation_clean/failure_per_cycle.csv` | 360 |
| Failure summary | `results/gnn_lpd_dqn_selective_db_lp/failure_validation_clean/failure_summary.csv` | 18 |
| LP-derived SDN simulation | `results/gnn_lpd_dqn_selective_db_lp/sdn_mininet_clean/sdn_per_run.csv` | 120 |
| SDN summary | `results/gnn_lpd_dqn_selective_db_lp/sdn_mininet_clean/sdn_summary.csv` | 12 |

Model and label artifacts:

| Artifact | Path |
|---|---|
| GNN-LPD selector checkpoint | `results/gnn_lpd_dqn_selective_db_lp/models/gnn_dbbudget_selector.pt` |
| DQN checkpoint | `results/gnn_lpd_dqn_selective_db_lp/dqn_best.pt` |
| Oracle labels | `results/gnn_lpd_dqn_selective_db_lp/labels/oracle_labels.csv` |
| Label provenance | `results/gnn_lpd_dqn_selective_db_lp/labels/label_provenance.json` |

## Audit command

```bash
python scripts/phase1_5/audit_gnn_lpd_dqn_clean_method.py --eval_dir results/gnn_lpd_dqn_selective_db_lp/final_N3976
```

Expected: `CLEAN METHOD AUDIT PASSED` — per-cycle rows = 3976, `criticality_backend = gnn_lpd`
in every row, and `heuristic_used = random_forest_gate_used = sticky_gate_used = stage2_used =
disturbance_finalization_used = 0`.

## Clean-method source files

| File | Role |
|---|---|
| `scripts/phase1_5/gnn_lpd_dqn_selective_db_lp.py` | Main method (selector + DQN + selected-flow DB-budgeted LP) |
| `scripts/phase1_5/build_dbbudget_oracle_labels.py` | DB-budgeted LP oracle label generation |
| `scripts/phase1_5/train_gnn_dbbudget_selector.py` | GNN-LPD selector training |
| `scripts/phase1_5/gnn_lp_inference.py` | GNN-LPD inference |
| `scripts/phase1_5/audit_gnn_lpd_dqn_clean_method.py` | Compliance audit |
| `scripts/phase1_5/run_failure_validation_clean.py` | Clean failure-scenario validation |
| `scripts/phase1_5/run_sdn_mininet_clean.py` | LP-derived SDN-style simulation (`--mode mininet` for Linux/OVS) |
| `scripts/phase1_5/windows_smoke_test.py` | Fresh-clone smoke test |
| `te/lp_solver.py` | Path LP solvers (incl. selected-flow DB-budgeted LP) |

---

## Background / legacy utilities — not the final clean method

> **The methods in this section are NOT part of the final clean GNN-LPD-DQN
> result.** They are earlier Phase-1/Phase-2 baselines and exploratory utilities,
> retained only for context and historical reproduction. Do **not** treat Top-K
> heuristic, bottleneck heuristic, OSPF/ECMP, RandomForest gating, sticky reuse,
> or Stage-2 LP as part of the final method — the final method explicitly
> excludes all of them (enforced by the compliance audit above).

The original repository also contains a flow-level TE simulator over SNDlib
dynamic traffic matrices with these earlier baselines:

- `M0` OSPF shortest path
- `M1` ECMP over equal-cost shortest candidate paths
- `M2` LP-optimal full MCF (all ODs, min MLU)
- `M3` Top-K demand heuristic + LP (selected ODs), ECMP for others — *legacy heuristic*
- `M4` Bottleneck-contribution heuristic + LP (selected ODs), ECMP for others — *legacy heuristic*
- `M5` RL selector + LP (optional, checkpoint-based) — *legacy*

These were used in Phase-1 (reactive TE) and Phase-2 (proactive TE with TM
prediction). They are independent of the clean GNN-LPD-DQN method and are kept
for reference only.

### Legacy Phase-1 / Phase-2 demos (reference only)

```bash
# Phase-1 reactive baselines demo
bash scripts/run_demo.sh

# Phase-2 proactive baselines demo
bash scripts/run_phase2_demo.sh
```

Legacy full runs (`eval.run_all`, `eval.run_phase2`), dataset download
(`scripts/download_sndlib.sh`), and preparation (`scripts/prepare_data.py`)
remain available for historical reproduction but are not required for, and not
part of, the final clean method.

### Legacy notes

- Chronological split is always 70/15/15 with no shuffling.
- Reported legacy metrics are computed on the test split.
- Deterministic seed is logged in `run_metadata.json`.
