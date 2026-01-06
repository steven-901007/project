from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
import random

## === 參數設定（保持你的命名） === ##
driver_path_str = r"C:\Users\Kevin\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # chromedriver位置_str

chrome_options = Options()  # 需要無頭、規避訊息等等再加
# chrome_options.add_argument("--headless=new")  # 無頭模式（可選）

## === 啟動（Selenium 4 正確寫法） === ##
chrome_service = Service(executable_path=driver_path_str)  # 用 Service 傳 driver 路徑
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

## === 進入目標頁 === ##
driver.get("https://my.ntu.edu.tw/mattend/ssi.aspx")  # 目標頁面

## 1) 點擊「登入」：等待元素可被點擊再點 ##
enter = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.LINK_TEXT, "登入"))
)
enter.click()  # 點擊滑鼠

## 2) 等待帳號欄位出現，然後填寫 ##
element = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.NAME, "user"))
)
time.sleep(random.randint(5,100)/100)  # 保留你的隨機停頓

user = driver.find_element(By.NAME, "user")
user.send_keys("stevenwsp")  # << 建議不要硬編碼；先這樣保留
time.sleep(random.randint(5,200)/100)

password = driver.find_element(By.NAME, "pass")
password.send_keys("Wsp970222")  # << 同上
time.sleep(random.randint(5,200)/100)

login_btn = driver.find_element(By.NAME, "Submit")
login_btn.click()

## 3) 等簽到按鈕出現（ID: btSign），再做移動+點擊 ##
chackin = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.ID, "btSign"))
)

actions = ActionChains(driver)

offset_x = random.randint(-5, 5)   # 水平隨機偏移像素
offset_y = random.randint(-3, 3)   # 垂直隨機偏移像素

actions.move_to_element_with_offset(chackin, offset_x, offset_y)
actions.pause(random.uniform(0.3, 0.8))
actions.click()
actions.perform()

time.sleep(5)
driver.quit()  # 需要的時候再關
with open("signin_log.txt", "a", encoding="utf-8") as f:
    f.write("簽到成功\n")