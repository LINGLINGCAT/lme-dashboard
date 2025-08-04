# -*- coding: utf-8 -*-
"""
政府標案監控爬蟲
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
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime, timedelta

from config import GOVERNMENT_TENDER_KEYWORDS, GOVERNMENT_SITES, SCRAPER_CONFIG, PATHS
from utils.logger import tender_logger

class TenderScraper:
    """政府標案監控爬蟲"""
    
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
            tender_logger.info("Selenium WebDriver初始化成功")
        except Exception as e:
            tender_logger.error(f"Selenium WebDriver初始化失敗: {e}")
            self.driver = None
    
    def scrape_government_e_procurement(self, keyword):
        """
        爬取政府電子採購網
        
        Args:
            keyword (str): 搜尋關鍵字
        
        Returns:
            list: 標案資料列表
        """
        tenders = []
        
        try:
            if not self.driver:
                return tenders
            
            tender_logger.info(f"開始爬取政府電子採購網: {keyword}")
            
            # 計算搜尋日期範圍（最近14天）
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=14)  # 改為14天
            
            # 訪問政府電子採購網
            self.driver.get(GOVERNMENT_SITES['政府電子採購網'])
            
            # 等待頁面載入
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 點擊"招標查詢"標籤
            try:
                tender_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '招標查詢')]"))
                )
                tender_tab.click()
                tender_logger.info("已點擊招標查詢標籤")
                
                # 等待搜尋表單載入
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[name*='keyword'], input[name*='search']"))
                )
                
                # 尋找財物名稱輸入框
                property_name_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='財物名稱' or contains(@name, '財物名稱') or contains(@name, 'property')]"))
                )
                
                # 輸入關鍵字
                property_name_input.clear()
                property_name_input.send_keys(keyword)
                tender_logger.info(f"已輸入財物名稱關鍵字: {keyword}")
                
                # 設定日期範圍
                try:
                    # 尋找公告日期輸入框
                    date_inputs = self.driver.find_elements(By.XPATH, "//input[@type='text' and contains(@placeholder, '日期') or contains(@name, 'date')]")
                    if len(date_inputs) >= 2:
                        # 設定開始日期
                        start_date_input = date_inputs[0]
                        start_date_input.clear()
                        start_date_input.send_keys(start_date.strftime("%Y/%m/%d"))
                        
                        # 設定結束日期
                        end_date_input = date_inputs[1]
                        end_date_input.clear()
                        end_date_input.send_keys(end_date.strftime("%Y/%m/%d"))
                        
                        tender_logger.info(f"已設定日期範圍: {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}")
                except Exception as e:
                    tender_logger.warning(f"設定日期範圍失敗: {e}")
                
                # 點擊搜尋按鈕
                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '查詢') or contains(@value, '查詢')]"))
                )
                search_button.click()
                tender_logger.info("已點擊搜尋按鈕")
                
                # 等待搜尋結果載入
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table, .result, .list"))
                )
                
                # 解析搜尋結果
                tenders = self._parse_government_e_procurement_results(keyword, start_date, end_date)
                
            except Exception as e:
                tender_logger.error(f"政府電子採購網搜尋失敗: {e}")
                
        except Exception as e:
            tender_logger.error(f"政府電子採購網爬取失敗: {e}")
        
        return tenders
    
    def _parse_government_e_procurement_results(self, keyword, start_date, end_date):
        """
        解析政府電子採購網搜尋結果
        
        Args:
            keyword (str): 搜尋關鍵字
            start_date (datetime): 開始日期
            end_date (datetime): 結束日期
        
        Returns:
            list: 標案資料列表
        """
        tenders = []
        
        try:
            # 解析搜尋結果頁面
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 嘗試多種可能的結果選擇器
            result_selectors = [
                'tr[class*="tender"]', 'tr[class*="row"]', 'tr[class*="item"]',
                '.tender-item', '.procurement-item', '.result-item',
                'table tr', '.list-item', '.result-row'
            ]
            
            tender_rows = []
            for selector in result_selectors:
                tender_rows = soup.select(selector)
                if tender_rows:
                    tender_logger.info(f"使用選擇器 '{selector}' 找到 {len(tender_rows)} 個結果")
                    break
            
            if not tender_rows:
                # 如果沒有找到特定選擇器，嘗試通用的表格行
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # 至少有標題行和數據行
                        tender_rows = rows[1:]  # 跳過標題行
                        tender_logger.info(f"從表格中找到 {len(tender_rows)} 個結果")
                        break
            
            for row in tender_rows[:20]:  # 限制結果數量
                try:
                    tender_info = self._parse_government_tender_row(row, keyword)
                    if tender_info and self._is_relevant_tender(tender_info['title'], keyword):
                        # 檢查日期是否在範圍內
                        if self._is_within_date_range(tender_info.get('deadline', ''), start_date, end_date):
                            tenders.append(tender_info)
                
                except Exception as e:
                    tender_logger.warning(f"解析標案資料時發生錯誤: {e}")
                    continue
            
            tender_logger.info(f"政府電子採購網解析完成，找到 {len(tenders)} 個相關標案")
            
        except Exception as e:
            tender_logger.error(f"解析政府電子採購網結果失敗: {e}")
        
        return tenders
    
    def _parse_government_tender_row(self, row, keyword):
        """
        解析政府電子採購網的標案行資料
        
        Args:
            row: BeautifulSoup元素
            keyword (str): 搜尋關鍵字
        
        Returns:
            dict: 標案資訊
        """
        try:
            # 提取所有文字內容
            cells = row.find_all(['td', 'th'])
            if not cells:
                return None
            
            # 嘗試提取標案資訊
            tender_info = {
                'title': '',
                'agency': '',
                'deadline': '',
                'url': '',
                'source': '政府電子採購網',
                'keyword': keyword
            }
            
            # 根據單元格數量分配資料
            if len(cells) >= 3:
                # 假設格式：標案名稱 | 機關名稱 | 截止日期 | ...
                tender_info['title'] = cells[0].get_text(strip=True) if cells[0] else ''
                tender_info['agency'] = cells[1].get_text(strip=True) if len(cells) > 1 and cells[1] else ''
                tender_info['deadline'] = cells[2].get_text(strip=True) if len(cells) > 2 and cells[2] else ''
            
            # 提取連結
            link = row.find('a')
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('/'):
                    href = 'https://web.pcc.gov.tw' + href
                tender_info['url'] = href
            
            # 如果沒有找到標題，嘗試從連結文字提取
            if not tender_info['title'] and link:
                tender_info['title'] = link.get_text(strip=True)
            
            # 清理資料
            for key in ['title', 'agency', 'deadline']:
                if tender_info[key]:
                    tender_info[key] = tender_info[key].strip()
            
            return tender_info if tender_info['title'] else None
            
        except Exception as e:
            tender_logger.warning(f"解析標案行資料失敗: {e}")
            return None
    
    def scrape_taipei_government(self, keyword):
        """
        爬取台北市政府採購網
        
        Args:
            keyword (str): 搜尋關鍵字
        
        Returns:
            list: 標案資料列表
        """
        tenders = []
        
        try:
            tender_logger.info(f"開始爬取台北市政府採購網: {keyword}")
            
            # 計算搜尋日期範圍（最近30天）
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=SCRAPER_CONFIG['search_days_back'])
            
            # 台北市政府採購網的搜尋URL
            search_url = f"{GOVERNMENT_SITES['台北市政府採購網']}search?keyword={keyword}"
            
            response = self.session.get(search_url, timeout=SCRAPER_CONFIG['timeout'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析搜尋結果（需要根據實際網站結構調整）
            tender_items = soup.find_all('div', class_='tender-item')
            
            for item in tender_items[:15]:  # 限制結果數量
                try:
                    title_elem = item.find('h3')
                    agency_elem = item.find('span', class_='agency')
                    deadline_elem = item.find('span', class_='deadline')
                    budget_elem = item.find('span', class_='budget')
                    
                    tender_info = {
                        'title': title_elem.get_text(strip=True) if title_elem else '',
                        'agency': agency_elem.get_text(strip=True) if agency_elem else '台北市政府',
                        'deadline': deadline_elem.get_text(strip=True) if deadline_elem else '',
                        'budget': budget_elem.get_text(strip=True) if budget_elem else '',
                        'status': '招標中',
                        'keyword': keyword,
                        'source': '台北市政府採購網',
                        'url': self._extract_url_from_item(item)
                    }
                    
                    if self._is_relevant_tender(tender_info['title'], keyword):
                        # 檢查日期是否在範圍內
                        if self._is_within_date_range(tender_info.get('deadline', ''), start_date, end_date):
                            tenders.append(tender_info)
                
                except Exception as e:
                    tender_logger.warning(f"解析台北市標案資料時發生錯誤: {e}")
                    continue
            
            tender_logger.info(f"台北市政府採購網爬取完成，找到 {len(tenders)} 個相關標案")
            
        except Exception as e:
            tender_logger.error(f"爬取台北市政府採購網失敗: {e}")
        
        return tenders
    
    def scrape_new_taipei_government(self, keyword):
        """
        爬取新北市政府採購網
        
        Args:
            keyword (str): 搜尋關鍵字
        
        Returns:
            list: 標案資料列表
        """
        tenders = []
        
        try:
            tender_logger.info(f"開始爬取新北市政府採購網: {keyword}")
            
            # 計算搜尋日期範圍（最近30天）
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=SCRAPER_CONFIG['search_days_back'])
            
            # 新北市政府採購網的搜尋URL
            search_url = f"{GOVERNMENT_SITES['新北市政府採購網']}search?q={keyword}"
            
            response = self.session.get(search_url, timeout=SCRAPER_CONFIG['timeout'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 解析搜尋結果（需要根據實際網站結構調整）
            tender_rows = soup.find_all('tr', class_='tender-row')
            
            for row in tender_rows[:15]:  # 限制結果數量
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        tender_info = {
                            'title': cells[0].get_text(strip=True) if len(cells) > 0 else '',
                            'agency': cells[1].get_text(strip=True) if len(cells) > 1 else '新北市政府',
                            'deadline': cells[2].get_text(strip=True) if len(cells) > 2 else '',
                            'budget': cells[3].get_text(strip=True) if len(cells) > 3 else '',
                            'status': '招標中',
                            'keyword': keyword,
                            'source': '新北市政府採購網',
                            'url': self._extract_url_from_row(row)
                        }
                        
                        if self._is_relevant_tender(tender_info['title'], keyword):
                            # 檢查日期是否在範圍內
                            if self._is_within_date_range(tender_info.get('deadline', ''), start_date, end_date):
                                tenders.append(tender_info)
                
                except Exception as e:
                    tender_logger.warning(f"解析新北市標案資料時發生錯誤: {e}")
                    continue
            
            tender_logger.info(f"新北市政府採購網爬取完成，找到 {len(tenders)} 個相關標案")
            
        except Exception as e:
            tender_logger.error(f"爬取新北市政府採購網失敗: {e}")
        
        return tenders
    
    def scrape_taoyuan_government(self, keyword):
        """
        爬取桃園市政府採購網
        
        Args:
            keyword (str): 搜尋關鍵字
        
        Returns:
            list: 標案資料列表
        """
        tenders = []
        
        try:
            tender_logger.info(f"開始爬取桃園市政府採購網: {keyword}")
            
            # 計算搜尋日期範圍（最近30天）
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=SCRAPER_CONFIG['search_days_back'])
            
            # 桃園市政府採購網的搜尋URL
            search_url = f"{GOVERNMENT_SITES['桃園市政府採購網']}search?keyword={keyword}"
            
            response = self.session.get(search_url, timeout=SCRAPER_CONFIG['timeout'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # 解析搜尋結果（需要根據實際網站結構調整）
            tender_items = soup.find_all('div', class_='procurement-item')
            
            for item in tender_items[:15]:  # 限制結果數量
                try:
                    title_elem = item.find('h4')
                    agency_elem = item.find('span', class_='department')
                    deadline_elem = item.find('span', class_='date')
                    budget_elem = item.find('span', class_='amount')
                    
                    tender_info = {
                        'title': title_elem.get_text(strip=True) if title_elem else '',
                        'agency': agency_elem.get_text(strip=True) if agency_elem else '桃園市政府',
                        'deadline': deadline_elem.get_text(strip=True) if deadline_elem else '',
                        'budget': budget_elem.get_text(strip=True) if budget_elem else '',
                        'status': '招標中',
                        'keyword': keyword,
                        'source': '桃園市政府採購網',
                        'url': self._extract_url_from_item(item)
                    }
                    
                    if self._is_relevant_tender(tender_info['title'], keyword):
                        # 檢查日期是否在範圍內
                        if self._is_within_date_range(tender_info.get('deadline', ''), start_date, end_date):
                            tenders.append(tender_info)
                
                except Exception as e:
                    tender_logger.warning(f"解析桃園市標案資料時發生錯誤: {e}")
                    continue
            
            tender_logger.info(f"桃園市政府採購網爬取完成，找到 {len(tenders)} 個相關標案")
            
        except Exception as e:
            tender_logger.error(f"爬取桃園市政府採購網失敗: {e}")
        
        return tenders
    
    def _is_relevant_tender(self, title, keyword):
        """判斷標案是否相關"""
        if not title:
            return False
        
        title_lower = title.lower()
        keyword_lower = keyword.lower()
        
        # 檢查標題是否包含關鍵字
        if keyword_lower in title_lower:
            return True
        
        # 檢查是否包含相關詞彙
        relevant_words = ['回收', '廢料', '金屬', '銅', '計量', '下腳', '五金']
        return any(word in title_lower for word in relevant_words)
    
    def _extract_tender_url(self, row):
        """從標案行提取URL"""
        try:
            link = row.find('a')
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('/'):
                    return f"https://web.pcc.gov.tw{href}"
                return href
        except:
            pass
        return ''
    
    def _extract_url_from_item(self, item):
        """從標案項目提取URL"""
        try:
            link = item.find('a')
            if link and link.get('href'):
                return link.get('href')
        except:
            pass
        return ''
    
    def _extract_url_from_row(self, row):
        """從標案行提取URL"""
        try:
            link = row.find('a')
            if link and link.get('href'):
                return link.get('href')
        except:
            pass
        return ''
    
    def _parse_tender_row(self, row, keyword):
        """
        解析標案行資料
        
        Args:
            row: BeautifulSoup元素
            keyword (str): 搜尋關鍵字
        
        Returns:
            dict: 標案資訊字典
        """
        try:
            # 嘗試多種解析方式
            tender_info = {
                'title': '',
                'agency': '',
                'deadline': '',
                'budget': '',
                'status': '招標中',
                'keyword': keyword,
                'source': '政府電子採購網',
                'url': ''
            }
            
            # 提取標題
            title_selectors = ['h3', 'h4', '.title', '.name', 'td:nth-child(2)', 'td:nth-child(1)']
            for selector in title_selectors:
                title_elem = row.select_one(selector)
                if title_elem:
                    tender_info['title'] = title_elem.get_text(strip=True)
                    break
            
            # 提取機關
            agency_selectors = ['.agency', '.department', 'td:nth-child(3)', 'td:nth-child(2)']
            for selector in agency_selectors:
                agency_elem = row.select_one(selector)
                if agency_elem:
                    tender_info['agency'] = agency_elem.get_text(strip=True)
                    break
            
            # 提取截止日期
            date_selectors = ['.deadline', '.date', 'td:nth-child(4)', 'td:nth-child(3)']
            for selector in date_selectors:
                date_elem = row.select_one(selector)
                if date_elem:
                    tender_info['deadline'] = date_elem.get_text(strip=True)
                    break
            
            # 提取預算
            budget_selectors = ['.budget', '.amount', 'td:nth-child(5)', 'td:nth-child(4)']
            for selector in budget_selectors:
                budget_elem = row.select_one(selector)
                if budget_elem:
                    tender_info['budget'] = budget_elem.get_text(strip=True)
                    break
            
            # 提取URL
            tender_info['url'] = self._extract_url_from_row(row)
            
            # 如果沒有找到標題，嘗試從文字內容提取
            if not tender_info['title']:
                text = row.get_text()
                if text and len(text.strip()) > 10:
                    tender_info['title'] = text.strip()[:100]  # 取前100個字元
            
            return tender_info if tender_info['title'] else None
            
        except Exception as e:
            tender_logger.warning(f"解析標案行失敗: {e}")
            return None
    
    def _is_within_date_range(self, date_str, start_date, end_date):
        """
        檢查日期是否在指定範圍內
        
        Args:
            date_str (str): 日期字串
            start_date (datetime): 開始日期
            end_date (datetime): 結束日期
        
        Returns:
            bool: 是否在範圍內
        """
        if not date_str:
            return True  # 如果沒有日期資訊，預設包含
        
        try:
            # 嘗試多種日期格式
            date_formats = [
                '%Y-%m-%d', '%Y/%m/%d', '%Y年%m月%d日',
                '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    return start_date <= parsed_date <= end_date
                except ValueError:
                    continue
            
            # 如果無法解析日期，預設包含
            return True
            
        except Exception as e:
            tender_logger.warning(f"日期解析失敗: {date_str}, 錯誤: {e}")
            return True  # 預設包含
    
    def run_search(self):
        """
        執行完整的標案搜尋
        
        Returns:
            list: 標案資料列表
        """
        all_tenders = []
        
        tender_logger.info("開始執行政府標案搜尋")
        
        for keyword in GOVERNMENT_TENDER_KEYWORDS:
            tender_logger.info(f"搜尋關鍵字: {keyword}")
            
            # 爬取各政府網站
            gov_e_procurement_tenders = self.scrape_government_e_procurement(keyword)
            taipei_tenders = self.scrape_taipei_government(keyword)
            new_taipei_tenders = self.scrape_new_taipei_government(keyword)
            taoyuan_tenders = self.scrape_taoyuan_government(keyword)
            
            # 合併結果
            keyword_tenders = (
                gov_e_procurement_tenders + 
                taipei_tenders + 
                new_taipei_tenders + 
                taoyuan_tenders
            )
            
            # 去重
            unique_tenders = self._remove_duplicate_tenders(keyword_tenders)
            
            all_tenders.extend(unique_tenders)
            
            time.sleep(SCRAPER_CONFIG['delay_between_requests'])
        
        # 最終去重
        final_tenders = self._remove_duplicate_tenders(all_tenders)
        
        tender_logger.info(f"政府標案搜尋完成，共找到 {len(final_tenders)} 個相關標案")
        
        return final_tenders
    
    def _remove_duplicate_tenders(self, tenders):
        """移除重複的標案"""
        seen_titles = set()
        unique_tenders = []
        
        for tender in tenders:
            title = tender['title'].lower()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_tenders.append(tender)
        
        return unique_tenders
    
    def save_to_excel(self, tenders_data):
        """
        將標案資料儲存到Excel檔案
        
        Args:
            tenders_data (list): 標案資料列表
        """
        try:
            if not tenders_data:
                tender_logger.warning("沒有標案資料可儲存")
                return
            
            # 準備DataFrame
            df_data = []
            for tender in tenders_data:
                df_data.append({
                    '標案名稱': tender.get('title', ''),
                    '招標機關': tender.get('agency', ''),
                    '截止日期': tender.get('deadline', ''),
                    '預算金額': tender.get('budget', ''),
                    '標案狀態': tender.get('status', ''),
                    '來源網站': tender.get('source', ''),
                    '標案網址': tender.get('url', ''),
                    '搜尋關鍵字': tender.get('keyword', ''),
                    '搜尋日期': datetime.now().strftime('%Y-%m-%d')
                })
            
            df = pd.DataFrame(df_data)
            
            # 儲存到Excel
            df.to_excel(PATHS['tender_file'], index=False, engine='openpyxl')
            
            tender_logger.info(f"標案資料已儲存到: {PATHS['tender_file']}")
            
        except Exception as e:
            tender_logger.error(f"儲存標案資料失敗: {e}")
    
    def cleanup(self):
        """清理資源"""
        if self.driver:
            self.driver.quit()
            tender_logger.info("Selenium WebDriver已關閉") 