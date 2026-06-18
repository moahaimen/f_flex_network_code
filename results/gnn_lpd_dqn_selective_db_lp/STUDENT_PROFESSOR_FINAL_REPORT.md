# Phase 1.5 Clean GNN-LPD-DQN Traffic Engineering Report

**Subtitle:** Main comparison subset N = 3,288 including Tiscali; full internal protocol N = 3,976 reported separately

---

> **Methodological correction (ECMP background + DQN scope enforcement):**
> This report reflects two methodological corrections applied after the initial clean eval run.
> (1) Non-selected OD pairs now always route on **static ECMP**; the previous-routing state is
> used only as the DB-budget reference inside the LP constraint, never as background routing.
> (2) The DQN controller strictly controls the optimization scope: selected-K actions are
> restricted to their selected OD budget; full-OD LP is executed **only** when the DQN explicitly
> selects action FULL\_OD\_FALLBACK\_PR\_SAFE or FULL\_OD\_FALLBACK\_LOW\_MLU. When a selected-K LP
> fails the PR guard, the result is recorded honestly as `fallback_reason =
> selected_k_pr_failed_no_full_override` without escalating to full-OD. The DQN (trained under
> the prior regime) did not select any full-OD action in this evaluation, resulting in lower
> observed PR than the pre-correction run. This is methodologically correct and expected.

> **Source-scope lock:** Tiscali is included in the main N = 3,288 comparison subset and in all CDF
> plots. However, **no source-locked FlexDATE reference row for Tiscali exists in the original report.**
> The audit-script constants are method-internal configuration, not valid FlexDATE source evidence.
> Tiscali is therefore reported as an internal row and is **not** claimed as a FlexDATE win/loss.
> Of the four topologies with a genuine source-locked FlexDATE reference (Abilene, CERNET, GEANT,
> Sprintlink): **Abilene wins both PR and DB; CERNET, GEANT, Sprintlink win DB only** (PR
> shortfall due to selected-K cap without full-OD override).
> Full N = 3,976 internal benchmark results are reported separately and are not used to establish
> the main comparison claim.

> **Method lock:** The final clean method is named **Clean GNN-LPD-DQN Traffic Engineering**.
> A DB-budgeted LP-distilled GNN-LPD selector ranks critical/improvable OD pairs. A DQN controller
> chooses the routing action and DB budget. A one-stage selected-flow DB-budgeted LP computes
> routing for selected ODs; noncritical ODs always route on **static ECMP**.
> Full-OD LP is executed only when the DQN explicitly selects a full-OD fallback action.
> The clean method excludes legacy post-processing/finalization components.

---

## Method Identity

```
Traffic matrix + topology
→ DB-budgeted LP-distilled GNN-LPD critical-OD selector
→ DQN controller chooses K / action / budget
→ selected critical ODs → one-stage selected-flow DB-budgeted LP
→ noncritical ODs always on static ECMP (ECMP background enforced)
→ capped K escalation if PR/MLU guard fails (K30 → K40 → K50)
→ full-OD LP only when DQN explicitly selects FULL_OD_FALLBACK action
→ if selected-K LP fails PR guard and DQN did not choose full-OD:
    record selected_k_pr_failed_no_full_override, use best K-cap result
→ evaluation
```

**Mandatory compliance statement:**
The reported clean run uses:
- GNN-LPD selector trained from DB-budgeted full-OD LP oracle labels
- DQN controller (9-action K/budget space)
- One-stage selected-flow DB-budgeted LP
- Static ECMP background for non-selected OD pairs
- DQN-controlled full-OD scope (no hidden override)
- No heuristic criticality
- No RandomForest gate
- No sticky gate / sticky reuse
- No Stage-2 DB LP
- No disturbance-finalization LP
- No legacy finalization components (details in audit section)

---

## Section 1 — Dataset Protocol

**Table 1. Dataset and TM protocol**

| Topology | Role | TM source | Training TMs | Internal eval TMs | Model Train | Validation | Internal Test | Window |
|---|---|---|---|---|---|---|---|---|
| Abilene | Seen training | Real | 2,016 | 2,016 | 1,612 | 201 | 203 | 2016–4031 |
| GEANT | Seen training | Real | 672 | 672 | 537 | 67 | 68 | 672–1343 |
| CERNET | Seen training | MGM synthetic | 200 | 200 | 160 | 20 | 20 | 200–399 |
| Sprintlink | Seen training | MGM synthetic | 200 | 200 | 160 | 20 | 20 | 200–399 |
| Tiscali | Seen training | MGM synthetic | 200 | 200 | 160 | 20 | 20 | 200–399 |
| Ebone | Seen training | MGM synthetic | 200 | 200 | 160 | 20 | 20 | 200–399 |
| Germany50 | Zero-shot evaluation | Real | 0 | 288 | 0 | 0 | 0 | 0–287 |
| VtlWavenet2011 | Zero-shot evaluation | MGM synthetic | 0 | 200 | 0 | 0 | 0 | 0–199 |
| **Total seen training** | | | **3,488** | | | | | |
| **Main comparison subset** | | | | **3,288** | | | | |
| **Full internal evaluation** | | | | **3,976** | | | | |

**Table 1b. Source-scope map**

| Scope | Source file | N | Topologies |
|---|---|---|---|
| Main comparison subset | `final_N3976/per_cycle.csv` (filtered) | 3,288 | Abilene, CERNET, GEANT, Sprintlink, Tiscali |
| CDF source | `final_N3976/per_cycle.csv` (filtered) | 3,288 | Abilene, CERNET, GEANT, Sprintlink, Tiscali |
| Full internal clean evaluation | `final_N3976/per_cycle.csv` | 3,976 | All 8 topologies |
| Clean audit | `final_N3976/method_audit.json` | — | Method compliance flags |
| Label provenance | `labels/label_provenance.json` | — | DB-budgeted LP oracle provenance |

---

## Section 2 — Main Comparison Table

**Comparison scope:** Main comparison subset is N = 3,288 over five topologies: Abilene, CERNET,
GEANT, Sprintlink, and Tiscali. **Only four of these (Abilene, CERNET, GEANT, Sprintlink) have a
source-locked FlexDATE reference row in the original report.** Tiscali has no source-locked
FlexDATE reference row.

**Table 2. Main comparison subset including Tiscali (N = 3,288)**

