import numpy as np
import pandas as pd
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties, fontManager

data_top_path = "/home/steven/python_data/2025CWA_flash_plan"
data_paths = f"{data_top_path}/city_counts"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

font_path = f'{data_top_path}/msjh.ttc'
# 1. 將字型檔案加入 Matplotlib 的字型庫
fontManager.addfont(font_path)
# 2. 取得該字型的名稱並設為預設 font.family
prop = FontProperties(fname=font_path)
plt.rcParams['font.family'] = prop.get_name()
# 字型設定
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=18)

gdf = gpd.read_file(county_shp_path)
gdf_proj = gdf.to_crs(epsg=3826)
gdf_proj['area_km2'] = gdf_proj.area / 10**6
area_map = gdf_proj[['COUNTYNAME', 'area_km2']]

# 2. 合併縣市資料 (取數值平均) 並加入 DataFrame
def create_merged_row(df, target_name, source_names):
    subset = df[df['COUNTYNAME'].isin(source_names)]
    if not subset.empty:
        new_row = subset.sum(numeric_only=True)
        new_row['COUNTYNAME'] = target_name
        return pd.DataFrame([new_row])
    return pd.DataFrame()

# 3. 指定排序順序與名稱對照
sort_order = ['新北', '臺北', '基隆', '桃園', '新竹', '苗栗', '臺中', '彰化', 
              '南投', '雲林', '嘉義', '台南', '高雄', '屏東', '宜蘭', '花蓮', '臺東']

# 建立對照表 (原始名稱 -> 排序用簡稱)
# 未在對照表中的名稱 (如原始的新竹市/縣、嘉義市/縣) 會在映射後變為 NaN 並被濾除
name_map = {
    '新北市': '新北', '臺北市': '臺北', '基隆市': '基隆', '桃園市': '桃園',
    '新竹': '新竹', '苗栗縣': '苗栗', '臺中市': '臺中', '彰化縣': '彰化',
    '南投縣': '南投', '雲林縣': '雲林', '嘉義': '嘉義', '臺南市': '台南',
    '高雄市': '高雄', '屏東縣': '屏東', '宜蘭縣': '宜蘭', '花蓮縣': '花蓮',
    '臺東縣': '臺東'
}

for source in ['CWA', 'EN', 'TLDS']:
    for ic_or_cg in ['IC', 'CG', 'all']:
        ##決定色系
        if ic_or_cg == 'IC':
            c = "Blues"
        elif ic_or_cg == 'CG':
            c = "Reds"
        elif ic_or_cg == 'all':
            c = "Greens"

        density_df = pd.DataFrame()
        count_df = pd.DataFrame()
        
        for year in range(2015, 2025):
            data_path = f'{data_paths}/{year}_{source}.csv'

            if os.path.exists(data_path) is True:
                df = pd.read_csv(data_path)
                df = pd.merge(df, area_map, on='COUNTYNAME', how='left')
                df = df[~df['COUNTYNAME'].isin(['澎湖縣', '連江縣', '金門縣'])].copy()
                df = pd.concat([
                    df,
                    create_merged_row(df, '新竹', ['新竹市', '新竹縣']),
                    create_merged_row(df, '嘉義', ['嘉義市', '嘉義縣'])
                ], ignore_index=True)
                df['all'] = df['IC'] + df['CG']
                
                df['IC_density'] = df['IC'] / df['area_km2']
                df['CG_density'] = df['CG'] / df['area_km2']
                df['all_density'] = df['all'] / df['area_km2']

                new_col_name = year

                # 處理 Density
                density_target_col = f'{ic_or_cg}_density'
                df_copy = df.rename(columns={density_target_col: new_col_name})
                density_need_df = df_copy[['COUNTYNAME', new_col_name]].copy()
                
                if density_df.empty:
                    density_df = density_need_df
                else:
                    density_df = pd.merge(density_df, density_need_df, on='COUNTYNAME', how='outer')

                # 處理 Count
                count_target_col = ic_or_cg
                df_copy = df.rename(columns={count_target_col: new_col_name})
                count_need_df = df_copy[['COUNTYNAME', new_col_name]].copy()
                
                if count_df.empty:
                    count_df = count_need_df
                else:
                    count_df = pd.merge(count_df, count_need_df, on='COUNTYNAME', how='outer')


