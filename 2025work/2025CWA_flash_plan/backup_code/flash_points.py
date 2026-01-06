# -*- coding: utf-8 -*-
"""
組裝散點：回傳 [lon_list, lat_list]
get_lightning_points(data_source, years_list, paths_dict)
data_source ∈ {"TLDS","EN","CWA"}
"""

import os, glob
import pandas as pd

def _read_cwa_one_year_lonlat(year_int, cwa_root_path_str):
    fp = os.path.join(cwa_root_path_str, f"L{year_int}.csv")
    if not os.path.exists(fp):
        return pd.DataFrame(columns=["lon","lat"])
    # 僅讀需要欄位（若不存在也不會報錯）
    try:
        df = pd.read_csv(fp, encoding="utf-8", usecols=["Longitude", "Latitude"])
        lon_col, lat_col = "Longitude", "Latitude"
    except Exception:
        # 欄位名容錯（去空白、轉小寫）
        df = pd.read_csv(fp, encoding="utf-8")
        df.columns = df.columns.astype(str).str.strip()
        cols_lower = {c.lower(): c for c in df.columns}
        lon_col = cols_lower.get("longitude")
        lat_col = cols_lower.get("latitude")
        if lon_col is None or lat_col is None:
            # 找不到就補空欄，回空 df
            return pd.DataFrame(columns=["lon","lat"])

    out = pd.DataFrame({
        "lon": pd.to_numeric(df[lon_col], errors="coerce"),
        "lat": pd.to_numeric(df[lat_col],  errors="coerce"),
    }).dropna(subset=["lon","lat"])
    return out

def _read_en_one_year_lonlat(year_int, en_root_path_str):
    fp = os.path.join(en_root_path_str, f"lighting_{year_int}.txt")
    if not os.path.exists(fp):
        return pd.DataFrame(columns=["lon","lat"])
    try:
        df = pd.read_csv(fp)
    except:
        df = pd.read_csv(fp, sep=r"[\s,]+", engine="python")

    # 允許 Lon/Lat 或 lon/lat
    if "lon" in df.columns and "lat" in df.columns:
        lon_col, lat_col = "lon", "lat"
    elif "Lon" in df.columns and "Lat" in df.columns:
        lon_col, lat_col = "Lon", "Lat"
    else:
        # 最後再用小寫比對一遍
        df.columns = df.columns.astype(str).str.strip()
        cols_lower = {c.lower(): c for c in df.columns}
        lon_col = cols_lower.get("lon")
        lat_col = cols_lower.get("lat")
        if lon_col is None or lat_col is None:
            return pd.DataFrame(columns=["lon","lat"])

    out = pd.DataFrame({
        "lon": pd.to_numeric(df[lon_col], errors="coerce"),
        "lat": pd.to_numeric(df[lat_col], errors="coerce"),
    }).dropna(subset=["lon","lat"])
    return out

def _read_tlds_one_year_lonlat(year_int, tlds_root_path_str):
    year_folder = os.path.join(tlds_root_path_str, f"{year_int:04d}")
    pattern = os.path.join(year_folder, f"{year_int:04d}" + "*.txt")  # 例如 201801.txt, 201812.txt
    file_list = sorted(glob.glob(pattern))
    dfs = []
    for fp in file_list:
        try:
            df = pd.read_csv(fp, encoding="utf-8")
        except:
            df = pd.read_csv(fp, sep=r"[\s,]+", engine="python")
        # 預期中文欄位
        if "經度" not in df.columns or "緯度" not in df.columns:
            # 容錯：清理欄名（萬一有空白）
            df.columns = df.columns.astype(str).str.strip()
            if "經度" not in df.columns or "緯度" not in df.columns:
                continue  # 這個月檔案欄位對不上就跳過

        tmp = pd.DataFrame({
            "lon": pd.to_numeric(df["經度"], errors="coerce"),
            "lat": pd.to_numeric(df["緯度"], errors="coerce"),
        }).dropna(subset=["lon","lat"])
        dfs.append(tmp)

    if not dfs:
        return pd.DataFrame(columns=["lon","lat"])
    return pd.concat(dfs, ignore_index=True)

def _concat_years(years_list, reader_func, root_path_str):
    ## 只收集非空 df 再一次 concat，避免 FutureWarning
    dfs = []
    for y in years_list:
        tmp = reader_func(y, root_path_str)
        if isinstance(tmp, pd.DataFrame) and not tmp.empty:
            # 確保欄位型態穩定
            if "lon" in tmp.columns and "lat" in tmp.columns:
                tmp["lon"] = pd.to_numeric(tmp["lon"], errors="coerce")
                tmp["lat"] = pd.to_numeric(tmp["lat"], errors="coerce")
                tmp = tmp.dropna(subset=["lon","lat"])
                dfs.append(tmp[["lon","lat"]])
    if not dfs:
        return pd.DataFrame(columns=["lon","lat"])
    return pd.concat(dfs, ignore_index=True)


def get_lightning_points(data_source, years_list, paths_dict):
    """
    回傳 [lon_list, lat_list]（只針對單一 data_source）
    data_source ∈ {"TLDS","EN","CWA"}
    """
    if data_source == "CWA":
        df = _concat_years(years_list, _read_cwa_one_year_lonlat, paths_dict["CWA"])
    elif data_source == "EN":
        df = _concat_years(years_list, _read_en_one_year_lonlat, paths_dict["EN"])
    elif data_source == "TLDS":
        df = _concat_years(years_list, _read_tlds_one_year_lonlat, paths_dict["TLDS"])
    else:
        raise ValueError("data_source 必須是 {'TLDS','EN','CWA'}")

    # 確保欄位存在（防止空 df 無欄位導致 KeyError）
    if "lon" not in df.columns or "lat" not in df.columns:
        return [[], []]

    return [df["lon"].tolist(), df["lat"].tolist()]