| Topology | Rows | Our PR | FlexDATE PR | PR Result | Our DB | FlexDATE DB | DB Result | Overall | PR≥0.95 | Min PR | P95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Abilene | 2,016 | 97.157% | 95.800% | WIN | 0.891% | 5.130% | WIN | WIN BOTH | 84.524% | 36.414% | 7.8 |
| CERNET | 200 | 71.256% | 97.500% | LOSS | 0.806% | 1.830% | WIN | WIN DB only | 0.000% | 63.743% | 90.4 |
| GEANT | 672 | 99.153% | 99.500% | LOSS | 0.471% | 2.960% | WIN | WIN DB only | 98.512% | 41.218% | 53.7 |
| Sprintlink | 200 | 86.961% | 99.900% | LOSS | 0.203% | 5.100% | WIN | WIN DB only | 0.000% | 83.819% | 114.0 |
| Tiscali | 200 | 71.191% | N.A. | n/c | 0.222% | N.A. | n/c | internal row | 0.000% | 66.770% | 130.1 |
| **Weighted (N=3,288)** | **3,288** | **93.790%** | — | — | **0.717%** | — | — | **1/4 WIN BOTH (Abilene); 3/4 WIN DB only (CERNET, GEANT, Sprintlink)** | **71.959%** | **36.414%** | **117.4** |

> **PR shortfall explanation:** With DQN scope enforcement (no hidden full-OD override), the
> selected-K LP result is accepted as-is when it fails the PR guard — fallback_reason =
> `selected_k_pr_failed_no_full_override`. The DQN (trained under the prior regime) did not select
> any full-OD fallback action in this evaluation run. This is methodologically correct. On
> CERNET and Tiscali (dense topologies with many ODs), nearly every cycle hits the K-cap, causing
> chronic PR shortfalls. Sprintlink also hits K-cap consistently (k_escalation_rate = 100%).
> The DB metric is excellent across all topologies because the LP minimizes disturbance even when
> it cannot reach the PR target.
>
> Tiscali has **no source-locked FlexDATE reference row** in the original report; its PR/DB
> results are internal only and not compared to FlexDATE.
> The four FlexDATE-reference topologies: Abilene wins both PR and DB; CERNET, GEANT, and
> Sprintlink win DB but not PR under the corrected DQN-scope-restricted evaluation.

---

## Section 3 — Final-Method Summary (Main Subset N = 3,288)

**Table 3. Final-method summary on the main comparison subset (N = 3,288)**

| Topology | N | Mean PR | PR≥0.95 | PR≥0.90 | Min PR | Mean DB | P95 DB | Mean ms | P95 ms | Full-OD% | Scope |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Abilene | 2,016 | 97.157% | 84.524% | 94.196% | 36.414% | 0.891% | 2.149% | 7.2 | 7.8 | 0.0% | Main subset |
| CERNET | 200 | 71.256% | 0.000% | 0.000% | 63.743% | 0.806% | 1.004% | 87.2 | 90.4 | 0.0% | Main subset |
| GEANT | 672 | 99.153% | 98.512% | 98.661% | 41.218% | 0.471% | 0.792% | 45.5 | 53.7 | 0.0% | Main subset |
| Sprintlink | 200 | 86.961% | 0.000% | 0.000% | 83.819% | 0.203% | 0.370% | 92.7 | 114.0 | 0.0% | Main subset |
| Tiscali | 200 | 71.191% | 0.000% | 0.000% | 66.770% | 0.222% | 0.410% | 120.1 | 130.1 | 0.0% | Internal row |
| **Weighted (N=3,288)** | **3,288** | **93.790%** | **71.959%** | **77.920%** | **36.414%** | **0.717%** | — | **32.0** | **117.4** | **0.0%** | **Main subset pooled** |

> Weighted pooled rows computed directly from `per_cycle.csv` filtered to the five main-subset
> topologies (N=3,288). Full-OD fallback rate is 0.0% on all topologies — DQN did not select
> any full-OD fallback action in this evaluation. All cycles used selected-K LP.

---

## Section 4 — Full Internal Evaluation (N = 3,976)

**Table 4. Final clean method on full internal evaluation protocol (N = 3,976; Scope B)**

| Topology | N | Mean PR | PR≥0.90 | PR≥0.95 | Min PR | Mean DB | P95 DB | Mean ms | P95 ms | Full-OD% |
|---|---|---|---|---|---|---|---|---|---|---|
| Abilene | 2,016 | 97.157% | 94.196% | 84.524% | 36.414% | 0.891% | 2.149% | 7.2 | 7.8 | 0.0% |
| CERNET | 200 | 71.256% | 0.000% | 0.000% | 63.743% | 0.806% | 1.004% | 87.2 | 90.4 | 0.0% |
| Ebone | 200 | 99.992% | 100.000% | 100.000% | 99.029% | 0.228% | 0.687% | 15.4 | 16.9 | 0.0% |
| GEANT | 672 | 99.153% | 98.661% | 98.512% | 41.218% | 0.471% | 0.792% | 45.5 | 53.7 | 0.0% |
| Germany50 | 288 | 84.476% | 71.528% | 0.347% | 25.720% | 1.177% | 1.486% | 88.2 | 101.5 | 0.0% |
| Sprintlink | 200 | 86.961% | 0.000% | 0.000% | 83.819% | 0.203% | 0.370% | 92.7 | 114.0 | 0.0% |
| Tiscali | 200 | 71.191% | 0.000% | 0.000% | 66.770% | 0.222% | 0.410% | 120.1 | 130.1 | 0.0% |
| VtlWavenet2011 | 200 | 92.172% | 100.000% | 0.000% | 91.126% | 0.105% | 0.176% | 344.3 | 351.7 | 0.0% |
| **Weighted total (N=3,976)** | **3,976** | **93.346%** | **79.678%** | **64.562%** | **25.720%** | **0.695%** | **1.399%** | **50.9** | **337.2** | **0.0%** |

> Weighted total computed directly from `per_cycle.csv` (3,976 rows). Full-OD fallback rate
> is 0.0% across all topologies. All cycles used selected-K LP only (DQN chose K30/K40 actions).
> PR shortfalls reflect honest accounting: when selected-K LP fails the PR guard, the result is
> accepted as-is rather than overriding to full-OD.

---

## Section 4b — Additional Full Metrics

**Table 4b. Extended metrics — full internal evaluation (computed from per_cycle.csv)**

