import gzip
import glob
import os


locate = '松山'
year = '109'

def un_gf(file_name):
    f_name = file_name.replace(".gz","")
    g_file = gzip.GzipFile(file_name)
    open(f_name,"wb+").write(g_file.read())
    g_file.close()
errorfile = []
result  =glob.glob('C:/Users/steve/Desktop/python相關資料/raw data/'+locate+'/'+year+'/**')
for day in result:
    # print(day)
    files  =glob.glob(day+"/wind_reconstruction_data/*")
    for file in files:
        file = file + '/*.gz'

        result  =glob.glob(file)
        
        for f in result: 
            try:
                print(f)
                un_gf(f)
                os.remove(f)
            except:
                errorfile.append(f)
                os.remove(f[:161])          
print(errorfile)