# [修改] 直接替換名稱、過濾、並排序
        # 1. 將 COUNTYNAME 替換為簡稱 (例如: 新北市 -> 新北)
        density_df['COUNTYNAME'] = density_df['COUNTYNAME'].map(name_map)
        # 2. 移除 NaN (不在 map 中的舊名稱)
        density_df = density_df.dropna(subset=['COUNTYNAME'])
        # 3. 設定排序順序
        density_df['COUNTYNAME'] = pd.Categorical(density_df['COUNTYNAME'], categories=sort_order, ordered=True)
        density_df = density_df.sort_values('COUNTYNAME').reset_index(drop=True)

        # Count DF 同理處理
        count_df['COUNTYNAME'] = count_df['COUNTYNAME'].map(name_map)
        count_df = count_df.dropna(subset=['COUNTYNAME'])
        count_df['COUNTYNAME'] = pd.Categorical(count_df['COUNTYNAME'], categories=sort_order, ordered=True)
        count_df = count_df.sort_values('COUNTYNAME').reset_index(drop=True)



        # 複製原始 DataFrame 以保持結構
        ratio_df = density_df.copy()
        # 定義年份欄位 (排除 COUNTYNAME)
        year_cols = density_df.columns.drop('COUNTYNAME')
        # 計算每年的總次數 (Column-wise sum)
        yearly_sums = density_df[year_cols].sum()
        # 將各數值除以該年份的總和，計算比例
        ratio_df[year_cols] = density_df[year_cols].div(yearly_sums, axis=1)

        # 若需要百分比格式，可取消註解下一行
        ratio_df[year_cols] = ratio_df[year_cols] * 100

        print(ratio_df)
        
        print(f"--- Result for {source} {ic_or_cg} ---")
        # print(count_df)
        print(density_df)


            
        # [修改] 繪圖邏輯：顏色=Density, 數字=Count
        if not density_df.empty and not count_df.empty:
            
            # 建立儲存路徑 (防止報錯)
            save_dir = f"{data_top_path}/result/flash_pattern_draw/count_area/{source}"
            os.makedirs(save_dir, exist_ok=True)

            plt.figure(figsize=(12, 10))
            
            # 1. 準備顏色資料 (Density)
            plot_data = density_df.set_index('COUNTYNAME')
            cols = sorted(plot_data.columns) # 確保年份排序
            plot_data = plot_data[cols]

            # [新增] 計算 vmax: 找比 max 大的最小 10 的倍數
            max_val = plot_data.max().max()
            if pd.isna(max_val):
                vmax_val = 10
            else:
                vmax_val = (int(max_val) // 10 + 1) * 10

            # 2. 準備文字資料 (Count) - 必須與 plot_data 形狀和順序完全一致
            annot_data = ratio_df.set_index('COUNTYNAME')
            annot_data = annot_data[cols] 

            # 3. 繪製熱力圖
            # [修改] 加入 vmax 參數



            ax = sns.heatmap(
                plot_data, 
                cmap=c, 
                annot=annot_data, 
                fmt=".0f",  # 標註：新增此參數以顯示整數
                linecolor='gray', 
                linewidths=.5, 
                vmax=vmax_val,
                cbar_kws={'pad': 0.01}  # 標註：新增此參數調整距離
            )
            


            for ys in [3,6,9,14]:
                ax.axhline(y=ys, color='black', linewidth=3)
            
            # 強制設定軸標籤字型
            plt.yticks(fontproperties=myfont, rotation=0)
            plt.ylabel(None)
            # 取得 heatmap 自動生成的 colorbar 物件
            cbar = ax.collections[0].colorbar
            # 設定 Colorbar 標籤文字 (例如：閃電密度)
            cbar.set_label('閃電密度 (次/km²)', fontproperties=myfont)
            # 設定刻度字型 (確保刻度數字正確顯示)
            cbar.ax.tick_params(labelsize=10)

            if ic_or_cg == 'all':
                plt.title(f'Density Hotmap: {source}  (IC+CG) 文字 = 該年縣市占比', fontproperties=title_font)
            else:
                plt.title(f'Density Hotmap: {source}  ({ic_or_cg}) 文字 = 該年縣市占比', fontproperties=title_font)
            plt.tight_layout()

            # 存檔
            save_img_path = f"{save_dir}/heatmap_{source}_{ic_or_cg}.png"
            plt.savefig(save_img_path)
            plt.close()

            save_cont_excel = f"{save_dir}/{source}_{ic_or_cg}.xlsx"
            count_df.to_excel(save_cont_excel,index=None)

            print(f"Saved heatmap to {save_img_path}")