#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time

def test_google_search():
    """測試Google搜尋功能"""
    
    # 設定headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # 測試搜尋
    keyword = "沖壓工廠"
    url = f"https://www.google.com/search?q={keyword}"
    
    print(f"測試搜尋: {keyword}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"狀態碼: {response.status_code}")
        print(f"頁面標題: {BeautifulSoup(response.content, 'html.parser').title.string if BeautifulSoup(response.content, 'html.parser').title else 'No title'}")
        
        # 檢查是否有驗證碼
        if "captcha" in response.text.lower() or "verify" in response.text.lower():
            print("檢測到驗證碼或驗證頁面")
            return False
            
        # 嘗試解析搜尋結果
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 嘗試多種選擇器
        selectors = [
            'div.g',
            'div.rc', 
            'div[data-sokoban-container]',
            'div.yuRUbf',
            'div.tF2Cxc',
            'div.Gx5Zad'
        ]
        
        results = []
        for selector in selectors:
            elements = soup.select(selector)
            print(f"選擇器 '{selector}' 找到 {len(elements)} 個元素")
            if elements:
                results = elements
                break
        
        if not results:
            # 最後嘗試：尋找所有包含連結的div
            all_divs = soup.find_all('div')
            results = [div for div in all_divs if div.find('a') and div.find('a').get('href', '').startswith('http')]
            print(f"通用選擇器找到 {len(results)} 個元素")
        
        print(f"總共找到 {len(results)} 個搜尋結果")
        
        # 顯示前3個結果
        for i, result in enumerate(results[:3]):
            title_elem = result.find('h3') or result.find('h2') or result.find('a')
            link_elem = result.find('a')
            
            if title_elem and link_elem:
                title = title_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                print(f"結果 {i+1}: {title}")
                print(f"連結: {link}")
                print("---")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"搜尋失敗: {e}")
        return False

if __name__ == "__main__":
    test_google_search() 