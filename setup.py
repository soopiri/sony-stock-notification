#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.discord_notifier import DiscordNotifier
from src.stock_monitor import StockMonitor

def create_env_file():
    """환경 변수 파일 생성"""
    if os.path.exists('.env'):
        print("⚠️  .env 파일이 이미 존재합니다.")
        response = input("덮어쓰시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("설정을 취소합니다.")
            return
    
    print("🔧 Sony 재고 모니터링 서비스 설정을 시작합니다.")
    print("-" * 50)
    
    # 사용자 입력 받기
    website_url = input("모니터링할 Sony 제품 URL을 입력하세요: ").strip()
    if not website_url:
        print("❌ URL을 입력해주세요.")
        return
        
    stock_selector = input("재고 상태 CSS Selector를 입력하세요 (예: .stock-status): ").strip()
    if not stock_selector:
        print("❌ CSS Selector를 입력해주세요.")
        return
        
    discord_webhook = input("Discord Webhook URL을 입력하세요: ").strip()
    if not discord_webhook or not discord_webhook.startswith('https://discord.com/api/webhooks/'):
        print("❌ 올바른 Discord Webhook URL을 입력해주세요.")
        return
        
    check_interval = input("재고 확인 주기를 분 단위로 입력하세요 (기본값: 3): ").strip()
    if not check_interval:
        check_interval = "3"
    
    health_check_times = input("헬스체크 시간을 입력하세요 (기본값: 09:00,12:00,15:00,18:00,21:00,00:00): ").strip()
    if not health_check_times:
        health_check_times = "09:00,12:00,15:00,18:00,21:00,00:00"
    
    # .env 파일 생성
    env_content = f"""# Sony 제품 페이지 URL
WEBSITE_URL={website_url}

# 재고 상태를 확인할 CSS Selector
STOCK_SELECTOR={stock_selector}

# 재고 확인 주기 (분 단위)
CHECK_INTERVAL_MINUTES={check_interval}

# Discord Webhook URL
DISCORD_WEBHOOK_URL={discord_webhook}

# 헬스체크 시간 (쉼표로 구분, 24시간 형식)
HEALTH_CHECK_TIMES={health_check_times}
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env 파일이 생성되었습니다.")
    return True

def test_discord_webhook():
    """Discord Webhook 연결 테스트"""
    load_dotenv()
    
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL이 설정되지 않았습니다.")
        return False
    
    print("🔔 Discord Webhook 연결을 테스트합니다...")
    
    try:
        notifier = DiscordNotifier(webhook_url)
        success = notifier.test_webhook()
        
        if success:
            print("✅ Discord Webhook 연결 테스트 성공!")
            return True
        else:
            print("❌ Discord Webhook 연결 테스트 실패!")
            return False
            
    except Exception as e:
        print(f"❌ Discord Webhook 테스트 중 오류: {str(e)}")
        return False

def test_stock_monitor():
    """재고 모니터링 테스트"""
    load_dotenv()
    
    website_url = os.getenv('WEBSITE_URL')
    stock_selector = os.getenv('STOCK_SELECTOR')
    
    if not website_url or not stock_selector:
        print("❌ WEBSITE_URL 또는 STOCK_SELECTOR가 설정되지 않았습니다.")
        return False
    
    print("🕷️ 재고 모니터링 테스트를 시작합니다...")
    print(f"URL: {website_url}")
    print(f"Selector: {stock_selector}")
    
    try:
        monitor = StockMonitor(website_url, stock_selector)
        stock_status = monitor.check_stock()
        
        status_text = "재고 있음" if stock_status else "품절"
        print(f"✅ 재고 모니터링 테스트 성공! 현재 상태: {status_text}")
        return True
        
    except Exception as e:
        print(f"❌ 재고 모니터링 테스트 중 오류: {str(e)}")
        return False

def run_full_test():
    """전체 시스템 테스트"""
    print("🧪 전체 시스템 테스트를 시작합니다.")
    print("=" * 50)
    
    # Discord Webhook 테스트
    discord_ok = test_discord_webhook()
    print()
    
    # 재고 모니터링 테스트
    stock_ok = test_stock_monitor()
    print()
    
    if discord_ok and stock_ok:
        print("🎉 모든 테스트가 성공했습니다! 서비스를 시작할 수 있습니다.")
        print("다음 명령으로 서비스를 시작하세요:")
        print("  python src/main.py")
        print("또는 Docker로 실행:")
        print("  cd docker && docker-compose up -d")
    else:
        print("❌ 일부 테스트가 실패했습니다. 설정을 확인해주세요.")

def create_directories():
    """필요한 디렉토리 생성"""
    directories = ['src', 'docker', 'logs']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 {directory}/ 디렉토리를 생성했습니다.")
    
    print("✅ 모든 필요한 디렉토리가 생성되었습니다.")

def show_project_structure():
    """프로젝트 구조 출력"""
    print("📁 프로젝트 구조:")
    print("""
sony-stock-monitor/
├── README.md                 # 프로젝트 메인 설명서
├── .gitignore               # Git 무시 파일
├── .env.example             # 환경변수 예제 파일
├── .env                     # 실제 환경변수 파일 (git에서 제외)
├── setup.py                 # 전체 프로젝트 설정 및 테스트 스크립트
├── requirements.txt         # Python 패키지 의존성
├── src/                     # 소스 코드 디렉토리
│   ├── __init__.py         # Python 패키지 초기화
│   ├── main.py             # 메인 애플리케이션
│   ├── stock_monitor.py    # 재고 모니터링 클래스
│   ├── discord_notifier.py # Discord 알림 클래스
│   └── test_sender.py      # 운영 중 테스트 발송 스크립트
├── docker/                  # Docker 관련 파일들
│   ├── Dockerfile          # Docker 컨테이너 설정
│   └── docker-compose.yml  # Docker Compose 설정
└── logs/                   # 로그 디렉토리 (자동 생성)
    └── stock_monitor.log   # 애플리케이션 로그
    """)

def install_dependencies():
    """의존성 패키지 설치"""
    print("📦 Python 패키지를 설치합니다...")
    
    import subprocess
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 모든 패키지가 성공적으로 설치되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 중 오류: {str(e)}")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt 파일을 찾을 수 없습니다.")
        return False

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'setup':
            create_env_file()
        elif command == 'test-discord':
            test_discord_webhook()
        elif command == 'test-stock':
            test_stock_monitor()
        elif command == 'test':
            run_full_test()
        elif command == 'install':
            install_dependencies()
        elif command == 'init':
            create_directories()
        elif command == 'structure':
            show_project_structure()
        else:
            print("사용법:")
            print("  python setup.py setup        # 환경 설정")
            print("  python setup.py test-discord # Discord 테스트")
            print("  python setup.py test-stock   # 재고 모니터링 테스트")
            print("  python setup.py test         # 전체 테스트")
            print("  python setup.py install      # 의존성 패키지 설치")
            print("  python setup.py init         # 디렉토리 초기화")
            print("  python setup.py structure    # 프로젝트 구조 보기")
    else:
        print("🚀 Sony 재고 모니터링 서비스 설정 도구")
        print("=" * 50)
        print("1. 디렉토리 초기화")
        print("2. 의존성 패키지 설치")
        print("3. 환경 설정")
        print("4. Discord Webhook 테스트")
        print("5. 재고 모니터링 테스트")
        print("6. 전체 테스트")
        print("7. 프로젝트 구조 보기")
        print("8. 종료")
        
        while True:
            choice = input("\n선택하세요 (1-8): ").strip()
            
            if choice == '1':
                create_directories()
            elif choice == '2':
                install_dependencies()
            elif choice == '3':
                create_env_file()
            elif choice == '4':
                test_discord_webhook()
            elif choice == '5':
                test_stock_monitor()
            elif choice == '6':
                run_full_test()
            elif choice == '7':
                show_project_structure()
            elif choice == '8':
                print("종료합니다.")
                break
            else:
                print("올바른 번호를 선택해주세요.")

if __name__ == "__main__":
    main()