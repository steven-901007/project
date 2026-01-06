#!/usr/bin/env bash
set -euo pipefail

# Python 解譯器位置（你可以換成 python3 或你的環境路徑）
PYTHON=python

# 跑 #1 ~ #12
for i in $(seq 1 12); do
  TAG="#${i}"
  echo "=============================="
  echo "Running data_set.py for ${TAG}"
  ${PYTHON} data_set.py "${TAG}"
done

echo "=============================="
echo "All sensors (#1 ~ #12) finished."
