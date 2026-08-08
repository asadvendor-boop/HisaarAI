#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=src

check() {
  local number="$1"
  local label="$2"
  shift 2
  printf '\n[%s/8] %s\n' "$number" "$label"
  uv run pytest -q "$@"
}

check 1 "Non-clear Model Armor never reaches Gemini" \
  tests/test_task3_protection.py::test_injection_match_blocks_before_gemini \
  tests/test_task3_protection.py::test_unavailable_screening_blocks_before_gemini
check 2 "Vendor mismatch quarantines without a receipt" \
  tests/test_task3_protection.py::test_semantic_tamper_reaches_quarantine_after_real_agent_stage
check 3 "Execution before approval is denied" \
  tests/test_task5_governance.py::test_execution_before_approval_is_denied
check 4 "Wrong or expired approval is denied" \
  tests/test_task5_governance.py::test_wrong_commander_cannot_change_state \
  tests/test_task5_governance.py::test_expired_warrant_blocks_without_receipt
check 5 "Clean standby excludes contaminated context" \
  tests/test_task4_recovery.py::test_recovery_uses_revision_and_excludes_contaminated_context
check 6 "Duplicate execution returns one stable receipt" \
  tests/test_task5_governance.py::test_one_human_decision_completes_once_and_replay_is_stable
check 7 "Verification disagreement fails closed" \
  tests/test_task2_gate.py::test_verification_disagreement_fails_closed
check 8 "Clean control completes normally" \
  tests/test_task5_governance.py::test_clean_control_completes_normally

printf '\nHisaarAI demo-check: all eight business invariants passed.\n'
