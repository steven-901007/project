#!/usr/bin/env bash
set -euo pipefail

PY_SCRIPT="${1:-./xy_ppi.py}"   # 第1個參數：python 程式路徑（預設 ./xy_ppi.py）
shift || true

# === 這裡可以自訂要跑的清單 ===
# 每一行是一組參數（不含 sweep index，會自己加上）
CUSTOM_LIST=(
  "./xy_ppi.py 2021 05 30 05 01 "
  # "./xy_ppi.py 2021 05 30 05 25 "
  # "./xy_ppi.py 2021 05 30 05 31 "
  # "./xy_ppi.py 2021 05 30 05 55 "
  # "./xy_ppi.py 2021 05 31 05 17 "  
  # "./xy_ppi.py 2021 05 31 06 05 "  
  # "./xy_ppi.py 2021 05 31 08 30 "  
)

# === 如果有設定 list，就跑 list ===
if [ ${#CUSTOM_LIST[@]} -gt 0 ]; then
  echo "偵測到 CUSTOM_LIST，將依照 list 執行"
  for LINE in "${CUSTOM_LIST[@]}"; do
    for SWEEP in $(seq 0 17); do
      echo "========================================"
      echo "Running: python $LINE $SWEEP"
      echo "開始時間：$(date '+%Y-%m-%d %H:%M:%S')"
      python $LINE $SWEEP
      echo "結束時間：$(date '+%Y-%m-%d %H:%M:%S')"
      sleep 2
    done
  done
else
  # === 沒有設定 list，就跑你給的參數 ===
  PY_ARGS=("$@")
  for SWEEP in $(seq 0 17); do
    echo "========================================"
    echo "Running: python ${PY_SCRIPT} ${PY_ARGS[*]} ${SWEEP}"
    echo "開始時間：$(date '+%Y-%m-%d %H:%M:%S')"
    python "${PY_SCRIPT}" "${PY_ARGS[@]}" "${SWEEP}"
    echo "結束時間：$(date '+%Y-%m-%d %H:%M:%S')"
    sleep 2
  done
fi

echo "全部 sweeps 執行完畢。"
