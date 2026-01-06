#!/bin/bash

# 參數設定 (根據你程式需要調整)
# 從終端讀參數（沒給的話用預設值）
source=${1:-"CWA"}  # {"TLDS","EN","CWA"}

for YEAR in $(seq 2019 1 2024); do
    echo "Running flash_pattern_map.py with year=${YEAR} ..."
    python flash_pattern_map.py $YEAR $source
done






