import pandas as pd

nb = 6235

path = "C:/Users/steve/Downloads/"+str(nb)+"_history.csv"

df = pd.read_csv(path,encoding = 'utf-8')
# print(df)
df['day'] = df['Date'].str[8:10]
# print(df)

# df.to_csv(path)