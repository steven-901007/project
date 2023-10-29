import matplotlib.pyplot as plt

# file = "C:/Users/steve/Desktop/python相關資料/田中lidar/data/20230301/Wind_Profile_254_20230301_081607.hpl" #PC
file = "C:/Users/steven.LAPTOP-8A1BDJC6/OneDrive/桌面/code/Python_code/data站存區/Wind_Profile_254_20230301_081607.hpl" #nb
data = []
with open(file,encoding='BIG5',errors='replace') as file: 
    lines = file.readlines() 

    data = [line.strip().split() for line in lines] 


# for i in range(0,100):
#     # if data[i][0] == '666':
#     #     print(1)
#     print(data[i])
max_data_0number = int(data[len(data)-1][0])
need_data_v = []
need_data_SNR = []
need_data_Beta = []
need_data_Spectral_Width = []
for i in range(max_data_0number+1):
    need_data_v.append([])
    need_data_SNR.append([])
    need_data_Beta.append([])
    need_data_Spectral_Width.append([])
    # print(i)
for i in range(len(data)):
    try:
        if float(data[i][0])*10 == round(float(data[i][0]))*10:
            need_data_v[int(data[i][0])].append(float(data[i][1]))
            need_data_SNR[int(data[i][0])].append(float(data[i][2]))
            need_data_Beta[int(data[i][0])].append(float(data[i][3]))
            need_data_Spectral_Width[int(data[i][0])].append(float(data[i][4]))
            # print(data[i])
        # else:
            # print(data[i])
    except:
        # print(data[i])
        pass
# print(min(need_data_Beta[0]))
# print(float(data[999][0]))        
# print(need_data_v) #從0~len(neeed_data_v)
# print(len(need_data_SNR))
#chack
# for i in range(len(need_data_v)):
#     for j in range(len(need_data_v[i])):
#         if len(need_data_v[i]) != 6:
#             print('data_number_error+'+str(i))
#         # if i != int(need_data[i][j]):
#         #     print(i)

# 創建一個新的圖形
fig, ax = plt.subplots()


# 顯示圖形
plt.axis('equal')  # 讓座標軸縮放一致
# plt.show()
