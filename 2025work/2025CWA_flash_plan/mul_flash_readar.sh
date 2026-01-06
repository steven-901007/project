#!/bin/bash

# 建立2015~2024 CWA、EN(2018~2024)、TLDS IC CG 在台灣各縣市的總量

# 參數設定 (根據你程式需要調整)
# 從終端讀參數（沒給的話用預設值）
source=${1:-"CWA"}  # {"TLDS","EN","CWA"}

for YEAR in $(seq 2015 1 2024); do
    echo "Running flash_reader.py with year=${YEAR} ..."
    python flash_reader.py $YEAR $source
done






