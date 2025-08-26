"""
LME Dashboard 版本管理
"""

# 版本號格式：主版本.次版本.修訂版本
VERSION = "1.3.0"

# 版本說明
VERSION_INFO = {
    "version": VERSION,
    "release_date": "2024-12-30",
    "features": [
        "LME 即時報價看板",
        "前日收盤數據",
        "線上計算機 (修正 LME 係數計算)",
        "管理員權限系統",
        "數據分析功能",
        "系統設定功能",
        "使用說明文檔",
        "快速測試工具",
        "智能報價系統 (新增)"
    ],
    "latest_changes": [
        "新增智能報價系統",
        "支援買賣雙向報價管理",
        "客戶/供應商管理功能",
        "智能價格建議算法",
        "PDF報價單生成功能",
        "報價成功率分析"
    ]
}

def get_version():
    """獲取版本號"""
    return VERSION

def get_version_info():
    """獲取完整版本資訊"""
    return VERSION_INFO

def get_version_display():
    """獲取版本顯示文字"""
    return f"v{VERSION}" 