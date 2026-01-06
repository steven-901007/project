import numpy as np

# ==========================================
# 核心數學工具 (Math Helpers)
# ==========================================

def _trapezoid_function(data, x1, x2, x3, x4):
    """
    梯形隸屬函數 (Trapezoidal Membership Function)
    對應論文中的 x1, x2, x3, x4 定義
    支援 NumPy Array 的廣播運算 (Broadcasting)
    """
    # 初始化分數陣列，預設為 0
    score = np.zeros_like(data, dtype=np.float32)
    
    # 為了避免除以 0 的錯誤，檢查斜率寬度
    # 左斜坡 (x1 ~ x2)
    left_slope = x2 - x1
    # 右斜坡 (x3 ~ x4)
    right_slope = x4 - x3

    # 1. 區間 [x2, x3]: 機率為 1
    mask_one = (data >= x2) & (data <= x3)
    score[mask_one] = 1.0
    
    # 2. 區間 [x1, x2): 左斜坡上升
    mask_left = (data >= x1) & (data < x2)
    # 使用 np.divide 安全處理除法 (雖然理論上 x2>x1)
    if np.any(left_slope > 0): # 如果是純垂直線則跳過
         score[mask_left] = (data[mask_left] - x1[mask_left]) / left_slope[mask_left]
            
    # 3. 區間 (x3, x4]: 右斜坡下降
    mask_right = (data > x3) & (data <= x4)
    if np.any(right_slope > 0):
        score[mask_right] = (x4[mask_right] - data[mask_right]) / right_slope[mask_right]
        
    return score

# ==========================================
# PID Method Park (Main Function)
# ==========================================

