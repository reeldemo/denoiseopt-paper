# Shared helpers for experiment launchers (source after experiment_env.sh).

research_backup_step() {
  local step="${1:?step name required}"
  local hook="${HOME}/bin/research-backup-now"
  if [[ "${RESEARCH_BACKUP_OPTIONAL:-0}" == "1" ]]; then
    if [[ -x "${hook}" ]]; then
      "${hook}" "${step}" || true
    fi
    return 0
  fi
  if [[ ! -x "${hook}" ]]; then
    echo "ERROR: mandatory backup hook missing or not executable: ${hook}" >&2
    echo "  Install ~/bin/research-backup-now or set RESEARCH_BACKUP_OPTIONAL=1 (dry-run/CI only)." >&2
    return 1
  fi
  rc=0
  "${hook}" "${step}" || rc=$?
  if [[ "${rc}" -ne 0 ]]; then
    echo "ERROR: research-backup-now failed for step=${step} (exit ${rc})" >&2
    return "${rc}"
  fi
  return 0
}
