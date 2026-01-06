#!/usr/bin/env bash
# 用法：
# ./mul_PID_count_3in1.sh 2021-05-30T12:00:00 2021-05-30T16:00:00 RCWF park 0.125
# ./mul_PID_count_3in1.sh 2021-05-31T12:00:00 2021-05-31T21:00:00 RCWF park 0.25
# ./mul_PID_count_3in1.sh 2021-05-24T12:00:00 2021-05-24T16:00:00 RCWF park 0.05


start="$1"      # 例：2021-05-30T04:00:00
end="$2"        # 例：2021-05-30T08:00:00
station="$3"    # 例：RCWF
pid="$4"        # 例：park
range="$5"    # 例：0.25

data_top_path="/home/steven/python_data/radar"

ts_start=$(date -d "$start" +%s)
ts_end=$(date -d "$end" +%s)

t=$ts_start
while [ $t -le $ts_end ]; do
  ymd=$(date -u -d "@$t" +"%Y%m%d")
  hms=$(date -u -d "@$t" +"%H%M%S")
  folder="${data_top_path}/PID/${ymd}_${station}_${pid}"
  file="${folder}/${ymd}${hms}.nc"

  if [ -f "$file" ]; then
    # 🧠 解析時間（例如 20210530040100）
    fname=$(basename "$file")         # => 20210530040100.nc
    timestamp="${fname%.nc}"          # => 20210530040100

    yyyy=${timestamp:0:4}             # 2021
    mm=${timestamp:4:2}               # 05
    dd=${timestamp:6:2}               # 30
    HH=${timestamp:8:2}               # 04
    MM=${timestamp:10:2}              # 01


    echo "📁 找到檔案：$file"
    echo "⏱️ 時間拆解：$yyyy-$mm-$dd $HH:$MM"

    # ✅ 在這裡直接呼叫 Python，並把年月日時分秒帶入
    python PID_count_3in1.py "$yyyy" "$mm" "$dd" "$HH" "$MM" "$station" "1" "$range" 
    # python PID_count_3in1.py "$yyyy" "$mm" "$dd" "$HH" "$MM" "$station" "2"
    # ↑ 最後 "2" 是 point_num，如果要單點改成 "1" 並加上半徑參數

  fi
  t=$((t+60))
done