def pid_method_park(Z, Zdr, Kdp, rhohv):
    """
    基於 Park et al. 論文的模糊邏輯粒子辨識演算法
    
    參數:
    Z     : Reflectivity (dBZ)
    Zdr   : Differential Reflectivity (dB)
    Kdp   : Specific Differential Phase (deg/km) -> 內部會轉為 LKdp
    rhohv : Correlation Coefficient (0~1)
    
    回傳:
    prob_results (dict): 各類別的機率分數
    classes (list): 類別名稱列表
    """
    
    # 1. 前處理
    # ------------------------------------------------------------------
    # 處理 LKdp: 論文使用 10*log10(Kdp)。
    # 為了避免 log(0) 或 log(負數)，我們先將 Kdp 小於 0.001 的值設為 0.001
    Kdp_safe = np.where(Kdp < 0.001, 0.001, Kdp)
    LKdp = 10 * np.log10(Kdp_safe)
    
    # 2. 計算動態參數 (Reflectivity-dependent parameters)
    # 參考提供的公式圖片 [image_84e033.png, image_84e04f.png]
    # ------------------------------------------------------------------
    
    # Zdr 的依賴函數 f1, f2, f3
    # f1(Z) = -0.50 + 2.50e-3 Z + 7.50e-4 Z^2
    f1 = -0.50 + (2.50e-3 * Z) + (7.50e-4 * Z**2)
    
    # f2(Z) = 0.68 - 4.81e-2 Z + 2.92e-3 Z^2
    f2 = 0.68 - (4.81e-2 * Z) + (2.92e-3 * Z**2)
    
    # f3(Z) = 1.42 + 6.67e-2 Z + 4.85e-4 Z^2 (注意圖片係數確認)
    f3 = 1.42 + (6.67e-2 * Z) + (4.85e-4 * Z**2)
    
    # LKdp 的依賴函數 g1, g2
    # g1(Z) = -44.0 + 0.8 Z
    g1 = -44.0 + (0.8 * Z)
    
    # g2(Z) = -22.0 + 0.5 Z
    g2 = -22.0 + (0.5 * Z)

    # 為了方便廣播運算，將純量參數擴展成與 Z 相同形狀 (Helper arrays)
    ones = np.ones_like(Z)
    
    # 3. 定義類別與權重 (Table 2)
    # 參考提供的權重圖片 [image_84e072.png]
    # 注意：這裡暫時忽略 SD(Z) 和 SD(PhiDP)，因輸入變數未包含
    # ------------------------------------------------------------------
    classes_list = ['GC/AP', 'BS', 'DS', 'WS', 'CR', 'GR', 'BD', 'RA', 'HR', 'RH']
    
    # 權重格式: [W_Z, W_Zdr, W_rhohv, W_LKdp]
    weights = {
        'GC/AP': [0.2, 0.4, 1.0, 0.0],
        'BS':    [0.4, 0.6, 1.0, 0.0],
        'DS':    [1.0, 0.8, 0.6, 0.0],
        'WS':    [0.6, 0.8, 1.0, 0.0],
        'CR':    [1.0, 0.6, 0.4, 0.5],
        'GR':    [0.8, 1.0, 0.4, 0.0],
        'BD':    [0.8, 1.0, 0.6, 0.0],
        'RA':    [1.0, 0.8, 0.6, 0.0],
        'HR':    [1.0, 0.8, 0.6, 1.0],
        'RH':    [1.0, 0.8, 0.6, 1.0]
    }

    # 4. 定義參數表 (Table 1)
    # 參考提供的參數圖片 [image_84e054.png]
    # 這裡將動態變數直接填入 array
    # ------------------------------------------------------------------
    
    prob_results = {}

    for cls in classes_list:
        W = weights[cls] # 取得權重 [Z, Zdr, rho, LKdp]
        
        # 初始化各變數的分數 P(Xi)
        p_z = np.zeros_like(Z)
        p_zdr = np.zeros_like(Z)
        p_rho = np.zeros_like(Z)
        p_kdp = np.zeros_like(Z)
        
        # --- (A) Reflectivity Z ---
        if cls == 'GC/AP': params = (15, 20, 70, 80)
        elif cls == 'BS':  params = (5, 10, 20, 30)
        elif cls == 'DS':  params = (5, 10, 35, 40)
        elif cls == 'WS':  params = (25, 30, 40, 50)
        elif cls == 'CR':  params = (0, 5, 20, 25)
        elif cls == 'GR':  params = (25, 35, 50, 55)
        elif cls == 'BD':  params = (20, 25, 45, 50)
        elif cls == 'RA':  params = (5, 10, 45, 50)
        elif cls == 'HR':  params = (40, 45, 55, 60)
        elif cls == 'RH':  params = (45, 50, 75, 80)
        else: params = (0,0,0,0)
        
        # 轉換成 array 以符合 shape
        p_z = _trapezoid_function(Z, params[0]*ones, params[1]*ones, params[2]*ones, params[3]*ones)

        # --- (B) ZDR ---
        # 需處理動態邊界 (f1, f2, f3)
        if cls == 'GC/AP': x = (-4, -2, 1, 2)
        elif cls == 'BS':  x = (0, 2, 10, 12)
        elif cls == 'DS':  x = (-0.3, 0.0, 0.3, 0.6)
        elif cls == 'WS':  x = (0.5, 1.0, 2.0, 3.0)
        elif cls == 'CR':  x = (0.1, 0.4, 3.0, 3.3)
        elif cls == 'GR':  x = (-0.3, 0.0, f1, f1 + 0.3) # Dynamic
        elif cls == 'BD':  x = (f2 - 0.3, f2, f3, f3 + 1.0) # Dynamic
        elif cls == 'RA':  x = (f1 - 0.3, f1, f2, f2 + 0.5) # Dynamic
        elif cls == 'HR':  x = (f1 - 0.3, f1, f2, f2 + 0.5) # Dynamic (Same as RA)
        elif cls == 'RH':  x = (-0.3, 0.0, f1, f1 + 0.5) # Dynamic
        else: x = (0,0,0,0)
        
        # 確保 x 的四個元素都是 array
        x_arr = [val if isinstance(val, np.ndarray) else val*ones for val in x]
        p_zdr = _trapezoid_function(Zdr, x_arr[0], x_arr[1], x_arr[2], x_arr[3])

        # --- (C) RhoHV ---
        if cls == 'GC/AP': params = (0.5, 0.6, 0.9, 0.95)
        elif cls == 'BS':  params = (0.3, 0.5, 0.8, 0.83)
        elif cls == 'DS':  params = (0.95, 0.98, 1.00, 1.01)
        elif cls == 'WS':  params = (0.88, 0.92, 0.95, 0.985)
        elif cls == 'CR':  params = (0.95, 0.98, 1.00, 1.01)
        elif cls == 'GR':  params = (0.90, 0.97, 1.00, 1.01)
        elif cls == 'BD':  params = (0.92, 0.95, 1.00, 1.01)
        elif cls == 'RA':  params = (0.95, 0.97, 1.00, 1.01)
        elif cls == 'HR':  params = (0.92, 0.95, 1.00, 1.01)
        elif cls == 'RH':  params = (0.85, 0.90, 1.00, 1.01)
        else: params = (0,0,0,0)
        
        p_rho = _trapezoid_function(rhohv, params[0]*ones, params[1]*ones, params[2]*ones, params[3]*ones)
        
        # --- (D) LKdp (Need Log Kdp) ---
        # 需處理動態邊界 (g1, g2)
        if cls == 'GC/AP': x = (-30, -25, 10, 20)
        elif cls == 'BS':  x = (-30, -25, 10, 10) # Typo in table? Img says 10, 10. Let's trust img.
        elif cls == 'DS':  x = (-30, -25, 10, 20)
        elif cls == 'WS':  x = (-30, -25, 10, 20)
        elif cls == 'CR':  x = (-5, 0, 10, 15)
        elif cls == 'GR':  x = (-30, -25, 10, 20)
        elif cls == 'BD':  x = (g1 - 1, g1, g2, g2 + 1) # Dynamic
        elif cls == 'RA':  x = (g1 - 1, g1, g2, g2 + 1) # Dynamic
        elif cls == 'HR':  x = (g1 - 1, g1, g2, g2 + 1) # Dynamic
        elif cls == 'RH':  x = (-10, -4, g1, g1 + 1) # Dynamic
        else: x = (0,0,0,0)

        x_arr = [val if isinstance(val, np.ndarray) else val*ones for val in x]
        p_kdp = _trapezoid_function(LKdp, x_arr[0], x_arr[1], x_arr[2], x_arr[3])

        # 5. 計算加權總分 (Aggregation)
        # Formula: Total = sum(P_i * W_i) / sum(W_i)
        # 這裡我們計算 Weighted Sum，如同你之前要求的。
        # 如果需要正規化到 0~1，最後再除以權重總和即可。
        # 這裡根據你的指示 "相加的方式是對的"，直接加權相加。
        
        total_score = (
            p_z * W[0] + 
            p_zdr * W[1] + 
            p_rho * W[2] + 
            p_kdp * W[3]
        )
        
        # 將結果存入字典
        prob_results[cls] = total_score
        
    return prob_results, classes_list