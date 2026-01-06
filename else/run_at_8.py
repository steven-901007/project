## 等到下一個 08:00 執行指定指令（單次）
## 方式：
##   - 如果有給命令列參數 (--cmd / --args)，會優先使用
##   - 如果沒給，就用下面 DEFAULT_CMD / DEFAULT_ARGS
## 行為：
##   - 目前時間 < 今天 08:00 → 等到今天 08:00
##   - 目前時間 ≥ 今天 08:00 → 等到明天 08:00
##   - 到點後使用 subprocess.run 執行指令

import argparse
import subprocess
import time
from datetime import datetime, timedelta

## === 預設要執行的程式與參數（可自行修改） === ##
DEFAULT_CMD = r"C:/Users/Kevin/AppData/Local/Programs/Python/Python313/python.exe"
DEFAULT_ARGS = r"C:\Users\Kevin\Desktop\steven\project\else\NTU_signin.py"

def calc_next_8am_dt(now_dt):
    target_dt = now_dt.replace(hour=8, minute=10, second=0, microsecond=0)
    if now_dt >= target_dt:
        target_dt = target_dt + timedelta(days=1)
    return target_dt

def main():
    parser = argparse.ArgumentParser(description="等到下一個 08:00 執行指定指令（單次）")
    parser.add_argument("--cmd", help="要執行的程式路徑")
    parser.add_argument("--args", default="", help="傳給程式的參數（整段字串，可留空）")
    args = parser.parse_args()

    # 如果沒給參數，就用預設值
    cmd = args.cmd if args.cmd else DEFAULT_CMD
    cmd_args = args.args if args.args.strip() else DEFAULT_ARGS

    now_dt = datetime.now()
    run_target_dt = calc_next_8am_dt(now_dt)

    print(f"🕗 目前時間：{now_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ 將在：{run_target_dt.strftime('%Y-%m-%d %H:%M:%S')} 執行")
    print(f"👉 指令：{cmd} {cmd_args}")

    while True:
        now_dt = datetime.now()
        remain_seconds_float = (run_target_dt - now_dt).total_seconds()
        if remain_seconds_float <= 0:
            break
        step_seconds_int = int(min(60, max(1, remain_seconds_float)))
        time.sleep(step_seconds_int)

    print("🚀 到點開始執行...")
    try:
        full_cmd_list = [cmd] + cmd_args.split()
        result = subprocess.run(full_cmd_list, check=False)
        print(f"✅ 指令結束，returncode = {result.returncode}")
    except Exception as e:
        print(f"❌ 執行發生錯誤：{e}")

if __name__ == "__main__":
    main()
