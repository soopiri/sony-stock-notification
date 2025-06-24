#!/usr/bin/env python3
"""
운영 중 테스트 발송 스크립트
- 재고 있음/품절 상태 시뮬레이션 메시지 발송
- 실제 재고 확인 테스트
- 헬스체크 메시지 발송
- 사용자 정의 메시지 발송
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.discord_notifier import DiscordNotifier
from src.stock_monitor import StockMonitor

# 환경 변수 로드
load_dotenv()

class TestSender:
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.website_url = os.getenv('WEBSITE_URL', '')
        self.stock_selector = os.getenv('STOCK_SELECTOR', '')
        
        if not self.discord_webhook:
            raise ValueError("DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")
            
        self.notifier = DiscordNotifier(self.discord_webhook)
        
    def send_stock_available_test(self):
        """재고 있음 테스트 메시지 발송"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"🟢 **[테스트] 재고 있음!** 🟢\n⏰ {current_time}\n🔗 {self.website_url}\n\n⚠️ 이것은 테스트 메시지입니다."
        
        print("📤 재고 있음 테스트 메시지를 발송합니다...")
        success = self.notifier.send_message(message)
        
        if success:
            print("✅ 재고 있음 테스트 메시지 발송 성공!")
        else:
            print("❌ 재고 있음 테스트 메시지 발송 실패!")
            
    def send_timezone_test(self):
        """타임존 테스트 메시지 발송"""
        import time
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timezone_info = time.tzname
        
        message = f"🕐 **[타임존 테스트]** 🕐\n⏰ 현재 시간: {current_time}\n🌏 타임존: {timezone_info}\n\n⚠️ 이것은 테스트 메시지입니다."
        
        print("📤 타임존 테스트 메시지를 발송합니다...")
        success = self.notifier.send_message(message)
        
        if success:
            print("✅ 타임존 테스트 메시지 발송 성공!")
        else:
            print("❌ 타임존 테스트 메시지 발송 실패!")
            
        return success
        
    def send_out_of_stock_test(self):
        """품절 테스트 메시지 발송"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"🔴 **[테스트] 품절** 🔴\n⏰ {current_time}\n🔗 {self.website_url}\n\n⚠️ 이것은 테스트 메시지입니다."
        
        print("📤 품절 테스트 메시지를 발송합니다...")
        success = self.notifier.send_message(message)
        
        if success:
            print("✅ 품절 테스트 메시지 발송 성공!")
        else:
            print("❌ 품절 테스트 메시지 발송 실패!")
            
        return success
        
    def send_health_check_test(self):
        """헬스체크 테스트 메시지 발송"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"💚 **[테스트] 재고 모니터링 서비스 정상 동작** 💚\n⏰ {current_time}\n📊 모니터링 URL: {self.website_url}\n\n⚠️ 이것은 테스트 메시지입니다."
        
        print("📤 헬스체크 테스트 메시지를 발송합니다...")
        success = self.notifier.send_message(message)
        
        if success:
            print("✅ 헬스체크 테스트 메시지 발송 성공!")
        else:
            print("❌ 헬스체크 테스트 메시지 발송 실패!")
            
        return success
        
    def send_error_test(self):
        """에러 테스트 메시지 발송"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"❌ **[테스트] 재고 확인 오류** ❌\n⏰ {current_time}\n오류: 테스트용 에러 메시지입니다.\n\n⚠️ 이것은 테스트 메시지입니다."
        
        print("📤 에러 테스트 메시지를 발송합니다...")
        success = self.notifier.send_message(message)
        
        if success:
            print("✅ 에러 테스트 메시지 발송 성공!")
        else:
            print("❌ 에러 테스트 메시지 발송 실패!")
            
        return success
        
    def send_custom_message(self, message):
        """사용자 정의 메시지 발송"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"💬 **[사용자 정의 메시지]** 💬\n⏰ {current_time}\n\n{message}"
        
        print("📤 사용자 정의 메시지를 발송합니다...")
        success = self.notifier.send_message(full_message)
        
        if success:
            print("✅ 사용자 정의 메시지 발송 성공!")
        else:
            print("❌ 사용자 정의 메시지 발송 실패!")
            
        return success
        
    def send_actual_stock_check(self):
        """실제 재고 확인 후 메시지 발송"""
        if not self.website_url or not self.stock_selector:
            print("❌ WEBSITE_URL 또는 STOCK_SELECTOR가 설정되지 않아 실제 재고 확인을 할 수 없습니다.")
            return False
            
        print("🕷️ 실제 재고 상태를 확인합니다...")
        
        try:
            monitor = StockMonitor(self.website_url, self.stock_selector)
            stock_status = monitor.check_stock()
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if stock_status:
                message = f"🟢 **[실제 확인] 재고 있음!** 🟢\n⏰ {current_time}\n🔗 {self.website_url}\n\n✅ 실제 재고 상태를 확인했습니다."
                print("✅ 실제 재고 확인 결과: 재고 있음")
            else:
                message = f"🔴 **[실제 확인] 품절** 🔴\n⏰ {current_time}\n🔗 {self.website_url}\n\n✅ 실제 재고 상태를 확인했습니다."
                print("✅ 실제 재고 확인 결과: 품절")
                
            success = self.notifier.send_message(message)
            
            if success:
                print("✅ 실제 재고 확인 메시지 발송 성공!")
            else:
                print("❌ 실제 재고 확인 메시지 발송 실패!")
                
            return success
            
        except Exception as e:
            error_message = f"❌ **[실제 확인 오류]** ❌\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n오류: {str(e)}"
            print(f"❌ 실제 재고 확인 중 오류: {str(e)}")
            
            success = self.notifier.send_message(error_message)
            return success
            
    def send_embed_test(self):
        """Embed 형태 테스트 메시지 발송"""
        print("📤 Embed 테스트 메시지를 발송합니다...")
        
        fields = [
            {"name": "📊 모니터링 URL", "value": self.website_url, "inline": False},
            {"name": "🔄 상태", "value": "테스트 중", "inline": True},
            {"name": "⏰ 시간", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": True}
        ]
        
        success = self.notifier.send_embed_message(
            title="🧪 Discord Embed 테스트",
            description="이것은 Embed 형태의 테스트 메시지입니다.",
            color=0x00ff00,  # 초록색
            fields=fields
        )
        
        if success:
            print("✅ Embed 테스트 메시지 발송 성공!")
        else:
            print("❌ Embed 테스트 메시지 발송 실패!")
            
        return success

    def send_notification_mode_test(self):
        """알림 모드별 테스트 메시지 발송"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 현재 설정된 알림 모드 확인
        notification_mode = os.getenv('NOTIFICATION_MODE', 'stock_available_only')
        
        mode_descriptions = {
            'stock_available_only': '재고 있을때만',
            'always': '매번 확인시마다'
        }
        
        mode_desc = mode_descriptions.get(notification_mode, notification_mode)
        
        message = f"⚙️ **[알림 모드 테스트]** ⚙️\n⏰ {current_time}\n📋 현재 알림 모드: {mode_desc}\n\n⚠️ 이것은 테스트 메시지입니다."
        
        print("📤 알림 모드 테스트 메시지를 발송합니다...")
        success = self.notifier.send_message(message)
        
        if success:
            print("✅ 알림 모드 테스트 메시지 발송 성공!")
        else:
            print("❌ 알림 모드 테스트 메시지 발송 실패!")
            
        return success

def main():
    parser = argparse.ArgumentParser(description="Sony 재고 모니터링 서비스 테스트 발송 도구")
    parser.add_argument('--stock-available', action='store_true', help='재고 있음 테스트 메시지 발송')
    parser.add_argument('--out-of-stock', action='store_true', help='품절 테스트 메시지 발송')
    parser.add_argument('--health-check', action='store_true', help='헬스체크 테스트 메시지 발송')
    parser.add_argument('--error', action='store_true', help='에러 테스트 메시지 발송')
    parser.add_argument('--actual-check', action='store_true', help='실제 재고 확인 후 메시지 발송')
    parser.add_argument('--embed', action='store_true', help='Embed 테스트 메시지 발송')
    parser.add_argument('--notification-mode', action='store_true', help='알림 모드 테스트 메시지 발송')
    parser.add_argument('--timezone', action='store_true', help='타임존 테스트 메시지 발송')
    parser.add_argument('--custom', type=str, help='사용자 정의 메시지 발송')
    parser.add_argument('--all', action='store_true', help='모든 테스트 메시지 발송')
    
    args = parser.parse_args()
    
    # 인수가 없으면 대화형 모드 실행
    if not any(vars(args).values()):
        interactive_mode()
        return
        
    try:
        sender = TestSender()
        
        if args.stock_available or args.all:
            sender.send_stock_available_test()
            
        if args.out_of_stock or args.all:
            sender.send_out_of_stock_test()
            
        if args.health_check or args.all:
            sender.send_health_check_test()
            
        if args.error or args.all:
            sender.send_error_test()
            
        if args.actual_check or args.all:
            sender.send_actual_stock_check()
            
        if args.embed or args.all:
            sender.send_embed_test()
            
        if args.notification_mode or args.all:
            sender.send_notification_mode_test()
            
        if args.timezone or args.all:
            sender.send_timezone_test()
            
        if args.custom:
            sender.send_custom_message(args.custom)
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        sys.exit(1)

def interactive_mode():
    """대화형 모드"""
    print("🧪 Sony 재고 모니터링 서비스 테스트 발송 도구")
    print("=" * 50)
    
    try:
        sender = TestSender()
        
        while True:
            print("\n📤 테스트 발송 옵션:")
            print("1. 재고 있음 테스트 메시지")
            print("2. 품절 테스트 메시지")
            print("3. 헬스체크 테스트 메시지")
            print("4. 에러 테스트 메시지")
            print("5. 실제 재고 확인 후 메시지")
            print("6. Embed 테스트 메시지")
            print("7. 알림 모드 테스트 메시지")
            print("8. 타임존 테스트 메시지")
            print("9. 사용자 정의 메시지")
            print("10. 모든 테스트 메시지 발송")
            print("11. 종료")
            
            choice = input("\n선택하세요 (1-11): ").strip()
            
            if choice == '1':
                sender.send_stock_available_test()
            elif choice == '2':
                sender.send_out_of_stock_test()
            elif choice == '3':
                sender.send_health_check_test()
            elif choice == '4':
                sender.send_error_test()
            elif choice == '5':
                sender.send_actual_stock_check()
            elif choice == '6':
                sender.send_embed_test()
            elif choice == '7':
                sender.send_notification_mode_test()
            elif choice == '8':
                sender.send_timezone_test()
            elif choice == '9':
                custom_msg = input("발송할 메시지를 입력하세요: ")
                if custom_msg.strip():
                    sender.send_custom_message(custom_msg)
                else:
                    print("❌ 메시지가 비어있습니다.")
            elif choice == '10':
                print("🚀 모든 테스트 메시지를 발송합니다...")
                sender.send_stock_available_test()
                sender.send_out_of_stock_test()
                sender.send_health_check_test()
                sender.send_error_test()
                sender.send_actual_stock_check()
                sender.send_embed_test()
                sender.send_notification_mode_test()
                sender.send_timezone_test()
            elif choice == '11':
                print("👋 종료합니다.")
                break
            else:
                print("❌ 올바른 번호를 선택해주세요.")
                
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()