#!/usr/bin/env bash
# Run approved experiment queue on one GPU (N2N rerun → E1 → E5 → E4 → E2 → E3). Skips completed jobs.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiment_env.sh
source "${SCRIPT_DIR}/experiment_env.sh"
export PYTHONPATH="${PAPER_ENGINE}:${PYTHONPATH:-}"

RESULT_N2N="${RESULTS_DIR}/n2n_baseline_rerun_complete.json"
RESULT_E1="${RESULTS_DIR}/e1_holdout_10seed.json"
RESULT_E5="${RESULTS_DIR}/e5_pareto_export.json"
RESULT_E4="${RESULTS_DIR}/e4_branch_ablation_5k.json"
RESULT_E2="${RESULTS_DIR}/e2_v14_converge_multiseed.json"
RESULT_E3="${RESULTS_DIR}/e3_meta_extra_seeds.json"

mark_queue() {
  export QUEUE_CURRENT="${1:-}"
  "${PAPER_PYTHON}" - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path
p = Path(os.environ["QUEUE_STATUS"])
if not p.parent.is_dir():
    raise SystemExit(f"RESULTS_DIR missing: {p.parent}")
data = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
data["queue_order"] = ["N2N_BASELINES", "E1", "E5", "E4", "E2", "E3"]
data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
cur = os.environ.get("QUEUE_CURRENT", "").strip()
data["current"] = cur or None
p.write_text(json.dumps(data, indent=2), encoding="utf-8")
PY
}

is_complete() {
  local f="$1"
  [[ -f "$f" ]] || return 1
  "${PAPER_PYTHON}" -c "import json,sys; d=json.load(open('$f')); sys.exit(0 if d.get('complete') else 1)"
}

n2n_rerun_complete() {
  local f="${RESULT_N2N}"
  local prov="${RESULTS_DIR}/n2n_retrain_provenance.json"
  [[ -f "$f" && -f "$prov" ]] || return 1
  "${PAPER_PYTHON}" - <<PY
import json, sys
from pathlib import Path
done = json.loads(Path("$f").read_text(encoding="utf-8"))
prov = json.loads(Path("$prov").read_text(encoding="utf-8"))
ok = done.get("complete") and done.get("n2n_checkpoint_sha256") == prov.get("sha256")
sys.exit(0 if ok else 1)
PY
}

run_step() {
  local name="$1"
  local result="$2"
  local runner="$3"
  if is_complete "$result"; then
    echo "== ${name} SKIP (complete: ${result})"
    return 0
  fi
  echo "== ${name} START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  mark_queue "${name}"
  if ! bash "${runner}"; then
    echo "== ${name} FAILED (aborting queue)" >&2
    exit 1
  fi
  echo "== ${name} DONE"
}

run_n2n_step() {
  if n2n_rerun_complete; then
    echo "== N2N_BASELINES SKIP (complete: ${RESULT_N2N})"
    return 0
  fi
  echo "== N2N_BASELINES START $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  mark_queue "N2N_BASELINES"
  if ! bash "${SCRIPT_DIR}/rerun_n2n_baselines.sh"; then
    echo "== N2N_BASELINES FAILED (aborting queue)" >&2
    exit 1
  fi
  echo "== N2N_BASELINES DONE"
}

mark_queue ""
run_n2n_step
run_step E1 "${RESULT_E1}" "${SCRIPT_DIR}/run_e1.sh"
run_step E5 "${RESULT_E5}" "${SCRIPT_DIR}/run_e5.sh"
run_step E4 "${RESULT_E4}" "${SCRIPT_DIR}/run_e4.sh"
run_step E2 "${RESULT_E2}" "${SCRIPT_DIR}/run_e2.sh"
run_step E3 "${RESULT_E3}" "${SCRIPT_DIR}/run_e3.sh"
mark_queue ""
echo "Queue complete. Status: ${QUEUE_STATUS}"
