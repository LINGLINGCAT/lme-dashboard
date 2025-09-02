# 🚀 LME Dashboard 部署指南

本指南將幫助您將 LME Dashboard 部署到本地環境或雲端平台。

## 📋 目錄

1. [本地部署](#本地部署)
2. [Streamlit Cloud 部署](#streamlit-cloud-部署)
3. [Docker 部署](#docker-部署)
4. [故障排除](#故障排除)

---

## 🖥️ 本地部署

### 系統需求

- **Python**: 3.8 或更高版本
- **記憶體**: 最少 2GB RAM
- **磁碟空間**: 最少 500MB 可用空間
- **網路**: 穩定的網際網路連線

### 步驟 1: 環境準備

```bash
# 1. 克隆專案
git clone <your-repo-url>
cd lme-dashboard

# 2. 創建虛擬環境（推薦）
python -m venv venv

# 3. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安裝依賴套件
pip install -r requirements.txt
```

### 步驟 2: 環境變數設定

創建 `.env` 檔案：

```bash
# 在專案根目錄創建 .env 檔案
touch .env
```

編輯 `.env` 檔案內容：

```env
# 密碼設定（建議更改預設密碼）
DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8

# 登入安全設定
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# 數據更新設定
REFRESH_INTERVAL=30
AUTO_SAVE=true
```

### 步驟 3: 系統測試

```bash
# 運行完整功能測試
python test_all_functions.py
```

### 步驟 4: 啟動應用程式

```bash
# 啟動主應用程式
streamlit run app.py

# 或指定端口
streamlit run app.py --server.port 8501
```

### 步驟 5: 訪問應用程式

打開瀏覽器訪問：`http://localhost:8501`

- **預設密碼**: `password`
- **建議**: 首次登入後立即更改密碼

---

## ☁️ Streamlit Cloud 部署

### 步驟 1: 準備 GitHub 倉庫

1. 將專案推送到 GitHub
2. 確保倉庫是公開的（免費版要求）
3. 確保包含所有必要檔案

### 步驟 2: 設定 Streamlit Cloud

1. 訪問 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 帳號登入
3. 點擊 "New app"
4. 填寫部署資訊：
   - **Repository**: 選擇您的 GitHub 倉庫
   - **Branch**: `main` 或 `master`
   - **Main file path**: `app.py`
   - **App URL**: 自定義 URL（可選）

### 步驟 3: 環境變數設定

在 Streamlit Cloud 設定頁面添加環境變數：

```env
DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
```

### 步驟 4: 部署

1. 點擊 "Deploy!"
2. 等待部署完成
3. 訪問您的應用程式 URL

### 步驟 5: 更新部署

每次推送代碼到 GitHub 時，Streamlit Cloud 會自動重新部署。

---

## 🐳 Docker 部署

### 步驟 1: 創建 Dockerfile

在專案根目錄創建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY . .

# 創建數據目錄
RUN mkdir -p data

# 暴露端口
EXPOSE 8501

# 設定環境變數
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 啟動命令
CMD ["streamlit", "run", "app.py"]
```

### 步驟 2: 創建 docker-compose.yml

```yaml
version: '3.8'

services:
  lme-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
      - MAX_LOGIN_ATTEMPTS=5
      - LOCKOUT_DURATION_MINUTES=15
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### 步驟 3: 構建和運行

```bash
# 構建 Docker 映像
docker build -t lme-dashboard .

# 使用 docker-compose 運行
docker-compose up -d

# 或直接使用 Docker
docker run -p 8501:8501 -e DASHBOARD_PASSWORD_HASH=5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 lme-dashboard
```

---

## 🔧 故障排除

### 常見問題

#### 1. 模組導入錯誤

**錯誤**: `ModuleNotFoundError: No module named 'streamlit'`

**解決方法**:
```bash
pip install -r requirements.txt
```

#### 2. 端口被佔用

**錯誤**: `Port 8501 is already in use`

**解決方法**:
```bash
# 使用不同端口
streamlit run app.py --server.port 8502

# 或停止佔用端口的程序
lsof -ti:8501 | xargs kill -9
```

#### 3. 數據抓取失敗

**錯誤**: `ConnectionError` 或 `TimeoutError`

**解決方法**:
- 檢查網路連線
- 確認防火牆設定
- 稍後再試

#### 4. 認證問題

**錯誤**: 無法登入或密碼錯誤

**解決方法**:
- 確認 `.env` 檔案設定正確
- 檢查密碼哈希值
- 重置為預設密碼

#### 5. 記憶體不足

**錯誤**: `MemoryError` 或應用程式變慢

**解決方法**:
- 增加系統記憶體
- 減少同時運行的應用程式
- 調整 Streamlit 記憶體限制

### 日誌查看

```bash
# 查看 Streamlit 日誌
streamlit run app.py --logger.level debug

# 查看 Docker 日誌
docker logs <container_id>

# 查看系統資源使用
htop  # Linux/macOS
taskmgr  # Windows
```

### 性能優化

1. **減少更新頻率**: 在系統設定中調整
2. **清理快取**: 定期清理舊數據
3. **使用 SSD**: 提高數據讀寫速度
4. **增加記憶體**: 提高並發處理能力

---

## 📊 監控和維護

### 定期維護

1. **每日檢查**:
   - 確認數據抓取正常
   - 檢查錯誤日誌
   - 驗證計算結果

2. **每週維護**:
   - 清理舊數據
   - 更新依賴套件
   - 備份重要數據

3. **每月維護**:
   - 檢查系統性能
   - 更新密碼
   - 檢查安全設定

### 備份策略

```bash
# 備份數據檔案
cp -r data/ backup/data_$(date +%Y%m%d)/

# 備份設定檔案
cp .env backup/env_$(date +%Y%m%d)

# 創建完整備份
tar -czf backup_$(date +%Y%m%d).tar.gz data/ .env/
```

---

## 🆘 支援

### 獲取幫助

1. **查看文檔**: 閱讀 `README.md` 和 `pages/6_使用說明.py`
2. **運行測試**: 執行 `python test_all_functions.py`
3. **檢查日誌**: 查看錯誤訊息和系統日誌
4. **社區支援**: 在 GitHub Issues 中提問

### 緊急聯絡

- **系統故障**: 重新啟動應用程式
- **數據問題**: 檢查網路連線和數據來源
- **安全問題**: 立即更改密碼和檢查日誌

---

## 📝 更新日誌

### v1.5 (2024-01-01)
- ✅ 新增數據分析功能
- ✅ 新增系統設定頁面
- ✅ 新增使用說明文檔
- ✅ 改進認證系統
- ✅ 優化用戶界面

### v1.4 (2023-12-15)
- ✅ 新增線上計算機
- ✅ 改進數據抓取穩定性
- ✅ 新增歷史數據功能

### v1.3 (2023-12-01)
- ✅ 新增認證系統
- ✅ 改進即時數據更新
- ✅ 優化響應式設計

---

**🎉 恭喜！您已成功部署 LME Dashboard。**

如有任何問題，請參考上述故障排除指南或聯繫技術支援。 