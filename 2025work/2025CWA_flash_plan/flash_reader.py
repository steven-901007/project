# -*- coding: utf-8 -*-
"""
計算各縣市閃電量
目前支援2019~2024年 CWA、EN 以及 TLDS 資料。
data_source ∈ {"TLDS","EN","CWA"}  # 僅單選，不支援 ALL
建立各縣市的IC、CG量 path = city_counts
讀檔path = raw_data
"""

import os, glob
import pandas as pd
import geopandas as gpd

## ============================== 常用轉換 ============================== ##
def _normalize_type(series):
    """將各來源型別正規化為 'IC' / 'CG'（其餘給 'UNK'）"""
    s = series.astype(str).str.strip().str.upper()
    map_dict = {
        "C": "IC", "CLOUD": "IC", "IC": "IC",
        "G": "CG", "GROUND": "CG", "CG": "CG",
    }
    return s.map(map_dict).fillna(s.where(s.isin(["IC","CG"]), "UNK"))

## ============================== 內部：各來源讀檔（依你提供的標題） ============================== ##
def _read_cwa_one_year_df(year_int, cwa_root_path_str):
    """
    CWA 欄位：
    Solution Key, Epoch Time, Nanoseconds, Major Code, Minor Code, Latitude, Longitude, ...
    """
    fp = os.path.join(cwa_root_path_str, f"L{year_int}.csv")
    if not os.path.exists(fp):
        return pd.DataFrame(columns=["time","lon","lat","type"])
    try:
        df = pd.read_csv(fp, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(fp, encoding='big5')

    rename_map = {"Epoch Time":"epoch_sec", "Nanoseconds":"nanosec",
                  "Longitude":"lon", "Latitude":"lat", "Cloud or Ground":"type"}
    for k, v in rename_map.items():
        if k in df.columns:
            df = df.rename(columns={k: v})

    time_s = pd.to_datetime(df.get("epoch_sec", pd.Series(dtype="float")), unit="s", errors="coerce", utc=True)
    if "nanosec" in df.columns:
        time_s = time_s + pd.to_timedelta(pd.to_numeric(df["nanosec"], errors="coerce").fillna(0), unit="ns")

    out = pd.DataFrame({
        "time": time_s,
        "lon":  pd.to_numeric(df.get("lon", pd.Series(dtype="float")), errors="coerce"),
        "lat":  pd.to_numeric(df.get("lat", pd.Series(dtype="float")), errors="coerce"),
        "type": _normalize_type(df.get("type", pd.Series(dtype="object")))
    }).dropna(subset=["lon","lat"])
    return out

def _read_en_one_year_df(year_int, en_root_path_str):
    """
    EN 欄位：
    Time, millisecond, lightning_type, icHeight, lon, lat
    """
    fp = os.path.join(en_root_path_str, f"lightning_{year_int}.txt")
    # print(f"Reading EN file: {fp}")
    if not os.path.exists(fp):
        return pd.DataFrame(columns=["time","lon","lat","type"])
    try:
        df = pd.read_csv(fp)

    except:
        df = pd.read_csv(fp, sep=r"[\s,]+", engine="python")
    # print(df)   
    for k in ["Time","millisecond","lightning_type","lon","lat"]:
        if k not in df.columns:
            df[k] = pd.NA
    df = df.rename(columns={"Time":"time_base", "millisecond":"ms", "lightning_type":"type"})

    time_s = pd.to_datetime(df["time_base"], errors="coerce", utc=True)
    time_s = time_s + pd.to_timedelta(pd.to_numeric(df["ms"], errors="coerce").fillna(0), unit="ms")

    out = pd.DataFrame({
        "time": time_s,
        "lon":  pd.to_numeric(df["lon"], errors="coerce"),
        "lat":  pd.to_numeric(df["lat"], errors="coerce"),
        "type": _normalize_type(df["type"])
    }).dropna(subset=["lon","lat"])
    return out


def _read_tlds_one_year_df(year_int, tlds_root_path_str):
    """
    TLDS 欄位（常見）：
    日期時間, 奈秒, 經度, 緯度, 電流強度(kA), 雷擊型態
    """
    year_int = int(year_int)  # 型別保險
    year_folder_path_str = os.path.join(tlds_root_path_str, f"{year_int:04d}")
    if not os.path.isdir(year_folder_path_str):
        return pd.DataFrame(columns=["time","lon","lat","type"])  # 年度資料夾不存在就回空表

    ## 同時抓該年 .txt 與 .csv；要求檔名以 YYYY 開頭
    if year_int == 2015:
        file_name_list = sorted([
            fn for fn in os.listdir(year_folder_path_str)
            if fn.startswith(f"HISTORY_{year_int:04d}") and (fn.endswith(".txt") or fn.endswith(".csv"))
        ])        
    else:
        file_name_list = sorted([
            fn for fn in os.listdir(year_folder_path_str)
            if fn.startswith(f"{year_int:04d}") and (fn.endswith(".txt") or fn.endswith(".csv"))
        ])
    

    if not file_name_list:
        return pd.DataFrame(columns=["time","lon","lat","type"])  # 沒檔案回空表

    dfs_list = []
    for file_name_str in file_name_list:
        file_path_str = os.path.join(year_folder_path_str, file_name_str)

        ## 先用 UTF-8，失敗才退 BIG5
        if year_int in [2016, 2017]: 
            try:
                df = pd.read_csv(file_path_str, encoding='utf-8',header=None)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path_str, encoding='big5',header=None)
            df.columns = ["日期時間", "奈秒", "緯度", "經度", "不知道這是三小(也不在乎)","雷擊型態"]

        else:
            try:
                df = pd.read_csv(file_path_str, encoding='utf-8',header=0)
            except UnicodeDecodeError:
                df = pd.read_csv(file_path_str, encoding='big5',header=0)
        
        ## 欄名清理：移除 BOM 與首尾空白
        df.columns = df.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip()

        # [修正] 確保必要欄位存在 (避免用 or 連接 list 造成的邏輯無效)
        # 檢查是否存在 '雷擊型態' 或 '類型'
        type_col_name = "雷擊型態" if "雷擊型態" in df.columns else ("類型" if "類型" in df.columns else None)
        
        # 簡單補齊其他欄位
        for col in ["日期時間", "奈秒", "經度", "緯度"]:
            if col not in df.columns:
                df[col] = pd.NA

        if type_col_name is None:
            # 如果連類型欄位都找不到，建一個空的並給 NA
            df["雷擊型態"] = pd.NA
            type_col_name = "雷擊型態"

        ## 時間處理
        time_series = pd.to_datetime(df["日期時間"], errors="coerce", utc=True)
        if "奈秒" in df.columns:
            time_series = time_series + pd.to_timedelta(pd.to_numeric(df["奈秒"], errors="coerce").fillna(0), unit="ns")
        
        ## 數值轉型與標準化
        raw_type_col = df[type_col_name]
        
        # 判斷經緯度是否顛倒
        lat_mean = pd.to_numeric(df["緯度"], errors="coerce").mean()
        lon_mean = pd.to_numeric(df["經度"], errors="coerce").mean()
        
        # 假設經度應該在 100 以上 (台灣約 120)，緯度約 23
        # 如果 "經度" 的平均值比 "緯度" 小，很可能標題反了
        if (not pd.isna(lon_mean) and not pd.isna(lat_mean)) and (lon_mean < lat_mean):
            tmp_df = pd.DataFrame({  
                "time": time_series,
                "lon":  pd.to_numeric(df["緯度"], errors="coerce"), # 標題寫緯度但其實是經度
                "lat":  pd.to_numeric(df["經度"], errors="coerce"), # 標題寫經度但其實是緯度
                "type": _normalize_type(raw_type_col)
            }).dropna(subset=["lon","lat"]) 
        else:
            tmp_df = pd.DataFrame({
                "time": time_series,
                "lon":  pd.to_numeric(df["經度"], errors="coerce"),
                "lat":  pd.to_numeric(df["緯度"], errors="coerce"),
                "type": _normalize_type(raw_type_col)
            }).dropna(subset=["lon","lat"]) 
        
        if not tmp_df.empty:
            dfs_list.append(tmp_df)

    if not dfs_list:
        return pd.DataFrame(columns=["time","lon","lat","type"])
      
    return pd.concat(dfs_list, ignore_index=True)


