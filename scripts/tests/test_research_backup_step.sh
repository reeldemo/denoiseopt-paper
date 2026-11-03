#!/usr/bin/env bash
# Shell tests for mandatory research-backup-now policy.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../experiment_helpers.sh
source "${ROOT}/experiment_helpers.sh"

TMP_HOME="$(mktemp -d)"
trap 'rm -rf "${TMP_HOME}"' EXIT
export HOME="${TMP_HOME}"
export RESEARCH_BACKUP_HOOK="${HOME}/bin/research-backup-now"
mkdir -p "${HOME}/bin"

pass=0
fail_count=0

assert_fail() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "FAIL: ${name} (expected non-zero)" >&2
    fail_count=$((fail_count + 1))
  else
    echo "ok ${name}"
    pass=$((pass + 1))
  fi
}

assert_ok() {
  local name="$1"
  shift
  if "$@"; then
    echo "ok ${name}"
    pass=$((pass + 1))
  else
    echo "FAIL: ${name}" >&2
    fail_count=$((fail_count + 1))
  fi
}

# Missing hook, backup required
unset RESEARCH_BACKUP_OPTIONAL
assert_fail "missing_hook_required" research_backup_step "test_step"

# Optional mode skips missing hook
export RESEARCH_BACKUP_OPTIONAL=1
assert_ok "optional_missing_hook" research_backup_step "test_step"

# Hook that fails (mandatory mode)
RESEARCH_BACKUP_OPTIONAL=0
export RESEARCH_BACKUP_OPTIONAL
cat >"${HOME}/bin/research-backup-now" <<'EOF'
#!/usr/bin/env bash
exit 42
EOF
chmod +x "${HOME}/bin/research-backup-now"
assert_fail "hook_nonzero" research_backup_step "bad_step"

# Hook success
RESEARCH_BACKUP_OPTIONAL=0
export RESEARCH_BACKUP_OPTIONAL
cat >"${HOME}/bin/research-backup-now" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "${HOME}/bin/research-backup-now"
assert_ok "hook_success" research_backup_step "good_step"

echo "research_backup_step: ${pass} passed, ${fail_count} failed"
exit "${fail_count}"
