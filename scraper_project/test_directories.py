#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time

def test_business_directories():
    """測試商業目錄網站"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # 測試的商業目錄網站
    directories = [
        {
            'name': '台灣公司網',
            'url': 'https://www.twincn.com/',
            'search_url': 'https://www.twincn.com/search.aspx?keyword={}'
        },
        {
            'name': '中華黃頁',
            'url': 'https://www.iyp.com.tw/',
            'search_url': 'https://www.iyp.com.tw/search?q={}'
        },
        {
            'name': '台灣工商名錄',
            'url': 'https://www.taiwancompany.com/',
            'search_url': 'https://www.taiwancompany.com/search?q={}'
        }
    ]
    
    keyword = "沖壓工廠"
    
    for directory in directories:
        print(f"\n測試 {directory['name']}")
        print(f"URL: {directory['url']}")
        
        try:
            # 先測試主頁
            response = requests.get(directory['url'], headers=headers, timeout=10)
            print(f"主頁狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                print(f"頁面標題: {soup.title.string if soup.title else 'No title'}")
                
                # 尋找搜尋框
                search_inputs = soup.find_all('input', {'type': 'text'})
                print(f"找到 {len(search_inputs)} 個搜尋輸入框")
                
                # 尋找公司連結
                company_links = soup.find_all('a', href=True)
                company_links = [link for link in company_links if any(keyword in link.text for keyword in ['公司', '企業', '工廠', '廠'])]
                print(f"找到 {len(company_links)} 個可能的公司連結")
                
                # 顯示前3個連結
                for i, link in enumerate(company_links[:3]):
                    print(f"連結 {i+1}: {link.text.strip()} - {link.get('href')}")
            
        except Exception as e:
            print(f"測試失敗: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    test_business_directories() 