#!/bin/bash

# 參數設定 (根據你程式需要調整)
# 從終端讀參數（沒給的話用預設值）
YEAR=${1:-2021}
MONTH=${2:-05}
DAY=${3:-30}
STATION=${4:-RCWF}
DRAW_MODE=${5:-all}
PID=${6:-park}
# 迴圈跑 z_target 3000~10000 (每1000)
for Z in $(seq 3000 1000 10000); do
    echo "Running CAPPI_PID.py with z_target=${Z} ..."
    python CAPPI_PID.py $YEAR $MONTH $DAY $STATION $DRAW_MODE $PID $Z
done
