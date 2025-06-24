#!/usr/bin/env python3
"""
런타임 설정 변경 도구 (수정됨)
- 실행 중인 서비스의 설정을 동적으로 변경
- JSON 파일을 통한 설정 업데이트
- 설정 변경 후 강제 리로드 기능 추가
"""

import os
import sys
import json
import argparse
import signal
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config_manager import get_config_manager

def show_current_config():
    """현재 설정 표시"""
    config_manager = get_config_manager()
    
    # runtime_config.json 파일이 있는지 확인
    import os
    if os.path.exists('runtime_config.json'):
        print("📄 runtime_config.json 파일 발견")
        try:
            import json
            with open('runtime_config.json', 'r', encoding='utf-8') as f:
                runtime_config = json.load(f)
            print(f"📄 runtime_config.json 내용: {runtime_config}")
        except Exception as e:
            print(f"❌ runtime_config.json 읽기 실패: {str(e)}")
    else:
        print("📄 runtime_config.json 파일 없음")
    
    current_config = config_manager.get_config()
    
    print("📋 현재 설정:")
    print("-" * 50)
    for key, value in current_config.items():
        print(f"{key}: {value}")
    print("-" * 50)

def trigger_config_reload():
    """메인 프로세스에 설정 리로드 신호 전송"""
    try:
        # 실행 중인 메인 프로세스 찾기
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'src/main.py'], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pid = int(result.stdout.strip().split('\n')[0])
            print(f"🔄 메인 프로세스 (PID: {pid})에 리로드 신호 전송...")
            
            # SIGUSR1 신호로 설정 리로드 요청
            os.kill(pid, signal.SIGUSR1)
            print("✅ 설정 리로드 신호 전송 완료")
            return True
        else:
            print("⚠️ 실행 중인 메인 프로세스를 찾을 수 없습니다")
            return False
            
    except Exception as e:
        print(f"⚠️ 설정 리로드 신호 전송 실패: {str(e)}")
        return False

def update_notification_mode(mode):
    """알림 모드 변경"""
    valid_modes = ['stock_available_only', 'always']
    if mode not in valid_modes:
        print(f"❌ 잘못된 알림 모드: {mode}")
        print(f"유효한 모드: {', '.join(valid_modes)}")
        return False
        
    config_manager = get_config_manager()
    
    # 변경 전 설정 확인
    old_mode = config_manager.get_config('NOTIFICATION_MODE')
    print(f"변경 전 알림 모드: {old_mode}")
    
    success = config_manager.update_config(NOTIFICATION_MODE=mode)
    
    if success:
        print(f"✅ 알림 모드 변경: {old_mode} → {mode}")
        
        # runtime_config.json 파일 확인
        import os, json
        if os.path.exists('runtime_config.json'):
            try:
                with open('runtime_config.json', 'r', encoding='utf-8') as f:
                    runtime_config = json.load(f)
                print(f"📄 저장된 파일 내용: {runtime_config.get('NOTIFICATION_MODE', '없음')}")
            except Exception as e:
                print(f"❌ 파일 읽기 실패: {str(e)}")
        
        # 환경변수 확인
        env_mode = os.getenv('NOTIFICATION_MODE')
        print(f"🌍 환경변수: {env_mode}")
        
        # ConfigManager에서 다시 읽기
        final_mode = config_manager.get_config('NOTIFICATION_MODE')
        print(f"🔄 최종 ConfigManager 설정: {final_mode}")
        
        # 메인 프로세스에 리로드 신호 전송
        reload_success = trigger_config_reload()
        if not reload_success:
            print("💡 수동으로 컨테이너를 재시작하세요: docker restart sony-stock-monitor")
        
    else:
        print("❌ 알림 모드 변경 실패")
    return success

def update_check_interval(minutes):
    """체크 주기 변경"""
    try:
        minutes = int(minutes)
        if minutes < 1:
            print("❌ 체크 주기는 1분 이상이어야 합니다")
            return False
            
        config_manager = get_config_manager()
        success = config_manager.update_config(CHECK_INTERVAL_MINUTES=minutes)
        
        if success:
            print(f"✅ 체크 주기 변경: {minutes}분")
            trigger_config_reload()
        else:
            print("❌ 체크 주기 변경 실패")
        return success
    except ValueError:
        print("❌ 잘못된 숫자 형식")
        return False

def update_health_check_times(times):
    """헬스체크 시간 변경"""
    # 시간 형식 검증
    time_list = [t.strip() for t in times.split(',')]
    for time_str in time_list:
        try:
            hour, minute = time_str.split(':')
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                raise ValueError
        except (ValueError, IndexError):
            print(f"❌ 잘못된 시간 형식: {time_str} (예: 09:00,12:00,15:00)")
            return False
    
    config_manager = get_config_manager()
    success = config_manager.update_config(HEALTH_CHECK_TIMES=times)
    
    if success:
        print(f"✅ 헬스체크 시간 변경: {times}")
        trigger_config_reload()
    else:
        print("❌ 헬스체크 시간 변경 실패")
    return success