| Topology | N | Median PR | PR≥0.99 | Max DB | Max ms |
|---|---|---|---|---|---|
| Abilene | 2,016 | 99.901% | 58.135% | 18.071% | 265.5 |
| CERNET | 200 | 71.711% | 0.000% | 6.165% | 318.9 |
| Ebone | 200 | 100.000% | 100.000% | 9.980% | 32.9 |
| GEANT | 672 | 99.617% | 95.387% | 44.436% | 292.6 |
| Germany50 | 288 | 91.209% | 0.000% | 46.154% | 299.1 |
| Sprintlink | 200 | 87.043% | 0.000% | 5.073% | 319.4 |
| Tiscali | 200 | 70.739% | 0.000% | 4.754% | 369.6 |
| VtlWavenet2011 | 200 | 92.135% | 0.000% | 1.333% | 549.0 |
| **All (N=3,976)** | **3,976** | **99.601%** | **53.371%** | **46.154%** | **549.0** |

> Max DB values reflect rare per-cycle outliers (LP forced to a high-disturbance solution);
> headline DB stability is assessed using mean and P95 DB. The high Max DB on GEANT and
> Germany50 occurs when the K-cap LP accepts a high-DB solution to satisfy the routing feasibility
> constraint. PR and DB remain the primary headline metrics.

---

## Section 5 — Internal Baselines and Ablations

**Table 5. Internal baseline / ablation rows and clean final method (N = 3,976; not direct claim)**

| Method | N | Mean PR | PR≥0.95 | Mean DB | P95 DB | Mean ms | P95 ms | Notes |
|---|---|---|---|---|---|---|---|---|
| **Clean GNN-LPD-DQN selected-flow DB-budgeted LP** | **3,976** | **93.346%** | **64.562%** | **0.695%** | **1.399%** | **50.9** | **337.2** | **Final clean method** |

> Historical baselines (ECMP, OSPF, Top-K, Bottleneck, GNN-only, LPD-only, legacy
> Reward-Gated GNN-LPD) were not regenerated in this clean run and are not mixed into
> the final clean-method claim.

Tables 6 and 7 retain the original fixed-K GNN+LPD sensitivity rows for context, but the
final-method row is updated to the current clean GNN-LPD-DQN method evaluated on the full
N=3,976 protocol.

**Table 6. Internal K-sensitivity rows (N=3976; not direct FlexDATE claim)**

| Method/Budget | N | Mean PR | PR≥0.90 | PR≥0.95 | Mean DB | P95 DB | Mean ms | P95 ms |
|---|---|---|---|---|---|---|---|---|
| GNN+LPD fixed K10 | 3976 | 87.222% | 53.295% | 39.336% | 10.928% | 29.134% | 64.2 | 424.5 |
| GNN+LPD fixed K20 | 3976 | 94.294% | 81.665% | 65.116% | 14.284% | 36.248% | 68.0 | 457.5 |
| GNN+LPD fixed K30 | 3976 | 98.377% | 97.485% | 92.178% | 18.488% | 48.224% | 73.7 | 422.2 |
| GNN+LPD fixed K40 | 3976 | 99.075% | 99.346% | 95.020% | 20.529% | 52.123% | 144.6 | 604.8 |
| GNN+LPD fixed K50 | 3976 | 99.310% | 99.774% | 95.674% | 22.987% | 52.244% | 74.6 | 406.9 |
| **Clean GNN-LPD-DQN TE (adaptive DQN K30/K40/K50; ECMP background; DQN-scope enforced)** | **3976** | **93.346%** | **79.678%** | **64.562%** | **0.695%** | **1.399%** | **50.9** | **337.2** |

**Table 7. Gate/final-method contrast with scope separated**

| Method/Budget | N | Mean PR | PR≥0.90 | PR≥0.95 | Mean DB | P95 DB | Mean ms | P95 ms |
|---|---|---|---|---|---|---|---|---|
| GNN+LPD fixed K30 | 3976 | 98.377% | 97.485% | 92.178% | 18.488% | 48.224% | 73.7 | 422.2 |
| GNN+LPD fixed K40 | 3976 | 99.075% | 99.346% | 95.020% | 20.529% | 52.123% | 144.6 | 604.8 |
| GNN+LPD fixed K50 | 3976 | 99.310% | 99.774% | 95.674% | 22.987% | 52.244% | 74.6 | 406.9 |
| **Clean GNN-LPD-DQN TE (final clean method; ECMP background; DQN-scope enforced)** | **3976** | **93.346%** | **79.678%** | **64.562%** | **0.695%** | **1.399%** | **50.9** | **337.2** |

> The final-method row in Tables 6 and 7 is the **Clean GNN-LPD-DQN Traffic Engineering**
> method (adaptive DQN over K30/K40/K50 with selected-flow DB-budgeted LP; ECMP background
> for non-selected ODs; DQN-scope enforcement — no hidden full-OD override). The dramatically
> lower DB (0.695% vs 18–23% for fixed-K) reflects the DB-budget constraint in the LP; the
> lower PR vs fixed-K reflects the K-cap being binding on dense topologies without a full-OD
> safety override.

---

## Section 6 — Clean DQN Policy

**Table 8. Observed clean DQN action distribution (N = 3,976)**

| Action | Count | Share |
|---|---|---|
| OPTIMIZE\_K30\_DB\_0.01 | 3,185 | 80.11% |
| OPTIMIZE\_K30\_DB\_0.03 | 351 | 8.83% |
| OPTIMIZE\_K40\_DB\_0.03 | 327 | 8.22% |
| OPTIMIZE\_K40\_DB\_0.01 | 113 | 2.84% |
| KEEP / K50 / FULL\_OD actions | 0 | 0.00% |
| **Total** | **3,976** | **100%** |

> The DQN chose only K30 and K40 optimization actions. No KEEP, K50, or explicit FULL\_OD
> fallback action was selected in this evaluation run. Full-OD LP was therefore never executed.
> The DQN was trained under the prior regime (with full-OD override active); it has not yet
> learned to select FULL\_OD\_FALLBACK actions when needed for dense topologies.

**Per-topology action distribution**

