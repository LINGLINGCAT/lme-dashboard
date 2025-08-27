# GitHub 部署指南

## 🚀 部署到 GitHub

### 1. 準備工作

#### 1.1 確保 Git 倉庫已初始化
```bash
git status
```

#### 1.2 添加所有文件到 Git
```bash
git add .
git commit -m "準備部署到 GitHub"
```

### 2. 推送到 GitHub

#### 2.1 創建 GitHub 倉庫
1. 前往 [GitHub](https://github.com)
2. 點擊 "New repository"
3. 輸入倉庫名稱：`lme-dashboard`
4. 選擇 Public 或 Private
5. 不要初始化 README（因為已經有）

#### 2.2 推送代碼
```bash
git remote add origin https://github.com/YOUR_USERNAME/lme-dashboard.git
git branch -M main
git push -u origin main
```

### 3. 部署到 Streamlit Cloud

#### 3.1 前往 Streamlit Cloud
1. 訪問 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 帳號登入
3. 點擊 "New app"

#### 3.2 配置部署
- **Repository**: `YOUR_USERNAME/lme-dashboard`
- **Branch**: `main`
- **Main file path**: `streamlit_app.py`
- **App URL**: 自動生成

#### 3.3 高級設定
- **Python version**: 3.9
- **Requirements file**: `requirements.txt`
- **System dependencies**: `packages.txt`

### 4. 環境變數設定

在 Streamlit Cloud 中設定以下環境變數：

```
STREAMLIT_SERVER_PORT = 8501
STREAMLIT_SERVER_ADDRESS = 0.0.0.0
```

### 5. 數據文件處理

#### 5.1 本地數據文件
- 將 `data/DATA.xlsx` 包含在倉庫中
- 或者使用外部數據源

#### 5.2 雲端數據文件
- 使用 Google Drive、OneDrive 等雲端服務
- 設定適當的訪問權限

### 6. 自動部署

#### 6.1 GitHub Actions
每次推送到 `main` 分支時，會自動觸發部署

#### 6.2 手動部署
在 Streamlit Cloud 中點擊 "Deploy" 按鈕

## 🔧 故障排除

### 常見問題

#### 1. 依賴問題
```bash
# 更新 requirements.txt
pip freeze > requirements.txt
```

#### 2. 路徑問題
確保所有文件路徑使用相對路徑

#### 3. 權限問題
檢查數據文件的訪問權限

### 測試部署

#### 1. 本地測試
```bash
streamlit run streamlit_app.py
```

#### 2. 雲端測試
訪問 Streamlit Cloud 提供的 URL

## 📊 監控和維護

### 1. 日誌查看
在 Streamlit Cloud 中查看應用程式日誌

### 2. 性能監控
監控應用程式的響應時間和資源使用

### 3. 更新部署
```bash
git add .
git commit -m "更新功能"
git push origin main
```

## 🎯 最佳實踐

### 1. 代碼管理
- 使用有意義的 commit 訊息
- 定期更新依賴
- 保持代碼整潔

### 2. 數據管理
- 定期備份數據文件
- 使用版本控制管理數據結構變更
- 考慮使用數據庫替代文件

### 3. 安全性
- 不要在代碼中硬編碼敏感信息
- 使用環境變數管理配置
- 定期更新安全依賴

## 📞 支援

如果遇到問題：
1. 檢查 Streamlit Cloud 日誌
2. 查看 GitHub Issues
3. 參考 Streamlit 官方文檔
