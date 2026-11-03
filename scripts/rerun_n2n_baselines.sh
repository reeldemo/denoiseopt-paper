#!/usr/bin/env bash
# Re-score all paper/reelsynth N2N baseline JSON and figures after checkpoint retrain.
# Requires REELSYNTH_ROOT @ 0a8567b, PAPER_PYTHON+torch, results/n2n_retrain_provenance.json sha256.
# PYTHONPATH: scripts/compat first (sitecustomize → SeamN2N.from_state shim for legacy benches).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiment_env.sh
source "${SCRIPT_DIR}/experiment_env.sh"
# shellcheck source=experiment_helpers.sh
source "${SCRIPT_DIR}/experiment_helpers.sh"

RS="${REELSYNTH_ROOT}"
ENGINE="${ENGINE_PYTHON}"
PAPER_COMPAT="${PAPER_ROOT}/scripts/compat"
export PYTHONPATH="${PAPER_COMPAT}:${RS}/scripts:${PAPER_ENGINE}:${PYTHONPATH:-}"
cd "${PAPER_ROOT}"
CLIFF_OUT="${RS}/brand/artifacts/cliff_strata.json"
CHAMP="${RS}/brand/artifacts/meta_approach_compare_v10/hybrid_lstm/champ_cell.pt"

run_step() {
  local name="$1"
  shift
  echo "== ${name} START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  "$@"
  research_backup_step "${name}" || exit $?
  echo "== ${name} DONE"
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

[[ -f "${RESULTS_DIR}/n2n_retrain_provenance.json" ]] || fail "missing results/n2n_retrain_provenance.json"

# Reelsynth @ 0a8567b: module-level from_state — benches expect SeamN2N.from_state (sitecustomize shim).
run_step n2n_compat_preflight "${ENGINE}" "${PAPER_COMPAT}/preflight_n2n_seam_compat.py"

# 1) Paired stats (first pass — refreshed again after merge below)
run_step n2n_stats_paired_pre "${PAPER_PYTHON}" "${PAPER_ROOT}/scripts/stats_paired_holdout.py"

# 2) Reelsynth GPU/CPU benches (load new n2n_corrupt_corrupt.pt)
run_step n2n_bench_v10 "${ENGINE}" "${RS}/scripts/bench_v10_n2n_vs_ours.py" --champ "${CHAMP}"
run_step n2n_bench_heal_latency "${ENGINE}" "${RS}/scripts/bench_signal_heal_latency.py"
run_step n2n_bench_cliff_strata "${ENGINE}" "${RS}/scripts/bench_cliff_strata.py" --out "${CLIFF_OUT}"
run_step n2n_bench_real_wt "${ENGINE}" "${RS}/scripts/real_wt_wrap_protocol.py"

# 3) Merge into figures/ + rescore sota_matrix / multiseed_summary N2N rows
run_step n2n_rebuild_figures "${PAPER_PYTHON}" "${PAPER_ROOT}/scripts/rebuild_n2n_paper_artifacts.py"

# 4) Stats + plots (paper repo)
run_step n2n_stats_paired_post "${PAPER_PYTHON}" "${PAPER_ROOT}/scripts/stats_paired_holdout.py"
run_step n2n_plot_v14 "${PAPER_PYTHON}" "${PAPER_ROOT}/scripts/plot_v14_paper_figures.py"
run_step n2n_fix_sota_bars "${PAPER_PYTHON}" "${PAPER_ROOT}/scripts/fix_sota_method_bars.py"

research_backup_step "n2n_baseline_rerun" || exit $?
echo "N2N baseline rerun complete. Marker: ${RESULTS_DIR}/n2n_baseline_rerun_complete.json"