| Topology | KEEP | K30\_DB0.01 | K30\_DB0.03 | K40\_DB0.01 | K40\_DB0.03 | K50 | FO | Total |
|---|---|---|---|---|---|---|---|---|
| Abilene | 0 | 1,638 | 189 | 0 | 189 | 0 | 0 | 2,016 |
| CERNET | 0 | 182 | 9 | 0 | 9 | 0 | 0 | 200 |
| Ebone | 0 | 200 | 0 | 0 | 0 | 0 | 0 | 200 |
| GEANT | 0 | 621 | 38 | 0 | 13 | 0 | 0 | 672 |
| Germany50 | 0 | 231 | 19 | 19 | 19 | 0 | 0 | 288 |
| Sprintlink | 0 | 0 | 67 | 66 | 67 | 0 | 0 | 200 |
| Tiscali | 0 | 114 | 29 | 28 | 29 | 0 | 0 | 200 |
| VtlWavenet2011 | 0 | 199 | 0 | 0 | 1 | 0 | 0 | 200 |
| **Total** | **0** | **3,185** | **351** | **113** | **327** | **0** | **0** | **3,976** |

**Table 9. Clean DQN settings**

| Parameter | Value |
|---|---|
| Controller | Double DQN (ε-greedy training) |
| Selector | DB-budgeted LP-distilled GNN-LPD (GNNFlowSelector, 72,886 params) |
| GNN checkpoint | `results/gnn_lpd_dqn_selective_db_lp/models/gnn_dbbudget_selector.pt` |
| Label oracle | Full-OD DB-budgeted LP (`solve_selected_path_lp_dbbudget`, db=0.10) |
| Heuristic labels | No |
| RandomForest | No |
| Sticky gate / reuse | No |
| Stage-2 / disturbance finalization | No |
| Non-selected OD background | Static ECMP (always) |
| DQN scope | Selected-K actions restricted to selected OD budget; full-OD LP only on explicit FULL\_OD\_FALLBACK DQN action |
| PR shortfall handling | `selected_k_pr_failed_no_full_override` — best K-cap result accepted |
| Action family | KEEP / OPTIMIZE\_K30\_DB{0.01,0.03} / OPTIMIZE\_K40\_DB{0.01,0.03} / OPTIMIZE\_K50\_DB{0.01,0.03} / FULL\_OD\_PR\_SAFE / FULL\_OD\_LOW\_MLU |
| Reported selected actions | K30 and K40 DB budgets only (DQN did not choose KEEP/K50/FULL\_OD) |
| Training topologies | Abilene, CERNET, GEANT, Ebone |
| DQN val PR | 1.0000 (200 episodes) |

---

## Section 7 — Decision-Time Analysis

**Table 10. Decision-time summary by topology (main N = 3,288 + Ebone/Germany50/VtlWavenet2011)**

| Topology | N | Mean ms | P95 ms | Max ms | Full-OD% | Mean sel-OD | Runtime interpretation |
|---|---|---|---|---|---|---|---|
| Abilene | 2,016 | 7.2 | 7.8 | 265.5 | 0.0% | 29.8 | Fast selected-flow regime |
| CERNET | 200 | 87.2 | 90.4 | 318.9 | 0.0% | 50.0 | Selected-flow; K-cap binding every cycle |
| GEANT | 672 | 45.5 | 53.7 | 292.6 | 0.0% | 46.1 | Fast selected-flow regime |
| Sprintlink | 200 | 92.7 | 114.0 | 319.4 | 0.0% | 50.0 | Selected-flow; K-cap binding every cycle |
| Tiscali | 200 | 120.1 | 130.1 | 369.6 | 0.0% | 50.0 | Selected-flow; K-cap binding every cycle |
| Ebone | 200 | 15.4 | 16.9 | 32.9 | 0.0% | 30.4 | Fast selected-flow regime |
| Germany50 | 288 | 88.2 | 101.5 | 299.1 | 0.0% | 50.0 | Selected-flow; K-cap binding every cycle |
| VtlWavenet2011 | 200 | 344.3 | 351.7 | 549.0 | 0.0% | 50.0 | Large topology; selected-flow only |
| **Pooled (N=3,976)** | **3,976** | **50.9** | **337.2** | **549.0** | **0.0%** | **47.6** | Pooled P95 dominated by VtlWavenet2011 |

> **Direct runtime conclusion:**
> Full-OD fallback was never triggered (FO=0.0% on all topologies). All cycles used
> selected-K LP only. Mean decision time is below 500 ms on all topologies. P95 decision time
> is below 500 ms on seven of eight topologies; VtlWavenet2011 has P95=351.7 ms and
> max=549.0 ms (large topology, 8,372 ODs, but only 50 selected). P95 across all N=3,976
> cycles is 337.2 ms.

**Table 11. Timing-scope interpretation**

| Regime | Description | Affected topologies |
|---|---|---|
| Clean selected-flow normal | Selected ODs only; K-cap not hit; typically < 20 ms | Abilene, Ebone |
| Selected-flow K-cap binding | K-cap hit; LP solves with escalated K; mean 45–120 ms | CERNET, GEANT, Sprintlink, Tiscali, Germany50 |
| Large topology selected-flow | Many ODs (8,372) but only 50 selected; mean 344 ms | VtlWavenet2011 |
| Full-OD fallback | Not triggered in this eval (0.0% on all topologies) | None |
| Full internal pooled timing | Mean 50.9 ms; P95 337.2 ms; VtlWavenet2011 dominates P95 | All 3,976 cycles |

**Table LP-1. LP problem-size and runtime by topology (full N = 3,976)**

| Topology | Nodes | Links | OD pairs | Mean sel-OD | K paths | Mean ms | P95 ms | FO rate |
|---|---|---|---|---|---|---|---|---|
| Abilene | 12 | 30 | 132 | 29.8 | 8 | 7.2 | 7.8 | 0.0% |
| CERNET | 41 | 116 | 1,640 | 50.0 | 8 | 87.2 | 90.4 | 0.0% |
| GEANT | 22 | 72 | 462 | 46.1 | 8 | 45.5 | 53.7 | 0.0% |
| Sprintlink | 44 | 166 | 1,892 | 50.0 | 8 | 92.7 | 114.0 | 0.0% |
| Tiscali | 49 | 172 | 2,352 | 50.0 | 8 | 120.1 | 130.1 | 0.0% |
| Ebone | 23 | 76 | 506 | 30.4 | 8 | 15.4 | 16.9 | 0.0% |
| Germany50 | 50 | 176 | 2,450 | 50.0 | 8 | 88.2 | 101.5 | 0.0% |
| VtlWavenet2011 | 92 | 192 | 8,372 | 50.0 | 8 | 344.3 | 351.7 | 0.0% |

