from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# 首頁：回傳網頁畫面
@app.route('/')
def index():
    return render_template('index.html')

# API：提供資料給前端畫圖
# 前端會呼叫：/api/data?year=2023
@app.route('/api/data')
def get_data():
    year = request.args.get('year') # 抓取前端傳來的年份
    
    conn = sqlite3.connect('rainfall.db')
    c = conn.cursor()
    
    # 搜尋該年份的所有資料
    c.execute("SELECT month, value FROM rain_data WHERE year=? ORDER BY month", (year,))
    rows = c.fetchall()
    conn.close()

    # 整理格式給前端 (Chart.js 需要 list 格式)
    # months = [1, 2, 3...]
    # values = [50, 60, 20...]
    months = [row[0] for row in rows]
    values = [row[1] for row in rows]
    
    return jsonify({'labels': months, 'data': values})

if __name__ == '__main__':
    app.run(debug=True)