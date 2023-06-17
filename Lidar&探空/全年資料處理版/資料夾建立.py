import os
import time

locate = str(input('地點'))
year = str(input('年分'))

try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/raw data/" + locate)
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/raw data/" + locate + '/' + year)
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate)
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year)
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year + "/1hour")
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year + "/10min")
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year + "/need_information_read")
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year + "/windcut")
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year + "/picture")
except:pass
try:
        os.makedirs("C:/Users/steve/Desktop/python相關資料/need data information/" + locate + "/" +year + "/need_information_set")
except:pass