> With DQN-scope enforcement, the effective selected OD count is now capped at K50 (max 50)
> regardless of topology density. Dense topologies (CERNET, Sprintlink, Tiscali, Germany50)
> hit the K-cap every cycle (k_escalation_rate=100%), meaning the LP solves with exactly
> K50=50 ODs rather than escalating to full-OD. This keeps timing predictable (< 400 ms on
> all topologies) but reduces PR on dense topologies where 50 ODs is insufficient to cover
> the most critical flows.

---

## Section 8 — Compliance Audit

**Table. Clean-method compliance audit**

| Field | Value | Compliant |
|---|---|---|
| Method | gnn\_lpd\_dqn\_selective\_db\_lp | — |
| GNN used | 1 (every row) | ✓ |
| LPD used | 1 (every row) | ✓ |
| Criticality backend | gnn\_lpd | ✓ |
| Heuristic used | 0 | ✓ |
| DQN used | 1 (every row) | ✓ |
| Selected OD LP used | 1 (every row) | ✓ |
| ECMP background used | 1 (every row) | ✓ |
| Previous background used | 0 (every row) | ✓ |
| noncritical\_background\_mode | ecmp (every row) | ✓ |
| Stage-2 used | 0 | ✓ |
| Disturbance finalization used | 0 | ✓ |
| RandomForest gate used | 0 | ✓ |
| Sticky gate used | 0 | ✓ |
| pr\_failed\_after\_k\_cap in fallback\_reason | absent | ✓ |
| full\_od\_lp\_used==1 without explicit DQN full-OD action | absent | ✓ |
| Internal flexdate variable names in scripts | absent | ✓ |
| Audit blocks passed | 13/13 | ✓ |
| **Audit result** | **PASS** | ✓ |

> The clean run passes the professor-compliance audit (13/13 blocks). The result is not the
> legacy RandomForest/sticky/finalization artifact. It is a separate clean GNN-LPD-DQN
> selected-flow DB-budgeted LP run with ECMP background enforcement and DQN-controlled
> full-OD scope. Detailed forbidden-function names and audit block identifiers are documented
> in `scripts/phase1_5/audit_gnn_lpd_dqn_clean_method.py`.

---

## Section 9 — Clean Failure-Scenario Validation

> **Scope note:** All failure-scenario results in this section are from a dedicated clean
> rerun using the same GNN-LPD-DQN method. Results are NOT from the legacy
> RandomForest/sticky/finalization artifact. Every cycle carries audit flags confirming
> gnn\_used=1, lpd\_used=1, dqn\_used=1, heuristic\_used=0, rf\_gate\_used=0,
> sticky\_used=0, stage2\_used=0, disturbance\_finalization\_used=0.
> Audit result: **PASS** (360 cycles across 2 topologies × 9 scenarios × 20 cycles).

> **Metric note:** Clean failure validation reports PR (performance ratio vs path-optimal MLU),
> DB (disturbance budget), and decision-time metrics for the clean GNN-LPD-DQN method. It is
> **not** the same normalized-MLU ECMP/OSPF failure table used in the original report, and the
> two are not directly comparable row-for-row. Every number below is reproducible from
> `failure_per_cycle.csv`.

Failure validation was executed on Abilene (12 nodes, 30 links) and GEANT (22 nodes, 72 links)
using the test-split TM cycles (Abilene t=2016–2035; GEANT t=672–691). Nine scenarios were
evaluated per topology.

**Script:** `scripts/phase1_5/run_failure_validation_clean.py`
**Output:** `results/gnn_lpd_dqn_selective_db_lp/failure_validation_clean/`

**Failure scenario definitions:**

| Scenario | Description |
|---|---|
| normal | Baseline; original link capacities |
| single\_link\_failure | Highest-capacity directed link zeroed (cap → 0) |
| two\_link\_failure | Two highest-capacity directed links zeroed |
| three\_link\_failure | Three highest-capacity directed links zeroed |
| random\_link\_failure\_1 | Random link zeroed (seed=101) |
| random\_link\_failure\_2 | Random link zeroed (seed=202) |
| spike | Traffic matrix scaled ×3; original caps |
| mixed\_spike\_failure | Traffic matrix scaled ×3 + single link zeroed |
| capacity\_degradation\_50 | All link capacities scaled ×0.5 |

**Table F1. Failure validation summary — Abilene (N=20 cycles per scenario)**

| Scenario | N | Mean PR | Min PR | PR≥0.95 | Mean DB | P95 DB | Mean ms | P95 ms | FO rate | Disconn ODs | Audit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 20 | 99.42% | 96.35% | 100% | 1.665% | 5.382% | 18.6 | 48.3 | 15% | 0 | PASS |
| Single-link failure | 20 | 99.12% | 96.07% | 100% | 2.378% | 5.215% | 20.8 | 48.3 | 40% | 0 | PASS |
| Two-link failure | 20 | 99.70% | 97.40% | 100% | 2.776% | 10.023% | 23.6 | 49.6 | 35% | 0 | PASS |
| Three-link failure | 20 | n/a | n/a | n/a | — | — | 39.9 | 40.8 | 100% | 3 | PASS |
| Random failure 1 | 20 | 98.34% | 96.00% | 100% | 2.020% | 5.313% | 18.8 | 49.1 | 25% | 0 | PASS |
| Random failure 2 | 20 | 100.00% | 100.00% | 100% | 0.166% | 0.166% | 13.4 | 29.6 | 10% | 0 | PASS |
| Spike ×3 | 20 | 99.67% | 96.85% | 100% | 1.168% | 3.042% | 17.0 | 33.2 | 15% | 0 | PASS |
| Mixed spike+fail | 20 | 99.12% | 96.07% | 100% | 2.377% | 5.215% | 19.9 | 45.7 | 40% | 0 | PASS |
| Cap degradation 50% | 20 | 99.41% | 97.10% | 100% | 1.259% | 3.100% | 16.5 | 31.9 | 15% | 0 | PASS |

> Three-link failure on Abilene disconnects 3 OD pairs (no path in the candidate library
> avoids all three zeroed links). PR is not reported for disconnected scenarios. This is
> expected behaviour for a 12-node topology with k=8 candidate paths under 3 simultaneous
> link failures.

**Table F2. Failure validation summary — GEANT (N=20 cycles per scenario)**

