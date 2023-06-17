import numpy as np
import pandas as pd
file = "C:/Users/steven.LAPTOP-8A1BDJC6/Downloads/新增 文字文件.txt"

data = []
with open(file,encoding='utf-8',errors='replace') as file:
    lines = file.readlines()
    data = [line.strip().split('\t') for idx, line in enumerate(lines) if idx > 0]
    # print(data)

# print(data)
df = []
for i in range(len(data)):
    data[i][6] = data[i][6].replace(',',"")
    data[i][6] = data[i][6].replace('%','')
    df.append(float(data[i][6])*0.01)
    # print(data[i][6])

    # df.append(float(data[i][46][:1]))

df = pd.DataFrame(df)[0]
# print(df)

M = str(round(round(df.mean(),5)*100,3)) #平均數(預期收益)
# print(M)
S = str(round(df.std(),3)) #標準差(預期風險)
# print(S)

# print('平均數(預期收益)'+M+'%\n標準差(預期風險)'+S)
print(M+'%',S)