#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 自動部署腳本
自動完成數據遷移、Git 提交和推送
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """執行命令並顯示結果"""
    print(f"\n🔄 {description}...")
    print(f"   執行命令：{command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout:
            print(f"   ✅ 輸出：{result.stdout.strip()}")
        
        if result.stderr:
            print(f"   ⚠️ 警告：{result.stderr.strip()}")
        
        if result.returncode == 0:
            print(f"   ✅ {description} 成功")
            return True
        else:
            print(f"   ❌ {description} 失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ 執行錯誤：{e}")
        return False

def check_git_status():
    """檢查 Git 狀態"""
    print("🔍 檢查 Git 狀態...")
    
    result = subprocess.run("git status", shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print("   ✅ Git 倉庫正常")
        return True
    else:
        print("   ❌ Git 倉庫異常")
        print(f"   錯誤：{result.stderr}")
        return False

def migrate_data():
    """執行數據遷移"""
    print("\n📊 執行數據遷移...")
    
    if not os.path.exists("migrate_data_to_github.py"):
        print("   ❌ 找不到數據遷移腳本")
        return False
    
    result = subprocess.run("python migrate_data_to_github.py", shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print("   ✅ 數據遷移成功")
        if result.stdout:
            print(f"   輸出：{result.stdout.strip()}")
        return True
    else:
        print("   ❌ 數據遷移失敗")
        if result.stderr:
            print(f"   錯誤：{result.stderr}")
        return False

def add_files_to_git():
    """添加文件到 Git"""
    print("\n📁 添加文件到 Git...")
    
    # 添加所有新文件和修改的文件
    commands = [
        "git add .",
        "git add data/DATA.xlsx",
        "git add pages/",
        "git add .github/",
        "git add *.py",
        "git add *.md",
        "git add *.toml",
        "git add *.txt"
    ]
    
    for command in commands:
        if not run_command(command, f"添加文件 ({command})"):
            return False
    
    return True

def commit_changes():
    """提交變更"""
    print("\n💾 提交變更...")
    
    commit_message = "🚀 部署到 GitHub：整合歷史數據並準備雲端部署"
    
    command = f'git commit -m "{commit_message}"'
    
    return run_command(command, "提交變更")

def push_to_github():
    """推送到 GitHub"""
    print("\n🚀 推送到 GitHub...")
    
    # 檢查是否有遠程倉庫
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True, encoding='utf-8')
    
    if "origin" not in result.stdout:
        print("   ⚠️ 沒有設定遠程倉庫")
        print("   💡 請先設定 GitHub 倉庫：")
        print("      git remote add origin https://github.com/YOUR_USERNAME/lme-dashboard.git")
        return False
    
    command = "git push origin main"
    
    return run_command(command, "推送到 GitHub")

def create_deployment_summary():
    """創建部署摘要"""
    print("\n📋 創建部署摘要...")
    
    summary = """# 🚀 GitHub 部署摘要

## ✅ 已完成的步驟

1. **數據遷移** - 整合現有歷史數據到 `data/DATA.xlsx`
2. **代碼更新** - 修改數據分析頁面支援多來源數據
3. **Git 提交** - 提交所有變更到本地倉庫
4. **GitHub 推送** - 推送到遠程 GitHub 倉庫

## 📊 數據統計

- **3M 數據**：594 行，14 欄位
- **CSP 數據**：605 行，6 欄位
- **時間範圍**：2024-01-01 至 2025-08-27

## 🎯 下一步

### 1. 部署到 Streamlit Cloud
1. 訪問 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 帳號登入
3. 點擊 "New app"
4. 設定：
   - Repository: `YOUR_USERNAME/lme-dashboard`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

### 2. 設定環境變數
在 Streamlit Cloud 中設定：
```
STREAMLIT_SERVER_PORT = 8501
STREAMLIT_SERVER_ADDRESS = 0.0.0.0
```

### 3. 數據更新流程
未來更新數據時：
1. 更新 `data/DATA.xlsx` 文件
2. 提交到 Git：`git add data/DATA.xlsx && git commit -m "更新數據"`
3. 推送到 GitHub：`git push origin main`
4. Streamlit Cloud 會自動重新部署

## 🔗 重要文件

- `data/DATA.xlsx` - 主要數據文件
- `pages/4_數據分析.py` - 數據分析頁面
- `streamlit_app.py` - Streamlit Cloud 入口文件
- `requirements.txt` - Python 依賴
- `config.toml` - Streamlit 配置

## 📞 支援

如果遇到問題，請檢查：
1. GitHub 倉庫權限
2. Streamlit Cloud 日誌
3. 數據文件格式
"""
    
    with open("DEPLOYMENT_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(summary)
    
    print("   ✅ 部署摘要已創建：DEPLOYMENT_SUMMARY.md")
    return True

def main():
    """主函數"""
    print("🚀 LME Dashboard GitHub 自動部署工具")
    print("=" * 60)
    print("📋 功能：自動完成數據遷移和 GitHub 部署")
    print("=" * 60)
    
    # 檢查 Git 狀態
    if not check_git_status():
        print("\n❌ Git 狀態檢查失敗，請確保已初始化 Git 倉庫")
        return
    
    # 執行數據遷移
    if not migrate_data():
        print("\n❌ 數據遷移失敗")
        return
    
    # 添加文件到 Git
    if not add_files_to_git():
        print("\n❌ 添加文件失敗")
        return
    
    # 提交變更
    if not commit_changes():
        print("\n❌ 提交變更失敗")
        return
    
    # 推送到 GitHub
    if not push_to_github():
        print("\n⚠️ 推送到 GitHub 失敗，請手動執行：")
        print("   git push origin main")
        return
    
    # 創建部署摘要
    create_deployment_summary()
    
    print("\n" + "=" * 60)
    print("🎉 GitHub 部署完成！")
    print("=" * 60)
    print("📝 下一步：")
    print("   1. 前往 Streamlit Cloud 部署應用程式")
    print("   2. 設定環境變數")
    print("   3. 測試雲端應用程式")
    print("\n📋 詳細說明請查看：DEPLOYMENT_SUMMARY.md")

if __name__ == "__main__":
    main()