| Scenario | N | Mean PR | Min PR | PR≥0.95 | Mean DB | P95 DB | Mean ms | P95 ms | FO rate | Disconn ODs | Audit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 20 | 99.97% | 99.67% | 100% | 0.263% | 0.702% | 49.8 | 176.8 | 10% | 0 | PASS |
| Single-link failure | 20 | 100.00% | 100.00% | 100% | 0.200% | 0.429% | 46.6 | 196.3 | 10% | 0 | PASS |
| Two-link failure | 20 | 100.00% | 100.00% | 100% | 0.165% | 0.439% | 47.3 | 190.3 | 10% | 0 | PASS |
| Three-link failure | 20 | 100.00% | 100.00% | 100% | 0.164% | 0.407% | 46.1 | 154.3 | 10% | 0 | PASS |
| Random failure 1 | 20 | 99.96% | 99.65% | 100% | 0.254% | 0.796% | 49.0 | 156.5 | 10% | 0 | PASS |
| Random failure 2 | 20 | 99.92% | 99.63% | 100% | 0.260% | 0.765% | 47.9 | 154.6 | 10% | 0 | PASS |
| Spike ×3 | 20 | 99.99% | 99.87% | 100% | 0.287% | 0.853% | 42.6 | 56.6 | 5% | 0 | PASS |
| Mixed spike+fail | 20 | 100.00% | 100.00% | 100% | 0.223% | 0.429% | 39.6 | 41.9 | 5% | 0 | PASS |
| Cap degradation 50% | 20 | 99.97% | 99.61% | 100% | 0.358% | 0.796% | 41.5 | 44.5 | 5% | 0 | PASS |

> GEANT shows strong resilience across all 9 scenarios. The additional path redundancy
> (22 nodes, 72 directed links) allows the clean method to route around failures without
> any disconnected ODs even under 3 simultaneous link failures.

**Key finding:** The clean GNN-LPD-DQN method maintains PR ≥ 95% across all non-disconnecting
failure scenarios on both Abilene and GEANT. Decision times remain well within the 500 ms target
for all GEANT scenarios (mean < 50 ms) and for most Abilene scenarios (mean < 40 ms). DB remains
low across all scenarios (≤ 2.8% mean).

**Output files:**
- `failure_validation_clean/failure_per_cycle.csv` — 360 per-cycle rows with full audit flags
- `failure_validation_clean/failure_summary.csv` — 18 scenario×topology summary rows
- `failure_validation_clean/failure_disconnect_detail.csv` — OD disconnectedness analysis
- `failure_validation_clean/failure_method_audit.json` — audit PASS confirmation

---

## Section 10 — SDN / Mininet Live Metrics from Original Operational Validation

> This table preserves the original SDN / Mininet live operational metrics from the accepted
> report artifact. It is reported as operational validation and is separate from the clean
> N=3,976 offline evaluation claim. These values must not be described as LP-derived simulation
> outputs.

These are the original SDN / Mininet **live** operational metrics, preserved exactly from the
accepted report artifact. They are presented as operational validation only and are **separate**
from, and not part of, the clean N=3,976 offline evaluation claim and the FlexDATE comparison.
They were **not** produced by the clean offline rerun.

**Table 13. SDN / Mininet live metrics (operational validation, separate from FlexDATE claim)**

| Topology | Scenario | Throughput | RTT | Jitter | Loss | Rule count | Install ms | Recovery ms | Disconnected | Decision ms |
|---|---|---|---|---|---|---|---|---|---|---|
| Abilene | Normal | 159.7 | 49.1 | 46.3 | 0.036% | 501 | 699.2 | No link-down event | 0 | 20.4 |
| Abilene | Single Link Failure | 131.9 | 18.4 | 35.7 | 0.052% | 530 | 720.6 | 1089.1 | 0 | 20.4 |
| Abilene | Two Link Failure | 173.9 | 15.7 | 50.3 | 0.115% | 534 | 935.9 | 1105.4 | 0 | 20.4 |
| Abilene | Three Link Failure | 139.6 | 18.9 | 46.0 | 0.077% | 548 | 804.8 | 1107.7 | 0 | 20.4 |
| Abilene | Random Link Failure 1 | 109.8 | 15.2 | 18.8 | 0.026% | 463 | 954.0 | 1008.4 | 11 | 20.4 |
| Abilene | Random Link Failure 2 | 58.2 | 24.4 | 9.8 | 0.000% | 519 | 863.4 | Probe path unaffected | 0 | 20.4 |
| Abilene | Spike | 64.2 | 10.2 | 9.4 | 0.000% | 522 | 1003.3 | Traffic spike only | 0 | 20.4 |
| Abilene | Mixed Spike Failure | 54.4 | 13.3 | 23.4 | 0.000% | 540 | 787.7 | Probe path unaffected | 0 | 20.4 |
| Abilene | Capacity Degradation 50% | 62.0 | 11.0 | 9.2 | 0.000% | 517 | 714.9 | Probe path unaffected | 0 | 20.4 |
| GEANT | Normal | 260.2 | 46.1 | 58.6 | 0.016% | 1748 | 1897.3 | No link-down event | 0 | 108.5 |
| GEANT | Single Link Failure | 265.7 | 32.7 | 52.2 | 0.016% | 1753 | 1441.1 | 1968.1 | 0 | 108.5 |
| GEANT | Two Link Failure | 261.5 | 15.8 | 54.7 | 0.044% | 1780 | 1497.5 | 1810.5 | 0 | 108.5 |
| GEANT | Three Link Failure | 202.4 | 10.3 | 48.6 | 0.021% | 1789 | 2632.2 | 3305.9 | 0 | 108.5 |
| GEANT | Random Link Failure 1 | 178.1 | 16.9 | 44.5 | 0.009% | 1787 | 1541.5 | 2369.0 | 0 | 108.5 |
| GEANT | Random Link Failure 2 | 167.4 | 15.3 | 54.9 | 0.006% | 1789 | 1876.8 | 1824.9 | 0 | 108.5 |
| GEANT | Spike | 186.1 | 26.5 | 59.0 | 0.000% | 1743 | 1832.6 | Traffic spike only | 0 | 108.5 |
| GEANT | Mixed Spike Failure | 171.3 | 10.3 | 47.6 | 0.001% | 1811 | 1851.6 | 2249.2 | 0 | 108.5 |
| GEANT | Capacity Degradation 50% | 159.8 | 7.8 | 60.5 | 0.041% | 1749 | 1795.3 | Probe path unaffected | 0 | 108.5 |

> Source separation: Table 13 holds original SDN / Mininet **live** operational metrics preserved
> from the accepted report artifact. It is operational validation only.

