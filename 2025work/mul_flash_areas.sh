#!/bin/bash

# 建立2015~2024 CWA、EN(2018~2024)、TLDS IC CG 在台灣各縣市的密度

# 參數設定
# [邏輯錯誤修正] 原本的 source=${1:-"CWA"} 會被下面的迴圈覆蓋，因此移除

for source in TLDS EN CWA; do
    for YEAR in $(seq 2015 1 2024); do
        
        # [邏輯錯誤修正] 根據註解，排除 EN 2018 年以前的資料
        if [ "$source" == "EN" ] && [ "$YEAR" -lt 2018 ]; then
            continue
        fi

        for ic_cg in IC CG; do
            echo "Running flash_areas.py with year=${YEAR} source=${source} type=${ic_cg} ..."
            # [變數錯誤修正] $IC_CG -> $ic_cg
            python flash_areas.py $YEAR $source $ic_cg
        done
    done
done