def update_website_info(url, selector):
    """웹사이트 정보 변경"""
    if not url.startswith('http'):
        print("❌ 올바른 URL 형식이 아닙니다")
        return False
        
    if not selector:
        print("❌ CSS Selector를 입력해주세요")
        return False
    
    config_manager = get_config_manager()
    success = config_manager.update_config(
        WEBSITE_URL=url,
        STOCK_SELECTOR=selector
    )
    
    if success:
        print(f"✅ 웹사이트 정보 변경:")
        print(f"   URL: {url}")
        print(f"   Selector: {selector}")
        trigger_config_reload()
    else:
        print("❌ 웹사이트 정보 변경 실패")
    return success

def force_reload_config():
    """강제로 설정 리로드"""
    print("🔄 설정을 강제로 리로드합니다...")
    config_manager = get_config_manager()
    
    # runtime_config.json이 있으면 다시 로드
    runtime_config = config_manager.load_runtime_config()
    if runtime_config:
        print("✅ 런타임 설정 리로드 완료")
        trigger_config_reload()
        return True
    else:
        print("⚠️ 런타임 설정 파일이 없거나 로드 실패")
        return False

def interactive_mode():
    """대화형 설정 변경"""
    config_manager = get_config_manager()
    
    while True:
        print("\n⚙️ 런타임 설정 변경 도구")
        print("=" * 40)
        show_current_config()
        print("\n🔧 변경 옵션:")
        print("1. 알림 모드 변경")
        print("2. 체크 주기 변경")
        print("3. 헬스체크 시간 변경")
        print("4. 웹사이트 정보 변경")
        print("5. 설정 초기화 (.env 파일로)")
        print("6. 강제 설정 리로드")
        print("7. 종료")
        
        choice = input("\n선택하세요 (1-7): ").strip()
        
        if choice == '1':
            print("\n알림 모드:")
            print("1. stock_available_only (재고 있을때만)")
            print("2. always (매번 확인시마다)")
            mode_choice = input("선택하세요 (1-2): ").strip()
            
            if mode_choice == '1':
                update_notification_mode('stock_available_only')
            elif mode_choice == '2':
                update_notification_mode('always')
            else:
                print("❌ 잘못된 선택")
                
        elif choice == '2':
            minutes = input("새로운 체크 주기 (분): ").strip()
            update_check_interval(minutes)
            
        elif choice == '3':
            current_times = config_manager.get_config('HEALTH_CHECK_TIMES')
            print(f"현재 헬스체크 시간: {current_times}")
            times = input("새로운 헬스체크 시간 (예: 09:00,12:00,15:00): ").strip()
            if times:
                update_health_check_times(times)
                
        elif choice == '4':
            current_url = config_manager.get_config('WEBSITE_URL')
            current_selector = config_manager.get_config('STOCK_SELECTOR')
            print(f"현재 URL: {current_url}")
            print(f"현재 Selector: {current_selector}")
            
            url = input("새로운 URL: ").strip()
            selector = input("새로운 CSS Selector: ").strip()
            
            if url and selector:
                update_website_info(url, selector)
                
        elif choice == '5':
            confirm = input("정말로 설정을 초기화하시겠습니까? (y/N): ").strip().lower()
            if confirm == 'y':
                config_manager.reset_to_env_file()
                print("✅ 설정이 .env 파일로 초기화되었습니다")
                trigger_config_reload()
                
        elif choice == '6':
            force_reload_config()
            
        elif choice == '7':
            print("👋 종료합니다.")
            break
        else:
            print("❌ 올바른 번호를 선택해주세요.")

def main():
    parser = argparse.ArgumentParser(description="Sony 재고 모니터링 서비스 런타임 설정 변경 도구")
    parser.add_argument('--show', action='store_true', help='현재 설정 표시')
    parser.add_argument('--notification-mode', type=str, help='알림 모드 변경 (stock_available_only/always)')
    parser.add_argument('--check-interval', type=int, help='체크 주기 변경 (분)')
    parser.add_argument('--health-times', type=str, help='헬스체크 시간 변경 (예: 09:00,12:00,15:00)')
    parser.add_argument('--url', type=str, help='모니터링 URL 변경')
    parser.add_argument('--selector', type=str, help='CSS Selector 변경')
    parser.add_argument('--reset', action='store_true', help='설정 초기화')
    parser.add_argument('--reload', action='store_true', help='강제 설정 리로드')
    
    args = parser.parse_args()
    
    # 인수가 없으면 대화형 모드
    if not any(vars(args).values()):
        interactive_mode()
        return
    
    if args.show:
        show_current_config()
        
    if args.notification_mode:
        update_notification_mode(args.notification_mode)
        
    if args.check_interval:
        update_check_interval(args.check_interval)
        
    if args.health_times:
        update_health_check_times(args.health_times)
        
    if args.url and args.selector:
        update_website_info(args.url, args.selector)
    elif args.url or args.selector:
        print("❌ URL과 Selector를 모두 입력해주세요")
        
    if args.reset:
        config_manager = get_config_manager()
        config_manager.reset_to_env_file()
        print("✅ 설정이 초기화되었습니다")
        trigger_config_reload()
        
    if args.reload:
        force_reload_config()

if __name__ == "__main__":
    main()