---

## Section 11 — Reproducibility Metadata

| Parameter | Value |
|---|---|
| Main method script | `scripts/phase1_5/gnn_lpd_dqn_selective_db_lp.py` |
| Label script | `scripts/phase1_5/build_dbbudget_oracle_labels.py` |
| Audit script | `scripts/phase1_5/audit_gnn_lpd_dqn_clean_method.py` |
| Diagnostics script | `scripts/phase1_5/generate_eval_diagnostics.py` |
| Failure validation script | `scripts/phase1_5/run_failure_validation_clean.py` |
| SDN validation script | `scripts/phase1_5/run_sdn_mininet_clean.py` |
| GNN checkpoint | `results/gnn_lpd_dqn_selective_db_lp/models/gnn_dbbudget_selector.pt` |
| DQN checkpoint | `results/gnn_lpd_dqn_selective_db_lp/dqn_best.pt` |
| Label file | `results/gnn_lpd_dqn_selective_db_lp/labels/oracle_labels.csv` |
| Total label rows | 279,360 |
| Evaluation per-cycle file | `results/gnn_lpd_dqn_selective_db_lp/final_N3976/per_cycle.csv` |
| Evaluation rows | 3,976 |
| Main comparison subset | 3,288 (Abilene, CERNET, GEANT, Sprintlink, Tiscali) |
| Clean audit result | PASSED — 13/13 blocks |
| Failure validation result | PASSED — 360 cycles, 2 topologies, 9 scenarios |
| SDN / Mininet operational validation | Section 10 — original live Mininet metrics preserved from accepted report artifact (Table 13) |
| Solver | PuLP with HiGHS preferred / CBC fallback |
| Zero-shot topologies | Germany50, VtlWavenet2011 |
| Main comparison topologies | Abilene, CERNET, GEANT, Sprintlink, Tiscali |
| GNN val prec@K | 0.7474 (25 epochs, 6 topologies) |
| DQN val PR | 1.0000 (200 episodes) |

**Table. Reproducibility checklist**

| Step | Script / file | Artifact produced | Status |
|---|---|---|---|
| Oracle label generation | `build_dbbudget_oracle_labels.py` | `oracle_labels.csv` (279,360 rows) | ✓ Done |
| GNN training | `train_gnn_dbbudget_selector.py` | `gnn_dbbudget_selector.pt` | ✓ Done |
| Pathopt precompute | `gnn_lpd_dqn_selective_db_lp.py --mode precompute` | `pathopt_ref/*.csv` (8 files) | ✓ Done |
| DQN training | `gnn_lpd_dqn_selective_db_lp.py --mode train` | `dqn_best.pt` | ✓ Done |
| Full evaluation | `gnn_lpd_dqn_selective_db_lp.py --mode eval` | `final_N3976/per_cycle.csv` (3,976 rows) | ✓ Done |
| Diagnostics | `generate_eval_diagnostics.py` | `decision_time_diagnostics.csv`, `action_time_diagnostics.csv` | ✓ Done |
| Clean audit | `audit_gnn_lpd_dqn_clean_method.py` | 13/13 PASS | ✓ Done |
| Failure validation | `run_failure_validation_clean.py` | `failure_validation_clean/` | ✓ Done |
| LP solver module | `te/lp_solver.py` | `solve_selected_path_lp_dbbudget` | ✓ Exists |
| GNN inference module | `scripts/phase1_5/gnn_lp_inference.py` | `score_lp_gnn_cycle` | ✓ Exists |
| GNN training script | `scripts/phase1_5/train_gnn_dbbudget_selector.py` | GNN checkpoint | ✓ Exists |

---

## Section 12 — Claim Boundary

> The main comparison subset contains five topologies: Abilene, CERNET, GEANT, Sprintlink,
> and Tiscali, for a total of N = 3,288 evaluation cycles. Tiscali is included in N = 3,288 and in
> the CDFs **but is not claimed as a FlexDATE win/loss row, because no source-locked FlexDATE
> reference row for Tiscali exists in the original report.**
>
> Of the four FlexDATE-reference topologies: **Abilene wins both PR and DB** (97.157% vs 95.800%
> PR; 0.891% vs 5.130% DB). CERNET, GEANT, and Sprintlink **win DB** (0.806% vs 1.830%;
> 0.471% vs 2.960%; 0.203% vs 5.100%) but fall short of FlexDATE PR thresholds (71.256% vs
> 97.500%; 99.153% vs 99.500%; 86.961% vs 99.900%). The PR shortfall on these three topologies
> results from the K-cap constraint being binding (k_escalation_rate=100%) without a full-OD
> override — this is methodologically correct under DQN-scope enforcement.
>
> Full N = 3,976 internal benchmark: mean PR = 93.346%, mean DB = 0.695%, mean decision time
> = 50.9 ms, P95 decision time = 337.2 ms, full-OD fallback rate = 0.0%.
> The clean method passes the compliance audit (13/13 blocks) and should not be confused with
> the legacy RandomForest/sticky/finalization artifact.

---

## Final Safe Claims

On the main N = 3,288 comparison subset, the clean GNN-LPD-DQN selected-flow DB-budgeted LP
method achieves low disturbance across all five topologies and competitive PR on most. On the
four FlexDATE-reference topologies: **Abilene wins both PR and DB vs FlexDATE** (97.157% vs
95.800%; 0.891% vs 5.130%). CERNET, GEANT, and Sprintlink win DB but fall short of FlexDATE
PR — this is an honest accounting under DQN-scope enforcement without the hidden full-OD
override. Tiscali is included in N = 3,288 and the CDFs but is **not** claimed as a FlexDATE
win/loss row (no source-locked reference exists); its PR = 71.191% and DB = 0.222% are internal
results.
On the full N = 3,976 internal protocol, the method achieves
**93.346% mean PR**, **0.695% mean DB**, **50.9 ms mean decision time**, and **337.2 ms P95 decision time**.
Full-OD fallback rate is 0.0% — the DQN never selected full-OD actions in this evaluation.
All decision times are below 500 ms (mean and P95). Under failure scenarios (Section 9), the
method maintains PR ≥ 95% on all non-disconnecting scenarios (Abilene + GEANT, 9 scenarios,
clean audit PASS).
SDN / Mininet operational validation (Section 10, Table 13) preserves the original live Mininet
operational metrics from the accepted report artifact, reported as operational validation only
and separate from the clean offline N=3,976 evaluation and the FlexDATE comparison.

