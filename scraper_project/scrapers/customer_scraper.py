# -*- coding: utf-8 -*-
"""
廢銅潛在客戶搜尋爬蟲
"""

import requests
import time
import re
import json
from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime

from config import COPPER_CUSTOMER_KEYWORDS, SEARCH_ENGINES, SCRAPER_CONFIG, PATHS
from utils.logger import customer_logger

class CustomerScraper:
    """客戶搜尋爬蟲"""
    
    def __init__(self):
        # self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # 初始化Selenium WebDriver
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """設定Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 無頭模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            customer_logger.info("Selenium WebDriver初始化成功")
        except Exception as e:
            customer_logger.error(f"Selenium WebDriver初始化失敗: {e}")
            self.driver = None
    
    def search_google(self, keyword, max_results=50):
        """
        使用多個搜尋引擎搜尋客戶
        
        Args:
            keyword (str): 搜尋關鍵字
            max_results (int): 最大結果數量
        
        Returns:
            list: 搜尋結果列表
        """
        results = []
        
        # 暫時跳過搜尋引擎，專注於商業目錄網站
        # 搜尋引擎被反爬蟲機制阻擋，暫時停用
        customer_logger.info(f"跳過搜尋引擎搜尋（被反爬蟲機制阻擋）: {keyword}")
        return results
    
    def search_business_directories(self, keyword):
        """
        搜尋商業目錄網站
        
        Args:
            keyword (str): 搜尋關鍵字
        
        Returns:
            list: 搜尋結果列表
        """
        results = []
        
        # 商業目錄網站列表
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
            },
            {
                'name': '經濟部商業司',
                'url': 'https://gcis.nat.gov.tw/',
                'search_url': 'https://gcis.nat.gov.tw/'
            },
            {
                'name': '台灣黃頁',
                'url': 'https://www.taiwanpage.com.tw/',
                'search_url': 'https://www.taiwanpage.com.tw/search?q={}'
            },
            {
                'name': '台灣工商名錄網',
                'url': 'https://www.taiwancompany.net/',
                'search_url': 'https://www.taiwancompany.net/search?q={}'
            }
        ]
        
        for directory in directories:
            try:
                customer_logger.info(f"搜尋商業目錄: {directory['name']}")
                
                # 先訪問主頁
                response = self.session.get(directory['url'], timeout=SCRAPER_CONFIG['timeout'])
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 尋找公司連結 - 使用多種模式
                company_links = []
                
                # 模式1: 尋找包含關鍵字的連結
                links = soup.find_all('a', href=True)
                for link in links:
                    link_text = link.get_text(strip=True)
                    if keyword in link_text and len(link_text) > 2:
                        company_links.append(link)
                
                # 模式1.5: 尋找包含關鍵字部分的連結
                if not company_links:
                    keyword_parts = keyword.split()
                    for link in links:
                        link_text = link.get_text(strip=True)
                        if any(part in link_text for part in keyword_parts) and len(link_text) > 2:
                            company_links.append(link)
                
                # 模式2: 尋找公司相關的連結
                if not company_links:
                    company_keywords = ['公司', '企業', '工廠', '廠', '工業', '製造']
                    for link in links:
                        link_text = link.get_text(strip=True)
                        if any(kw in link_text for kw in company_keywords):
                            company_links.append(link)
                
                # 模式3: 尋找特定class或id的連結
                if not company_links:
                    company_links = soup.find_all('a', class_=re.compile(r'company|business|enterprise'))
                
                # 模式4: 尋找工廠或製造相關的連結
                if not company_links:
                    factory_keywords = ['工廠', '製造', '工業', '加工', '沖壓', '電線', '電纜', '銅', '金屬']
                    for link in links:
                        link_text = link.get_text(strip=True)
                        if any(kw in link_text for kw in factory_keywords):
                            company_links.append(link)
                
                customer_logger.info(f"在 {directory['name']} 找到 {len(company_links)} 個可能的公司連結")
                
                for link in company_links[:10]:  # 限制結果數量
                    try:
                        company_name = link.get_text(strip=True)
                        company_url = link.get('href', '')
                        
                        # 確保URL是完整的
                        if company_url.startswith('/'):
                            company_url = directory['url'].rstrip('/') + company_url
                        elif not company_url.startswith('http'):
                            company_url = directory['url'] + company_url
                        
                        if company_name and self._is_relevant_company(company_name, keyword):
                            results.append({
                                'title': company_name,
                                'url': company_url,
                                'snippet': f"來自 {directory['name']}",
                                'keyword': keyword,
                                'source': directory['name']
                            })
                    except Exception as e:
                        customer_logger.warning(f"解析公司資訊時發生錯誤: {e}")
                        continue
                
                time.sleep(SCRAPER_CONFIG['delay_between_requests'])
                
            except Exception as e:
                customer_logger.error(f"搜尋商業目錄 {directory['name']} 失敗: {e}")
        
        return results
    
    def extract_company_info(self, url):
        """
        從公司網站提取詳細資訊
        
        Args:
            url (str): 公司網站URL
        
        Returns:
            dict: 公司詳細資訊
        """
        company_info = {
            'company_name': '',
            'address': '',
            'phone': '',
            'email': '',
            'website': url,
            'keywords': []
        }
        
        try:
            if not self.driver:
                return company_info
            
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 提取公司名稱
            company_info['company_name'] = self._extract_company_name(soup, url)
            
            # 提取地址
            company_info['address'] = self._extract_address(soup)
            
            # 提取電話
            company_info['phone'] = self._extract_phone(soup)
            
            # 提取Email
            company_info['email'] = self._extract_email(soup)
            
            # 識別關鍵字
            company_info['keywords'] = self._identify_keywords(soup)
            
            customer_logger.info(f"成功提取公司資訊: {company_info['company_name']}")
            
        except Exception as e:
            customer_logger.error(f"提取公司資訊失敗 {url}: {e}")
        
        return company_info
    
    def _is_relevant_result(self, title, snippet, keyword):
        """判斷搜尋結果是否相關"""
        text = f"{title} {snippet}".lower()
        keyword_lower = keyword.lower()
        
        # 檢查是否包含關鍵字
        if keyword_lower in text:
            return True
        
        # 檢查是否包含相關詞彙
        relevant_words = ['工廠', '廠', '製造', '加工', '回收', '金屬', '銅']
        return any(word in text for word in relevant_words)
    
    def _is_relevant_company(self, company_name, keyword):
        """判斷公司是否相關"""
        name_lower = company_name.lower()
        keyword_lower = keyword.lower()
        
        # 檢查公司名稱是否包含關鍵字
        if keyword_lower in name_lower:
            return True
        
        # 檢查關鍵字部分是否包含在公司名稱中
        keyword_parts = keyword_lower.split()
        if any(part in name_lower for part in keyword_parts):
            return True
        
        # 檢查是否包含相關詞彙
        relevant_words = ['工廠', '廠', '製造', '加工', '回收', '金屬', '銅', '沖壓', '電線', '電纜', '五金']
        if any(word in name_lower for word in relevant_words):
            return True
        
        # 檢查是否包含工業相關詞彙
        industry_words = ['工業', '企業', '有限公司', '股份有限公司', '公司']
        if any(word in name_lower for word in industry_words):
            # 如果包含工業詞彙，進一步檢查是否有製造相關詞彙
            manufacturing_words = ['製造', '加工', '生產', '製造商', '工廠']
            return any(word in name_lower for word in manufacturing_words)
        
        return False
    
    def _extract_company_name(self, soup, url):
        """提取公司名稱"""
        # 嘗試多種方式提取公司名稱
        selectors = [
            'h1', 'title', '.company-name', '.brand', '.logo-text',
            '[class*="company"]', '[class*="brand"]', '[class*="logo"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 100:
                    return text
        
        # 從URL提取
        if 'www.' in url:
            domain = url.split('www.')[1].split('/')[0]
            return domain.replace('.com', '').replace('.tw', '').title()
        
        return ''
    
    def _extract_address(self, soup):
        """提取地址"""
        # 尋找地址相關的元素
        address_patterns = [
            r'地址[：:]\s*(.+)',
            r'Address[：:]\s*(.+)',
            r'([0-9]+號[^0-9]+)',
            r'([^0-9]+路[0-9]+號)',
            r'([^0-9]+街[0-9]+號)'
        ]
        
        text = soup.get_text()
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        
        return ''
    
    def _extract_phone(self, soup):
        """提取電話號碼"""
        # 尋找電話號碼
        phone_patterns = [
            r'電話[：:]\s*([0-9\-\(\)\s]+)',
            r'Tel[：:]\s*([0-9\-\(\)\s]+)',
            r'([0-9]{2,4}-[0-9]{3,4}-[0-9]{4})',
            r'([0-9]{8,10})'
        ]
        
        text = soup.get_text()
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        
        return ''
    
    def _extract_email(self, soup):
        """提取Email"""
        # 尋找Email地址
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        text = soup.get_text()
        matches = re.findall(email_pattern, text)
        
        if matches:
            return matches[0]
        
        return ''
    
    def _identify_keywords(self, soup):
        """識別頁面中的關鍵字"""
        text = soup.get_text().lower()
        identified_keywords = []
        
        for keyword in COPPER_CUSTOMER_KEYWORDS:
            if keyword.lower() in text:
                identified_keywords.append(keyword)
        
        return identified_keywords
    
    def run_search(self):
        """
        執行完整的客戶搜尋
        
        Returns:
            list: 客戶資料列表
        """
        all_customers = []
        
        customer_logger.info("開始執行客戶搜尋")
        
        for keyword in COPPER_CUSTOMER_KEYWORDS:
            customer_logger.info(f"搜尋關鍵字: {keyword}")
            
            # Google搜尋
            google_results = self.search_google(keyword, max_results=30)
            
            # 商業目錄搜尋
            directory_results = self.search_business_directories(keyword)
            
            # 合併結果
            all_results = google_results + directory_results
            
            # 去重
            unique_results = self._remove_duplicates(all_results)
            
            # 提取詳細資訊
            for result in unique_results[:10]:  # 限制每個關鍵字的處理數量
                try:
                    company_info = self.extract_company_info(result['url'])
                    if company_info['company_name']:
                        company_info['source_url'] = result['url']
                        company_info['search_keyword'] = keyword
                        all_customers.append(company_info)
                    
                    time.sleep(SCRAPER_CONFIG['delay_between_requests'])
                    
                except Exception as e:
                    customer_logger.error(f"處理公司資訊時發生錯誤: {e}")
                    continue
        
        # 最終去重
        final_customers = self._remove_duplicate_customers(all_customers)
        
        customer_logger.info(f"客戶搜尋完成，共找到 {len(final_customers)} 個潛在客戶")
        
        return final_customers
    
    def _remove_duplicates(self, results):
        """移除重複的搜尋結果"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        return unique_results
    
    def _remove_duplicate_customers(self, customers):
        """移除重複的客戶資料"""
        seen_names = set()
        unique_customers = []
        
        for customer in customers:
            name = customer['company_name'].lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_customers.append(customer)
        
        return unique_customers
    
    def save_to_excel(self, customers_data):
        """
        將客戶資料儲存到Excel檔案
        
        Args:
            customers_data (list): 客戶資料列表
        """
        try:
            if not customers_data:
                customer_logger.warning("沒有客戶資料可儲存")
                return
            
            # 準備DataFrame
            df_data = []
            for customer in customers_data:
                df_data.append({
                    '公司名稱': customer.get('company_name', ''),
                    '地址': customer.get('address', ''),
                    '電話': customer.get('phone', ''),
                    'Email': customer.get('email', ''),
                    '網站': customer.get('website', ''),
                    '來源URL': customer.get('source_url', ''),
                    '搜尋關鍵字': customer.get('search_keyword', ''),
                    '識別關鍵字': ', '.join(customer.get('keywords', [])),
                    '搜尋日期': datetime.now().strftime('%Y-%m-%d')
                })
            
            df = pd.DataFrame(df_data)
            
            # 儲存到Excel
            df.to_excel(PATHS['customer_file'], index=False, engine='openpyxl')
            
            customer_logger.info(f"客戶資料已儲存到: {PATHS['customer_file']}")
            
        except Exception as e:
            customer_logger.error(f"儲存客戶資料失敗: {e}")
    
    def cleanup(self):
        """清理資源"""
        if self.driver:
            self.driver.quit()
            customer_logger.info("Selenium WebDriver已關閉") 