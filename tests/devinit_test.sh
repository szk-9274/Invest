#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_PATH="${ROOT_DIR}/devinit.sh"

if [[ ! -f "${SCRIPT_PATH}" ]]; then
  echo "devinit.sh が見つかりません: ${SCRIPT_PATH}" >&2
  exit 1
fi

grep -Fq 'readonly LOG_FILE="${ROOT_DIR}/backend.log"' "${SCRIPT_PATH}" || {
  echo "backend.log 定義が不足しています" >&2
  exit 1
}

grep -Fq 'readonly FRONTEND_LOG_FILE="${ROOT_DIR}/frontend.log"' "${SCRIPT_PATH}" || {
  echo "frontend.log 定義が不足しています" >&2
  exit 1
}

grep -Fq 'tee -a $(escape "${LOG_FILE}")' "${SCRIPT_PATH}" || {
  echo "backend 起動コマンドの tee 出力設定が不足しています" >&2
  exit 1
}

grep -Fq 'tee -a $(escape "${FRONTEND_LOG_FILE}")' "${SCRIPT_PATH}" || {
  echo "frontend 起動コマンドの tee 出力設定が不足しています" >&2
  exit 1
}

grep -Fq 'tail -F $(escape "${LOG_FILE}") $(escape "${FRONTEND_LOG_FILE}")' "${SCRIPT_PATH}" || {
  echo "logs ペインの 2 ファイル同時追尾設定が不足しています" >&2
  exit 1
}

echo "OK: devinit.sh logs 設定"
