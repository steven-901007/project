import mysql.connector as mysql
import paramiko # 新增：用於遠端 SSH 連線
import os

# --- 設定區 (改用 os.getenv 讀取) ---
SSH_HOST = os.getenv("SSH_HOST")
SSH_PORT = 22
SSH_USER = os.getenv("SSH_USER")
SSH_PASS = os.getenv("SSH_PASS")
REMOTE_FILE_PATH = "/tmp/data.txt"

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": 3306,
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"), # 這裡不再顯示明碼
}

# --- 程式主邏輯 ---
try:
    # 1. 連線到遠端 Linux (SSH)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS)
    
    # 開啟 SFTP 通道 (用於檔案傳輸)
    sftp = ssh.open_sftp()
    print(f"已連線至遠端伺服器：{SSH_HOST}")

    # 2. 讀取遠端檔案內容
    try:
        with sftp.open(REMOTE_FILE_PATH, 'r') as remote_file:
            file_content = remote_file.read().decode('utf-8') # 讀取並解碼
            print("成功讀取遠端資料。")

            # 3. 連線 MySQL 並寫入
            conn = mysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute('CREATE DATABASE IF NOT EXISTS rain_data')
            cursor.execute('USE rain_data')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute("INSERT INTO logs (content) VALUES (%s)", (file_content,))
            conn.commit()
            print("資料已寫入 MySQL。")

            # 關閉資料庫連線
            cursor.close()
            conn.close()

        # 4. 刪除遠端檔案 (只有在成功寫入資料庫後才執行)
        sftp.remove(REMOTE_FILE_PATH)
        print(f"遠端檔案 {REMOTE_FILE_PATH} 已刪除。")

    except FileNotFoundError:
        print(f"錯誤：遠端找不到檔案 {REMOTE_FILE_PATH}")
    
    # 關閉 SSH/SFTP 連線
    sftp.close()
    ssh.close()

except Exception as e:
    print(f"發生錯誤：{e}")