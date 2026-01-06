#!/usr/bin/env bash
# 用法：
# ./batch_rcntu_to_nc.sh /path/to/folder
#例：./mul_NTUradar2NC.sh /home/steven/python_data/NTU_radar/data/RCNTU_20210530_31_rhi/RCNTU_data/raw_by_date/20210530/
folder="$1"

# 確認資料夾存在
if [ ! -d "$folder" ]; then
    echo "❌ 資料夾不存在：$folder"
    exit 1
fi

# 找出 .scn 或 .rhi 檔案
files=$(find "$folder" -maxdepth 1 -type f \( -iname "*.scn" -o -iname "*.rhi" \) | sort)

# 沒找到就離開
if [ -z "$files" ]; then
    echo "⚠️ 沒有找到 .scn 或 .rhi 檔案"
    exit 0
fi

echo "📂 開始轉檔：$folder"
echo "-----------------------------"

# 一個一個檔案跑
for f in $files; do
    echo "▶️ 處理檔案：$(basename "$f")"
    python ../tmincarlpy/NTUradar2NC.py "$f"
    echo ""
done

echo "✅ 全部轉檔完成"
