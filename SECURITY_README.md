# 🔐 LME Dashboard 安全設定說明

## 密碼管理

### 密碼哈希生成
系統使用 SHA256 哈希算法儲存密碼，確保密碼安全性。

#### 使用 generate_password_hash.py
```bash
python generate_password_hash.py
```

#### 手動生成哈希
```python
import hashlib

def create_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 範例
password = "your_password"
hash_value = create_password_hash(password)
print(f"密碼: {password}")
print(f"哈希: {hash_value}")
```

### 環境變數設定
在 `.env` 檔案中設定密碼哈希：

```env
# 密碼哈希設定
DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
ADMIN_PASSWORD_HASH=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918

# 登入安全設定
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

### 預設密碼
- **一般用戶**: `password`
- **管理員**: `admin`

## 權限控制

### 用戶權限
- **一般用戶**: 可訪問基本功能（即時報價、前日收盤、線上計算機）
- **管理員**: 可訪問所有功能（包括數據分析、系統設定、使用說明）

### 安全機制
1. **密碼驗證**: 使用 SHA256 哈希驗證
2. **登入嘗試限制**: 防止暴力破解
3. **會話管理**: 自動登出和會話清理
4. **權限檢查**: 服務器端權限驗證

## 安全最佳實踐

### 密碼安全
- 使用強密碼（至少8個字符）
- 包含大小寫字母、數字和符號
- 定期更改密碼
- 不要在公共場所輸入密碼

### 系統安全
- 定期更新系統
- 監控登入活動
- 備份重要數據
- 使用 HTTPS 連接

### 環境安全
- 保護 `.env` 檔案
- 不要將密碼哈希提交到版本控制
- 定期檢查系統日誌
- 限制管理員權限

## 故障排除

### 常見問題
1. **密碼驗證失敗**
   - 檢查 `.env` 檔案是否存在
   - 確認密碼哈希是否正確
   - 檢查環境變數是否載入

2. **權限問題**
   - 確認用戶是否為管理員
   - 檢查會話狀態
   - 重新登入

3. **環境變數問題**
   - 確認 `.env` 檔案格式正確
   - 檢查檔案編碼（UTF-8）
   - 重新啟動應用程式

### 緊急處理
如果遇到安全問題：
1. 立即更改所有密碼
2. 檢查系統日誌
3. 暫停可疑帳戶
4. 聯繫系統管理員

## 技術細節

### 認證流程
1. 用戶輸入密碼
2. 系統生成 SHA256 哈希
3. 與儲存的哈希比對
4. 驗證成功後建立會話

### 權限檢查
```python
def is_admin():
    """檢查是否為管理員"""
    if 'admin_logged_in' in st.session_state:
        return st.session_state.admin_logged_in
    return False
```

### 會話管理
```python
def logout():
    """登出用戶"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
```

---

**注意**: 此文件包含敏感資訊，請妥善保管，不要分享給未授權人員。
