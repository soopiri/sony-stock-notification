import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logger = logging.getLogger(__name__)

class StockMonitor:
    def __init__(self, website_url, stock_selector):
        self.website_url = website_url
        self.stock_selector = stock_selector
        self.driver = None
        self._setup_driver()
        
    def _setup_driver(self):
        """Chrome WebDriver 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # GUI 없이 실행
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Chrome 바이너리 경로 설정 (Docker 환경 지원)
            chrome_bin = os.getenv('CHROME_BIN')
            if chrome_bin and os.path.exists(chrome_bin):
                chrome_options.binary_location = chrome_bin
                logger.info(f"Chrome 바이너리 경로 설정: {chrome_bin}")
            
            # ChromeDriver 경로 설정
            chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
            if chromedriver_path and os.path.exists(chromedriver_path):
                self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
                logger.info(f"ChromeDriver 경로 설정: {chromedriver_path}")
            else:
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver 설정 완료")
        except Exception as e:
            logger.error(f"WebDriver 설정 중 오류: {str(e)}")
            raise
            
    def _get_element_text_with_multiple_methods(self, element):
        """다양한 방법으로 element에서 텍스트 추출"""
        methods = [
            ('element.text', lambda: element.text.strip()),
            ('get_attribute("textContent")', lambda: element.get_attribute('textContent').strip() if element.get_attribute('textContent') else ''),
            ('get_attribute("innerText")', lambda: element.get_attribute('innerText').strip() if element.get_attribute('innerText') else ''),
            ('get_attribute("innerHTML")', lambda: element.get_attribute('innerHTML').strip() if element.get_attribute('innerHTML') else ''),
            ('JavaScript textContent', lambda: self.driver.execute_script("return arguments[0].textContent;", element).strip() if self.driver.execute_script("return arguments[0].textContent;", element) else ''),
            ('JavaScript innerText', lambda: self.driver.execute_script("return arguments[0].innerText;", element).strip() if self.driver.execute_script("return arguments[0].innerText;", element) else '')
        ]
        
        for method_name, method_func in methods:
            try:
                text = method_func()
                if text:
                    logger.debug(f"{method_name}로 텍스트 추출 성공: '{text}'")
                    return text
            except Exception as e:
                logger.debug(f"{method_name} 실패: {str(e)}")
                continue
                
        logger.warning("모든 텍스트 추출 방법 실패")
        return ""
        
    def _restart_driver(self):
        """WebDriver 재시작"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        
        time.sleep(2)
        self._setup_driver()
        logger.info("WebDriver 재시작 완료")
        
    def check_stock(self, max_retries=3):
        """재고 확인 (True: 재고있음, False: 품절)"""
        for attempt in range(max_retries):
            try:
                logger.info(f"재고 확인 시도 {attempt + 1}/{max_retries}")
                
                # 페이지 로드
                self.driver.get(self.website_url)
                
                # 페이지 로딩 대기
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 추가 대기 (동적 콘텐츠 로딩)
                time.sleep(3)
                
                # 재고 정보 요소 찾기
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, self.stock_selector))
                    )
                except TimeoutException:
                    logger.warning(f"재고 정보 요소를 찾을 수 없음: {self.stock_selector}")
                    # 페이지 전체에서 "일시품절" 텍스트 검색
                    page_source = self.driver.page_source
                    if "일시품절" in page_source:
                        logger.info("페이지에서 '일시품절' 텍스트 발견")
                        return False
                    else:
                        logger.info("페이지에서 '일시품절' 텍스트 없음 - 재고 있음으로 판단")
                        return True
                
                # 다양한 방법으로 텍스트 추출
                text = self._get_element_text_with_multiple_methods(element)
                
                logger.info(f"추출된 텍스트: '{text}'")
                
                # "일시품절" 텍스트 확인
                if "일시품절" in text:
                    logger.info("품절 상태 확인")
                    return False
                else:
                    logger.info("재고 있음 상태 확인")
                    return True
                    
            except WebDriverException as e:
                logger.error(f"WebDriver 오류 (시도 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("WebDriver 재시작 시도")
                    self._restart_driver()
                    time.sleep(5)
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"재고 확인 중 오류 (시도 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    raise
                    
        raise Exception("모든 재시도 실패")
        
    def __del__(self):
        """소멸자 - WebDriver 정리"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass