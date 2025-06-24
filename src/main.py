import os
import sys
import time
import schedule
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.stock_monitor import StockMonitor
from src.discord_notifier import DiscordNotifier

# 환경 변수 로드
load_dotenv()

# 알림 모드 상수
class NotificationMode:
    STOCK_AVAILABLE_ONLY = "stock_available_only"  # 재고 있을 때만 알림
    ALWAYS = "always"  # 매번 알림

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
        self.notification_mode = os.getenv('NOTIFICATION_MODE', NotificationMode.STOCK_AVAILABLE_ONLY).lower()
        self.duplicate_prevention_minutes = int(os.getenv('DUPLICATE_PREVENTION_MINUTES', 30))
        
        self.stock_monitor = StockMonitor(self.website_url, self.stock_selector)
        self.discord_notifier = DiscordNotifier(self.discord_webhook)
        
        # 알림 상태 추적
        self.last_notification_time = {}  # 각 상태별 마지막 알림 시간
        
        self._validate_config()
        
    def _validate_config(self):
        """환경 변수 유효성 검사"""
        if not self.website_url:
            raise ValueError("WEBSITE_URL이 설정되지 않았습니다")
        if not self.stock_selector:
            raise ValueError("STOCK_SELECTOR가 설정되지 않았습니다")
        if not self.discord_webhook:
            raise ValueError("DISCORD_WEBHOOK_URL이 설정되지 않았습니다")
            
        valid_modes = [NotificationMode.STOCK_AVAILABLE_ONLY, NotificationMode.ALWAYS]
        if self.notification_mode not in valid_modes:
            logger.warning(f"잘못된 NOTIFICATION_MODE: {self.notification_mode}. 기본값 '{NotificationMode.STOCK_AVAILABLE_ONLY}' 사용")
            self.notification_mode = NotificationMode.STOCK_AVAILABLE_ONLY
            
        logger.info(f"설정 완료 - URL: {self.website_url}")
        logger.info(f"체크 주기: {self.check_interval}분")
        logger.info(f"알림 모드: {self._get_mode_description()}")
        logger.info(f"중복 방지 시간: {self.duplicate_prevention_minutes}분")
        
    def _should_send_notification(self, current_stock_status):
        """알림 발송 여부 결정"""
        current_time = datetime.now()
        
        if self.notification_mode == NotificationMode.STOCK_AVAILABLE_ONLY:
            # 재고가 있을 때만 알림
            if not current_stock_status:
                return False
            # 중복 방지 확인
            return self._check_duplicate_prevention('stock_available', current_time)
            
        elif self.notification_mode == NotificationMode.ALWAYS:
            # 매번 알림 (중복 방지 적용)
            status_key = 'stock_available' if current_stock_status else 'out_of_stock'
            return self._check_duplicate_prevention(status_key, current_time)
            
        return False
        
    def _check_duplicate_prevention(self, status_key, current_time):
        """중복 알림 방지 확인"""
        if status_key not in self.last_notification_time:
            return True
            
        last_time = self.last_notification_time[status_key]
        time_diff = current_time - last_time
        
        return time_diff.total_seconds() >= (self.duplicate_prevention_minutes * 60)
        
    def _update_notification_time(self, status_key):
        """알림 시간 업데이트"""
        self.last_notification_time[status_key] = datetime.now()
        
    def check_stock(self):
        """재고 확인 및 Discord 알림"""
        try:
            logger.info("재고 확인 시작")
            stock_status = self.stock_monitor.check_stock()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 알림 발송 여부 확인
            should_notify = self._should_send_notification(stock_status)
            
            if should_notify:
                status_key = 'stock_available' if stock_status else 'out_of_stock'
                
                if stock_status:
                    message = f"🟢 **재고 있음!** 🟢\n⏰ {current_time}\n🔗 {self.website_url}"
                    logger.info("재고 있음 - Discord 알림 발송")
                else:
                    message = f"🔴 **품절** 🔴\n⏰ {current_time}\n🔗 {self.website_url}"
                    logger.info("품절 - Discord 알림 발송")
                
                # 알림 모드 정보 추가
                mode_info = self._get_mode_description()
                message += f"\n📋 알림 모드: {mode_info}"
                    
                self.discord_notifier.send_message(message)
                self._update_notification_time(status_key)
                
            else:
                reason = self._get_no_notification_reason(stock_status)
                logger.info(f"알림 발송하지 않음 - {reason}")
                
        except Exception as e:
            error_msg = f"❌ **재고 확인 오류** ❌\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n오류: {str(e)}"
            logger.error(f"재고 확인 중 오류: {str(e)}")
            self.discord_notifier.send_message(error_msg)
            
    def _get_mode_description(self):
        """알림 모드 설명 반환"""
        if self.notification_mode == NotificationMode.STOCK_AVAILABLE_ONLY:
            return "재고 있을때만"
        elif self.notification_mode == NotificationMode.ALWAYS:
            return "매번 확인시마다"
        return self.notification_mode
        
    def _get_no_notification_reason(self, current_stock_status):
        """알림을 보내지 않는 이유 반환"""
        if self.notification_mode == NotificationMode.STOCK_AVAILABLE_ONLY:
            if not current_stock_status:
                return "품절 상태 (재고 있을때만 알림 설정)"
            else:
                return f"중복 방지 시간 내 (재고 있음, {self.duplicate_prevention_minutes}분 대기)"
        elif self.notification_mode == NotificationMode.ALWAYS:
            status = '재고 있음' if current_stock_status else '품절'
            return f"중복 방지 시간 내 ({status}, {self.duplicate_prevention_minutes}분 대기)"
        
        return "알 수 없는 이유"
            
    def health_check(self):
        """서비스 정상 동작 확인"""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"💚 **재고 모니터링 서비스 정상 동작** 💚\n⏰ {current_time}\n📊 모니터링 URL: {self.website_url}\n📋 알림 모드: {self._get_mode_description()}"
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
        start_message = f"🚀 **Sony 재고 모니터링 서비스 시작** 🚀\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📊 모니터링 URL: {self.website_url}\n🔄 체크 주기: {self.check_interval}분\n📋 알림 모드: {self._get_mode_description()}"
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