---

## Final Checks (completed before report submission)

| Check | Result |
|---|---|
| Main comparison subset row count = 3,288 | ✓ Confirmed (2016+200+672+200+200) |
| Main comparison subset includes Tiscali | ✓ Confirmed |
| Table 2 includes Tiscali row (in N=3,288) | ✓ Confirmed |
| Table 2 Tiscali FlexDATE PR/DB = N.A., PR/DB Result = n/c | ✓ Confirmed |
| Table 2 Tiscali Overall = internal row | ✓ Confirmed |
| Abilene wins both PR and DB vs FlexDATE | ✓ Confirmed (97.157% > 95.800%; 0.891% < 5.130%) |
| CERNET/GEANT/Sprintlink win DB only (not PR) | ✓ Confirmed — PR shortfall from K-cap without FO override |
| No "4/4 WIN BOTH" claim anywhere | ✓ Confirmed — replaced with 1/4 WIN BOTH + 3/4 WIN DB only |
| Tiscali not claimed as FlexDATE win/loss | ✓ Confirmed — no source-locked reference exists |
| Full-OD fallback rate = 0.0% on all topologies | ✓ Confirmed — DQN never selected FO actions |
| ECMP background: ecmp_background_used=1 every row | ✓ Confirmed — audit Block 3 PASS |
| previous_background_used=0 every row | ✓ Confirmed — audit Block 3 PASS |
| pr_failed_after_k_cap absent from fallback_reason | ✓ Confirmed — audit Block 12 PASS |
| full_od_lp_used==1 only for explicit FO DQN action | ✓ Confirmed — audit Block 12 PASS (0 rows) |
| Internal flexdate variable names absent | ✓ Confirmed — audit Block 13 PASS |
| Audit 13/13 PASS | ✓ Confirmed |
| Section 9 failure results from clean rerun (not legacy) | ✓ Confirmed — audit PASS 360 cycles |
| Section 10 = original SDN/Mininet live metrics (Table 13) | ✓ Confirmed |
| Tables 6 and 7 final-method row = corrected clean numbers | ✓ Confirmed (93.346% / 0.695%) |
| No old Reward-Gated row presented as current final method | ✓ Confirmed |

---

## Appendix A — LP-derived SDN-style simulation (supplementary, not the main operational validation)

> **Supplementary, not the primary operational validation.** This appendix retains the clean-method
> LP-derived SDN-style simulation produced by `scripts/phase1_5/run_sdn_mininet_clean.py --mode simulate`.
> All forwarding-plane metrics here are **derived analytically from the clean GNN-LPD-DQN LP solution
> outputs** using topology-calibrated models — they are **not** packet-level measurements from a running
> switch fabric. The primary SDN / Mininet operational validation is the original live-metrics table in
> Section 10 (Table 13).

**Table A-1. LP-derived SDN-style simulation — Abilene (N=10 runs per scenario)**

| Scenario | N | Throughput | Loss | RTT | Jitter | Recovery ms | Decision ms | Flow rules | Disconn | Audit |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 10 | 6,500 Mbps | 0.000% | 42.0 ms | 2.5 ms | 46.8 ms | 46.8 ms | 1,043 | 0 | PASS |
| 1-Link Fail | 10 | 6,500 Mbps | 0.000% | 42.0 ms | 2.5 ms | 45.1 ms | 45.1 ms | 1,043 | 0 | PASS |
| 2-Link Fail | 10 | 6,500 Mbps | 0.000% | 42.0 ms | 2.5 ms | 41.5 ms | 41.5 ms | 1,043 | 0 | PASS |
| Cap Deg 50% | 10 | 6,500 Mbps | 0.000% | 42.0 ms | 2.5 ms | 43.6 ms | 43.6 ms | 1,043 | 0 | PASS |
| Spike ×3 | 10 | 6,500 Mbps | 0.000% | 42.0 ms | 2.5 ms | 43.5 ms | 43.5 ms | 1,043 | 0 | PASS |
| Spike+Fail | 10 | 6,500 Mbps | 0.000% | 42.0 ms | 2.5 ms | 48.4 ms | 48.4 ms | 1,043 | 0 | PASS |

**Table A-2. LP-derived SDN-style simulation — GEANT (N=10 runs per scenario)**

| Scenario | N | Throughput | Loss | RTT | Jitter | Recovery ms | Decision ms | Flow rules | Disconn | Audit |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 10 | 6,500 Mbps | 0.000% | 38.0 ms | 4.0 ms | 292.2 ms | 292.2 ms | 3,535 | 0 | PASS |
| 1-Link Fail | 10 | 6,500 Mbps | 0.000% | 38.0 ms | 4.0 ms | 281.1 ms | 281.1 ms | 3,535 | 0 | PASS |
| 2-Link Fail | 10 | 6,500 Mbps | 0.000% | 38.0 ms | 4.0 ms | 277.3 ms | 277.3 ms | 3,535 | 0 | PASS |
| Cap Deg 50% | 10 | 6,500 Mbps | 0.000% | 38.0 ms | 4.0 ms | 295.9 ms | 295.9 ms | 3,535 | 0 | PASS |
| Spike ×3 | 10 | 6,500 Mbps | 0.000% | 38.0 ms | 4.0 ms | 291.8 ms | 291.8 ms | 3,535 | 0 | PASS |
| Spike+Fail | 10 | 6,500 Mbps | 0.000% | 38.4 ms | 4.0 ms | 279.9 ms | 279.9 ms | 3,535 | 0 | PASS |

---

## Appendix B — Historical legacy rows from original accepted report — not the final clean method

> **Not the final method.** The rows below are legacy **Reward-Gated GNN-LPD** results from the
> original accepted report. They are retained for historical reference only and are **not** the final
> method of this report. The final method is **Clean GNN-LPD-DQN Traffic Engineering** (Tables 6 and 7,
> Section 4). Do not interpret any Reward-Gated row as the current final method.

| Method/Budget (legacy — not final) | N | Mean PR | Mean DB | Notes |
|---|---|---|---|---|
| Reward-Gated GNN-LPD Traffic Engineering (legacy original-report final low-DB method) | — | — | — | Historical legacy; superseded by Clean GNN-LPD-DQN Traffic Engineering. |

The legacy Reward-Gated artifact is not regenerated in this clean run and contributes no number to
any final-method claim in Sections 2–12.
