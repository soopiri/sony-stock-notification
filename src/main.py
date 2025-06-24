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

# config_manager import (없으면 기본 동작)
try:
    from src.config_manager import get_config_manager, start_config_watcher
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("config_manager를 사용할 수 없습니다. 기본 설정 모드로 실행합니다.")

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
        # config_manager 사용 가능한 경우 초기화
        if CONFIG_MANAGER_AVAILABLE:
            self.config_manager = get_config_manager()
            self.config_manager.register_callback(self._on_config_changed)
            # 런타임 설정이 있다면 적용
            self.config_manager.load_runtime_config()
            self._load_config_from_manager()
        else:
            self.config_manager = None
            self._load_config_from_env()
            
        self._setup_monitors()
        self._validate_config()
        
    def _load_config_from_manager(self):
        """ConfigManager에서 설정 로드"""
        config = self.config_manager.get_config()
        
        self.website_url = config.get('WEBSITE_URL', '')
        self.stock_selector = config.get('STOCK_SELECTOR', '')
        self.check_interval = config.get('CHECK_INTERVAL_MINUTES', 3)
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')
        self.health_check_times = config.get('HEALTH_CHECK_TIMES', '09:00,12:00,15:00,18:00,21:00,00:00').split(',')
        self.notification_mode = config.get('NOTIFICATION_MODE', NotificationMode.STOCK_AVAILABLE_ONLY).lower()
        
    def _load_config_from_env(self):
        """환경변수에서 설정 로드"""
        self.website_url = os.getenv('WEBSITE_URL', '')
        self.stock_selector = os.getenv('STOCK_SELECTOR', '')
        self.check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 3))
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')
        self.health_check_times = os.getenv('HEALTH_CHECK_TIMES', '09:00,12:00,15:00,18:00,21:00,00:00').split(',')
        self.notification_mode = os.getenv('NOTIFICATION_MODE', NotificationMode.STOCK_AVAILABLE_ONLY).lower()
        
    def _setup_monitors(self):
        """모니터링 객체 설정"""
        self.stock_monitor = StockMonitor(self.website_url, self.stock_selector)
        self.discord_notifier = DiscordNotifier(self.discord_webhook)
        
    def _on_config_changed(self, old_config, new_config):
        """설정 변경 시 콜백 (ConfigManager 사용 시에만)"""
        logger.info("설정 변경 감지 - 서비스 재구성 중...")
        
        # 설정 다시 로드
        self._load_config_from_manager()
        
        # 모니터링 객체 재설정 (URL이나 Selector가 바뀐 경우)
        if (old_config.get('WEBSITE_URL') != new_config.get('WEBSITE_URL') or 
            old_config.get('STOCK_SELECTOR') != new_config.get('STOCK_SELECTOR')):
            self._setup_monitors()
            
        # 스케줄러 재설정
        schedule.clear()
        self.setup_scheduler()
        
        # Discord 알림
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"⚙️ **설정 변경 적용** ⚙️\n⏰ {current_time}\n🔄 체크 주기: {self.check_interval}분\n📋 알림 모드: {self._get_mode_description()}"
        self.discord_notifier.send_message(message)
        
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
        
    def _should_send_notification(self, current_stock_status):
        """알림 발송 여부 결정"""
        if self.notification_mode == NotificationMode.STOCK_AVAILABLE_ONLY:
            # 재고가 있을 때만 알림
            return current_stock_status
            
        elif self.notification_mode == NotificationMode.ALWAYS:
            # 매번 알림
            return True
            
        return False
        
    def check_stock(self):
        """재고 확인 및 Discord 알림"""
        try:
            logger.info("재고 확인 시작")
            stock_status = self.stock_monitor.check_stock()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 알림 발송 여부 확인
            should_notify = self._should_send_notification(stock_status)
            
            if should_notify:
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
        
        # ConfigManager 사용 가능한 경우 설정 파일 감시 시작
        config_observer = None
        if CONFIG_MANAGER_AVAILABLE and self.config_manager:
            try:
                config_observer = start_config_watcher(self.config_manager)
                logger.info("동적 설정 변경 기능 활성화")
            except Exception as e:
                logger.warning(f"설정 파일 감시 시작 실패: {str(e)}")
        
        # 시작 메시지 발송
        dynamic_config_status = "활성화" if config_observer else "비활성화"
        start_message = f"🚀 **Sony 재고 모니터링 서비스 시작** 🚀\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n📊 모니터링 URL: {self.website_url}\n🔄 체크 주기: {self.check_interval}분\n📋 알림 모드: {self._get_mode_description()}\n⚙️ 동적 설정 변경: {dynamic_config_status}"
        self.discord_notifier.send_message(start_message)
        
        # 스케줄러 설정
        self.setup_scheduler()
        
        # 초기 재고 확인
        self.check_stock()
        
        try:
            # 스케줄러 실행
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("서비스 중단됨")
        finally:
            if config_observer:
                config_observer.stop()
                config_observer.join()

if __name__ == "__main__":
    try:
        service = SonyStockMonitorService()
        service.run()
    except KeyboardInterrupt:
        logger.info("서비스 중단됨")
    except Exception as e:
        logger.error(f"서비스 실행 중 오류: {str(e)}")
        raise