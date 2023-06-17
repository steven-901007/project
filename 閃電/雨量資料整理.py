import pandas as pd

file = "C:/Users/steven.LAPTOP-8A1BDJC6/OneDrive/桌面/筆電py/閃電/rawdata/2021_rain_10mn_10mm.txt" #筆電
file_1 = "C:/Users/steven.LAPTOP-8A1BDJC6/OneDrive/桌面/筆電py/閃電/needinformation/2021_rain_10mn_10mm.csv" #筆電
# file = "C:/Users/steve/Desktop/python相關資料/閃電/rawdata/2021_rain_10mn_10mm.txt" #桌電
# file_1 = "C:/Users/steve/Desktop/python相關資料/閃電/needinformation/2021_rain_10mn_10mm.csv" #桌電
data = []
with open(file,encoding='BIG5',errors='replace') as file: 
    lines = file.readlines() 

    data = [line.strip().split() for line in lines] 


# print(data)

data =  pd.DataFrame(data[1:],columns=data[0]).to_csv(file_1,encoding='BIG5')

file.close()