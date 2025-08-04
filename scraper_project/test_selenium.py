#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_selenium_search():
    """使用Selenium測試Google搜尋"""
    
    # 設定Chrome選項
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 暫時不使用無頭模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        # 初始化WebDriver
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # 測試搜尋
        keyword = "沖壓工廠"
        url = f"https://www.google.com/search?q={keyword}"
        
        print(f"測試搜尋: {keyword}")
        print(f"URL: {url}")
        
        # 訪問Google搜尋
        driver.get(url)
        
        # 等待頁面載入
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print(f"頁面標題: {driver.title}")
        
        # 檢查是否有驗證碼
        page_source = driver.page_source
        if "captcha" in page_source.lower() or "verify" in page_source.lower():
            print("檢測到驗證碼或驗證頁面")
            return False
        
        # 嘗試多種選擇器來找到搜尋結果
        selectors = [
            'div.g',
            'div.rc', 
            'div[data-sokoban-container]',
            'div.yuRUbf',
            'div.tF2Cxc',
            'div.Gx5Zad',
            'div[class*="g"]',
            'div[class*="result"]'
        ]
        
        results = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"選擇器 '{selector}' 找到 {len(elements)} 個元素")
                if elements:
                    results = elements
                    break
            except Exception as e:
                print(f"選擇器 '{selector}' 失敗: {e}")
                continue
        
        if not results:
            # 最後嘗試：尋找所有包含連結的div
            all_divs = driver.find_elements(By.TAG_NAME, "div")
            results = []
            for div in all_divs:
                try:
                    links = div.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        href = link.get_attribute('href')
                        if href and href.startswith('http'):
                            results.append(div)
                            break
                except:
                    continue
            print(f"通用選擇器找到 {len(results)} 個元素")
        
        print(f"總共找到 {len(results)} 個搜尋結果")
        
        # 顯示前3個結果
        for i, result in enumerate(results[:3]):
            try:
                title_elem = result.find_element(By.TAG_NAME, "h3")
                title = title_elem.text
            except:
                try:
                    title_elem = result.find_element(By.TAG_NAME, "h2")
                    title = title_elem.text
                except:
                    try:
                        title_elem = result.find_element(By.TAG_NAME, "a")
                        title = title_elem.text
                    except:
                        title = "無標題"
            
            try:
                link_elem = result.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute('href')
            except:
                link = "無連結"
            
            print(f"結果 {i+1}: {title}")
            print(f"連結: {link}")
            print("---")
        
        driver.quit()
        return len(results) > 0
        
    except Exception as e:
        print(f"搜尋失敗: {e}")
        try:
            driver.quit()
        except:
            pass
        return False

if __name__ == "__main__":
    test_selenium_search() 