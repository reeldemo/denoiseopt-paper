#!/usr/bin/env bash
# Run approved experiment queue on one GPU (E1 → E5 → E4 → E2 → E3). Skips completed jobs.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=experiment_env.sh
source "${SCRIPT_DIR}/experiment_env.sh"
export PYTHONPATH="${PAPER_ENGINE}:${PYTHONPATH:-}"

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
p.parent.mkdir(parents=True, exist_ok=True)
data = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
data["queue_order"] = ["E1", "E5", "E4", "E2", "E3"]
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
  bash "${runner}"
  echo "== ${name} DONE"
}

mark_queue ""
run_step E1 "${RESULT_E1}" "${SCRIPT_DIR}/run_e1.sh"
run_step E5 "${RESULT_E5}" "${SCRIPT_DIR}/run_e5.sh"
run_step E4 "${RESULT_E4}" "${SCRIPT_DIR}/run_e4.sh"
run_step E2 "${RESULT_E2}" "${SCRIPT_DIR}/run_e2.sh"
run_step E3 "${RESULT_E3}" "${SCRIPT_DIR}/run_e3.sh"
mark_queue ""
echo "Queue complete. Status: ${QUEUE_STATUS}"
