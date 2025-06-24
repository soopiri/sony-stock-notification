"""
Sony 재고 모니터링 서비스 by soopiri

이 패키지는 Sony 공식 홈페이지의 제품 재고를 실시간으로 모니터링하고
Discord 채널로 알림을 보내는 서비스를 제공합니다.

모듈:
    - main: 메인 애플리케이션
    - stock_monitor: 재고 모니터링 클래스
    - discord_notifier: Discord 알림 클래스
    - test_sender: 운영 중 테스트 발송 도구
"""

__version__ = "1.0.0"
__author__ = "soopiri"
__email__ = "soopiri.jay@gmail.com"

from .stock_monitor import StockMonitor
from .discord_notifier import DiscordNotifier

__all__ = ['StockMonitor', 'DiscordNotifier']