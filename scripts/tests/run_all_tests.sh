#!/usr/bin/env bash
# Run paper launcher unit/shell tests (CI: RESEARCH_BACKUP_OPTIONAL=1 where needed).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

bash "${ROOT}/tests/test_research_backup_step.sh"
bash "${ROOT}/tests/test_experiment_preflight.sh"
python3 "${ROOT}/compat/test_n2n_seam_compat.py" -v
python3 "${ROOT}/engine/test_holdout_eval_n2n.py" -v

echo "All scripts/tests passed"
