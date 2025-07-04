import wradlib as wrl
import pprint
vol_path = r"C:\Users\steve\python_data\radar\20110417_u.RCCG\2011_0417\2011041700003400dBZ.vol" # 替換成你的路徑




attrs = wrl.io.read_rainbow(vol_path)


import pprint
pprint.pprint(attrs['volume']['scan']['slice'][0]['slicedata'])