def _concat_years_df(years_list, reader_func, root_path_str):
    out = pd.DataFrame(columns=["time","lon","lat","type"])
    for y in years_list:
        new_data = reader_func(y, root_path_str)
    
        if not new_data.empty:
            if out.empty:
                out = new_data
            else:
                out = pd.concat([out, new_data], ignore_index=True)
    return out

## ============================== 主函式（單一來源、無 ALL） ============================== ##
def compute_counts_by_source(data_source, years_list, county_shp_path, paths_dict, output_csv_path=None, debug_print=False):
    if data_source not in {"TLDS","EN","CWA"}:
        raise ValueError("data_source 必須是 {'TLDS','EN','CWA'}（不支援 'ALL'）")

    if not isinstance(years_list, (list, tuple)) or len(years_list) != 1:
        raise ValueError("本函式一次只處理一個年度")

    ## 讀縣市並轉 EPSG:4326
    county_gdf = gpd.read_file(county_shp_path)
    if county_gdf.crs is None:
        raise ValueError("縣市圖層沒有 CRS")
    if str(county_gdf.crs).upper() not in ("EPSG:4326","WGS84"):
        county_gdf = county_gdf.to_crs(epsg=4326)
    county_name_col = "COUNTYNAME"

    ## 只讀取你選的來源
    if data_source == "CWA":
        pts_df = _concat_years_df(years_list, _read_cwa_one_year_df,  paths_dict["CWA"])
    elif data_source == "EN":
        pts_df = _concat_years_df(years_list, _read_en_one_year_df,   paths_dict["EN"])
    elif data_source == "TLDS":  
        pts_df = _concat_years_df(years_list, _read_tlds_one_year_df, paths_dict["TLDS"])
    else:
        raise ValueError("不支援的 data_source")
    
    ## 轉 GeoDataFrame
    if pts_df.empty:
        pts_gdf = gpd.GeoDataFrame(columns=["time","lon","lat","type","geometry"], crs="EPSG:4326")
    else:
        pts_gdf = gpd.GeoDataFrame(pts_df, geometry=gpd.points_from_xy(pts_df["lon"], pts_df["lat"]), crs="EPSG:4326")
    
    ## 統計
    if pts_gdf.empty:
        # 修正：空資料時也要確保有 IC 和 CG 欄位，避免後續讀取錯誤
        result_df = county_gdf[["COUNTYNAME"]].copy()
        result_df["IC"] = 0
        result_df["CG"] = 0
        result_df[data_source] = 0 # 保留原本邏輯
    else:
        joined = gpd.sjoin(pts_gdf, county_gdf[["COUNTYNAME","geometry"]], how="inner", predicate="within")
        
        out = joined.groupby(["COUNTYNAME", "type"]).size().reset_index(name="count")
        
        # [修正] Pivot 可能產生 NaN，需補 0
        result_df = out.pivot(index='COUNTYNAME', columns='type', values='count').reset_index()
        
        # [修正] 確保 IC 和 CG 欄位一定存在 (若當年無 CG，Pivot 後就不會有 CG 欄位，會導致 Key Error)
        for col in ['IC', 'CG']:
            if col not in result_df.columns:
                result_df[col] = 0
                
        # [修正] 填充 NaN 為 0 後再轉 int
        result_df = result_df.fillna(0)
        result_df[['IC','CG']] = result_df[['IC','CG']].astype(int)

    # Debug 印表（檢查用）
    if debug_print:
        print(f"\n===== {data_source} 各縣市閃電量 =====")
        print(result_df.to_string(index=False))

    ## 輸出 CSV
    if output_csv_path:
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        result_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

    return result_df, county_gdf, county_name_col

