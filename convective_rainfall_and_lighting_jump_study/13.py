"""
畫雨量圖+閃電分布圖
"""

import os
import pandas as pd
from glob import glob

year = '2021'
month = '05'


data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"
station_data_path = f"{data_top_path}/rain_data/station_data/{year}_{month}.csv"
rain_data_path = f"/{data_top_path}/rain_data/rainfall_data/{year}/{month}/"



