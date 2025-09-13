import pyart


data_top_path = "C:/Users/steve/python_data/radar"
year = '2024'
month = '05'
day = '23'
hh = '08'
mm = '02'
ss = '00'
station = 'RCWF'


## === 讀取雷達檔案 ===
file_path = f"{data_top_path}/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL" 
radar = pyart.io.read(file_path)

## 取得所有 field 名稱
field_names = radar.fields.keys()

## 印出所有 fields 的資訊
print("## 雷達變數（fields）清單與說明 ##")
for field_name in field_names:
    field = radar.fields[field_name]
    print(f"\n變數名稱 (field): {field_name}")
    print(f"  ▸ long_name    : {field.get('long_name', 'N/A')}")
    print(f"  ▸ units        : {field.get('units', 'N/A')}")
    print(f"  ▸ valid_range  : {field.get('valid_min', 'N/A')} ~ {field.get('valid_max', 'N/A')}")
    print(f"  ▸ shape        : {field['data'].shape}")
    print(f"  ▸ fill_value   : {field.get('_FillValue', 'N/A')}")
    print(f"  ▸ standard_name: {field.get('standard_name', 'N/A')}")