## ============================== 範例呼叫（單一來源） ============================== ##
if __name__ == "__main__":
    county_shp_path = r"/home/steven/python_data/2025CWA_flash_plan/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    paths_dict = {
        "TLDS": r"/home/steven/python_data/2025CWA_flash_plan/raw_data/flash/TLDS",
        "EN":   r"/home/steven/python_data/2025CWA_flash_plan/raw_data/flash/EN",
        "CWA":  r"/home/steven/python_data/2025CWA_flash_plan/raw_data/flash/CWA",
    }

    import sys
    year_int = sys.argv[1] if len(sys.argv) > 1 else 2015
    source = sys.argv[2] if len(sys.argv) > 2 else "CWA"  # {"TLDS","EN","CWA"}
    # 組 years_list（僅一個年份）
    years_list = [int(year_int)]

    # 輸出：.../flash_data/{年}_{source}.csv
    result_csv_dir_path = r"/home/steven/python_data/2025CWA_flash_plan/city_counts"
    result_csv_path = os.path.join(result_csv_dir_path, f"{year_int}_{source}.csv")
    os.makedirs(result_csv_dir_path, exist_ok=True)

    # 執行
    result_df, county_gdf, county_name_col = compute_counts_by_source(
        data_source=source,
        years_list=years_list,
        county_shp_path=county_shp_path,
        paths_dict=paths_dict,
        output_csv_path=result_csv_path,
        debug_print=True,
    )