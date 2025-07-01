# 🔐 LME Dashboard 安全系統

## 安全改進

相比原來的簡單密碼保護，新的安全系統提供了以下改進：

### 原來的問題
1. **密碼明文存儲** - 密碼直接寫在代碼中
2. **客戶端驗證** - 容易被繞過
3. **無防暴力破解** - 可以無限次嘗試密碼
4. **會話狀態不安全** - 容易被篡改

### 新的安全特性
1. **密碼哈希存儲** - 使用 SHA256 哈希存儲密碼
2. **環境變數配置** - 密碼不寫在代碼中
3. **防暴力破解** - 限制登入嘗試次數
4. **帳戶鎖定** - 超過嘗試次數後鎖定帳戶
5. **安全的會話管理** - 更安全的認證狀態管理

## 設置步驟

### 1. 安裝依賴
```bash
pip install python-dotenv
```

### 2. 設置密碼
運行密碼設置工具：
```bash
python setup_password.py
```

或者手動生成密碼哈希：
```python
python -c "from utils.auth import create_password_hash; print(create_password_hash('你的密碼'))"
```

### 3. 配置環境變數

#### 方法一：使用 .env 文件
創建 `.env` 文件：
```env
DASHBOARD_PASSWORD_HASH=你的密碼哈希
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

#### 方法二：設置系統環境變數
```bash
# Windows
set DASHBOARD_PASSWORD_HASH=你的密碼哈希
set MAX_LOGIN_ATTEMPTS=5
set LOCKOUT_DURATION_MINUTES=15

# Linux/Mac
export DASHBOARD_PASSWORD_HASH=你的密碼哈希
export MAX_LOGIN_ATTEMPTS=5
export LOCKOUT_DURATION_MINUTES=15
```

### 4. 運行應用
```bash
streamlit run app.py
```

## 安全配置選項

| 環境變數 | 說明 | 預設值 |
|---------|------|--------|
| `DASHBOARD_PASSWORD_HASH` | 密碼的 SHA256 哈希 | "password" 的哈希 |
| `MAX_LOGIN_ATTEMPTS` | 最大登入嘗試次數 | 5 |
| `LOCKOUT_DURATION_MINUTES` | 鎖定時間（分鐘） | 15 |

## 安全建議

1. **使用強密碼** - 包含大小寫字母、數字和特殊字符
2. **定期更換密碼** - 建議每 3-6 個月更換一次
3. **保護 .env 文件** - 確保 .env 文件不被提交到版本控制
4. **使用 HTTPS** - 在生產環境中使用 HTTPS
5. **監控登入嘗試** - 定期檢查是否有異常登入嘗試

## 故障排除

### 密碼不正確
- 確認密碼哈希是否正確生成
- 檢查環境變數是否正確設置
- 確認沒有多餘的空格或換行符

### 帳戶被鎖定
- 等待鎖定時間結束（預設 15 分鐘）
- 或者重啟應用程序重置鎖定狀態

### 環境變數不生效
- 確認 .env 文件在正確位置
- 檢查環境變數名稱是否正確
- 重啟應用程序

## 開發者注意事項

- 預設密碼是 "password"，僅用於開發測試
- 生產環境必須設置自己的密碼
- 不要將包含真實密碼的 .env 文件提交到版本控制
- 定期更新依賴包以修復安全漏洞 