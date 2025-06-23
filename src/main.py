import os
import sys
import time
import schedule
import logging
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.stock_monitor import StockMonitor
from src.discord_notifier import DiscordNotifier

# 환경 변수 로드
load_dotenv()

# 로깅 설정
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'stock_monitor.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SonyStockMonitorService:
    def __init__(self):
        self.website_url = os.getenv('WEBSITE_URL', '')
        self.stock_selector = os.getenv('STOCK_SELECTOR', '')
        self.check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 3))
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')
        self.health_check_times = os.getenv('HEALTH_CHECK_TIMES', '09:00,12:00,15:00,18:00,21:00,00:00').split(',')
        
        self.stock_monitor = StockMonitor(self.website_url, self.stock_selector)
        self.discord_notifier = DiscordNotifier(self.discord_webhook)
        self.last_stock_status = None
        
        self._validate_config()
        
    def _validate_config(self):
        """환경 변수 유효성 검사"""
        if not self.website_url:
            raise ValueError("WEBSITE_URL이 설정되지 않았습니다")
        if not self.stock_selector:
            raise ValueError("STOCK_SELECTOR가 설정되지 않았습니다")
        if not self.discord_webhook:
            raise ValueError("DISCORD_WEBHOOK_URL이 설정되지 않았습니다")
            
        logger.info(f"설정 완료 - URL: {self.website_url}, 체크 주기: {self.check_interval}분")
        
    def check_stock(self):
        """재고 확인 및 Discord 알림"""
        try:
            logger.info("재고 확인 시작")
            stock_status = self.stock_monitor.check_stock()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 재고 상태가 변경되었을 때만 알림
            if self.last_stock_status != stock_status:
                if stock_status:
                    message = f"🟢 **재고 있음!** 🟢\n⏰ {current_time}\n🔗 {self.website_url}"
                    logger.info("재고 있음 - Discord 알림 발송")
                else:
                    message = f"🔴 **품절** 🔴\n⏰ {current_time}\n🔗 {self.website_url}"
                    logger.info("품절 - Discord 알림 발송")
                    
                self.discord_notifier.send_message(message)
                self.last_stock_status = stock_status
            else:
                logger.info(f"재고 상태 변경 없음 - {'재고 있음' if stock_status else '품절'}")
                
        except Exception as e:
            error_msg = f"❌ **재고 확인 오류** ❌\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n오류: {str(e)}"
            logger.error(f"재고 확인 중 오류: {str(e)}")
            self.discord_notifier.send_message(error_msg)
            
    def health_check(self):
        """서비스 정상 동작 확인"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"💚 **재고 모니터링 서비스 정상 동작** 💚\n⏰ {current_time}\n📊 모니터링 URL: {self.website_url}"
            logger.info("헬스체크 - 서비스 정상 동작")
            self.discord_notifier.send_message(message)
        except Exception as e:
            logger.error(f"헬스체크 중 오류: {str(e)}")
            
    def setup_scheduler(self):
        """스케줄러 설정"""
        # 재고 확인 스케줄
        schedule.every(self.check_interval).minutes.do(self.check_stock)
        
        # 헬스체크 스케줄
        for time_str in self.health_check_times:
            schedule.every().day.at(time_str.strip()).do(self.health_check)
            
        logger.info(f"스케줄러 설정 완료 - 재고체크: {self.check_interval}분마다, 헬스체크: {', '.join(self.health_check_times)}")
        
    def run(self):
        """서비스 실행"""
        logger.info("Sony 재고 모니터링 서비스 시작")
        
        # 시작 메시지 발송
        start_message = f"🚀 **Sony 재고 모니터링 서비스 시작** 🚀\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📊 모니터링 URL: {self.website_url}\n🔄 체크 주기: {self.check_interval}분"
        self.discord_notifier.send_message(start_message)
        
        # 스케줄러 설정
        self.setup_scheduler()
        
        # 초기 재고 확인
        self.check_stock()
        
        # 스케줄러 실행
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    try:
        service = SonyStockMonitorService()
        service.run()
    except KeyboardInterrupt:
        logger.info("서비스 중단됨")
    except Exception as e:
        logger.error(f"서비스 실행 중 오류: {str(e)}")
        raise