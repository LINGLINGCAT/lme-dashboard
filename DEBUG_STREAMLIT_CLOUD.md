# Streamlit Cloud 除錯指南

當 `lme-dashboard.streamlit.app` 出現 **「Oh no. Error running app」** 時，可依下列步驟排查。

---

## 1. 先確認雲端日誌（最直接）

1. 登入 [share.streamlit.io](https://share.streamlit.io)
2. 點選你的 app **lme-dashboard**
3. 打開 **「Logs」** 或 **「Manage app」→「Logs」**
4. 查看 **Build logs**（建置失敗）或 **Runtime logs**（執行時錯誤）

日誌裡通常會出現 Python 的 traceback（例如 `ModuleNotFoundError`、`ImportError`），依該錯誤訊息修正即可。

---

## 2. 本地重現：用正確入口跑一次

在專案目錄執行（Cloud 若用 `streamlit_app.py` 就應用同一個入口）：

```powershell
cd d:\ANACONDA\lme-dashboard
python -m streamlit run streamlit_app.py
```

若 Cloud 設定的是 `app.py`，則改為：

```powershell
python -m streamlit run app.py
```

本地若出現錯誤，多半就是 Cloud 上也會失敗的原因（例如缺少套件、路徑錯誤）。

---

## 3. 常見原因與對策

| 現象 | 可能原因 | 處理方式 |
|------|----------|----------|
| 建置失敗 | `requirements.txt` 缺套件或版本不相容 | 在 `requirements.txt` 補上套件並註明版本，例如 `pandas>=2.0.0` |
| 執行時崩潰 | `st.set_page_config()` 不是第一個 Streamlit 指令 | 已在 `streamlit_app.py` 將 `st.set_page_config()` 移到最前面，請以該檔為 Cloud 主入口 |
| 找不到模組 | `utils`、`version`、`order_management` 等匯入失敗 | 確認 Cloud 主入口與本地一致、專案結構完整上傳（含 `utils/`、根目錄 `.py`） |
| 資料庫錯誤 | `quotation_system.db` 在 Cloud 上不存在或路徑不同 | Cloud 重啟後檔案可能被清空，需在應用內做「若無 DB 則自動建立」的邏輯（例如 `8_智能報價系統.py` 的 `init_database()`） |

---

## 4. 確認 Cloud 主入口

在 [share.streamlit.io](https://share.streamlit.io) → 你的 app → **Settings** 或 **Edit**：

- **Main file path** 應為：`streamlit_app.py`（或你實際設定的主檔名）
- 若設成 `app.py`，請改為 `streamlit_app.py`，以使用已修正「先 set_page_config 再 check_password」的版本。

---

## 5. 檢查依賴

專案已具備：

- `requirements.txt`：Python 套件
- `packages.txt`：系統套件（如 `libgomp1`、`libgl1-mesa-glx`，供 Plotly 等使用）

若日誌出現缺某個 Python 套件，把該套件加入 `requirements.txt` 並重新部署。

---

## 6. 本次已做的程式修正

- **`streamlit_app.py`**：已將 `st.set_page_config(...)` 移到檔案最前面（第一個 Streamlit 指令），避免因違反 Streamlit 規定而出現「Error running app」。

建議步驟：**先看 Cloud Logs 的錯誤訊息** → 再依上面對策修正；若仍無法解決，把完整錯誤貼到 GitHub Issues 或給管理員。
