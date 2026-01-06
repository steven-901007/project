import numpy as np

# ==========================================
# 核心數學工具 (Beta Membership Functions)
# ==========================================

def _beta_function_b1(data, m, a):
    """
    Dolan and Rutledge (2009) Beta 隸屬函數 (b=1)
    公式: beta = 1 / (1 + ((x - m) / a)^2)
    """
    # 避免 a=0 導致除以 0
    a = np.where(a == 0, 1e-6, a)
    return 1.0 / (1.0 + ((data - m) / a)**2)

def _beta_function_b2(data, m, a):
    """
    Dolan and Rutledge (2009) Beta 隸屬函數 (b=2)
    公式: beta = 1 / (1 + ((x - m) / a)^2)^2
    """
    a = np.where(a == 0, 1e-6, a)
    return 1.0 / (1.0 + ((data - m) / a)**2)**2

# ==========================================
# PID Method Dolan and Rutledge 2009
# ==========================================

def pid_method_dolan_2009(Z, Zdr, Kdp, rhohv, T, b_slope=1):
    """
    基於 Dolan and Rutledge (2009) 論文的 X-band 模糊邏輯粒子辨識演算法
    
    參數:
    Z     : Reflectivity (dBZ)
    Zdr   : Differential Reflectivity (dB)
    Kdp   : Specific Differential Phase (deg/km)
    rhohv : Correlation Coefficient (0~1)
    T     : Temperature (Celsius) 無此資料預設為0
    b_slope : 選擇 Beta 函數的斜率 b (1 或 2)
    """
    
    # 選擇使用的 Beta 函數
    beta_func = _beta_function_b2 if b_slope == 2 else _beta_function_b1
    
    ones = np.ones_like(Z)
    
    # 1. 定義類別與 XMBF 參數 (基於 Table 3-9) [cite: 450]
    # 格式: '類別': {'變數': (m, a)}
    # m = (Min + Max) / 2, a = (Max - Min) / 2
    # 溫度參數 m, a 參考論文描述之典型區間
    params = {
        'RN':  {'Z': (42.0, 17.0), 'Zdr': (2.85, 2.75), 'Kdp': (12.75, 12.75), 'rho': (0.99, 0.01),  'T': (15.0, 15.0)},
        'DZ':  {'Z': (2.0, 29.0),  'Zdr': (0.45, 0.45), 'Kdp': (0.03, 0.03),   'rho': (0.9925, 0.0075), 'T': (15.0, 15.0)},
        'AG':  {'Z': (16.0, 17.0), 'Zdr': (0.7, 0.7),   'Kdp': (0.2, 0.2),     'rho': (0.989, 0.011),  'T': (-10.0, 10.0)},
        'CR':  {'Z': (-3.0, 22.0), 'Zdr': (3.2, 2.6),   'Kdp': (0.15, 0.15),   'rho': (0.985, 0.015),  'T': (-15.0, 15.0)},
        'LDG': {'Z': (34.0, 10.0), 'Zdr': (0.3, 1.0),   'Kdp': (0.7, 2.1),     'rho': (0.9925, 0.0075), 'T': (-10.0, 10.0)},
        'HDG': {'Z': (43.0, 11.0), 'Zdr': (1.2, 2.5),   'Kdp': (2.55, 5.05),   'rho': (0.9825, 0.0175), 'T': (-10.0, 10.0)},
        'VI':  {'Z': (3.5, 28.5),  'Zdr': (-0.8, 1.3),  'Kdp': (-0.075, 0.075), 'rho': (0.965, 0.035),  'T': (-15.0, 15.0)}
    }

    # 2. 定義權重 (依據論文 Section 5 描述) 
    # W = [Zh, Zdr, Kdp, rhohv, T]
    weights = [1.5, 0.4, 1.0, 0.2, 0.5]
    
    classes_list = list(params.keys())
    prob_results = {}

    for cls in classes_list:
        p = params[cls]
        
        # 計算各變數的隸屬得分 f(x)
        f_z   = beta_func(Z,     p['Z'][0],   p['Z'][1])
        f_zdr = beta_func(Zdr,   p['Zdr'][0], p['Zdr'][1])
        f_kdp = beta_func(Kdp,   p['Kdp'][0], p['Kdp'][1])
        f_rho = beta_func(rhohv, p['rho'][0], p['rho'][1])
        f_t   = beta_func(T,     p['T'][0],   p['T'][1])
        
        # 3. 計算加權總分 (Aggregation)
        # 公式: Sum(f_i * W_i) / Sum(W_i)
        total_score = (
            f_z * weights[0] + 
            f_zdr * weights[1] + 
            f_kdp * weights[2] + 
            f_rho * weights[3] + 
            f_t * weights[4]
        ) / sum(weights)
        
        prob_results[cls] = total_score
        
    # === 【修正標註：邏輯優化】 ===
    # 將結果堆疊並找出得分最高的粒子類別
    score_stack = np.array([prob_results[cls] for cls in classes_list])
    max_idx = np.argmax(score_stack, axis=0)
    
    classes_array = np.array(classes_list)
    final_labels = classes_array[max_idx]
    
    return final_labels