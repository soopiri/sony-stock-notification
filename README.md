### 환경 변수 설정

`.env` 파일에서 다음 값들을 설정하세요:

```bash
# Sony 제품 페이지 URL
WEBSITE_URL=https://www.sony.co.kr/electronics/product/example

# 재고 상태를 확인할 CSS Selector
STOCK_SELECTOR=.stock-status

# 재고 확인 주기 (분 단위)
CHECK_INTERVAL_MINUTES=3

# Discord Webhook URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# 헬스체크 시간 (쉼표로 구분, 24시간 형식)
HEALTH_CHECK_TIMES=09:00,12:00,15:00,18:00,21:00,00:00

# 알림 조건 설정
# - stock_available_only: 재고가 있을 때만 알림 (기본값)
# - always: 매번 체크할 때마다 알림 (재고 있음/품절 모두)
NOTIFICATION_MODE=stock_available_only
```

## 📢 알림 모드 설명

### 간단한 두 가지 모드만

| 모드 | 설명 | 사용 예시 |
|------|------|-----------|
| `stock_available_only` | 재고가 있을 때만 알림 (기본값) | 재고 확보가 중요할 때 |
| `always` | 매번 체크시마다 현재 상태 알림 | 지속적인 상태 확인이 필요할 때 |

### 알림 예시

#### stock_available_only 모드
```
🟢 **재고 있음!** 🟢
⏰ 2025-06-23 14:30:15
🔗 https://www.sony.co.kr/electronics/product/# Sony 재고 모니터링 서비스

Sony 공식 홈페이지의 제품 재고를 실시간으로 모니터링하고 Discord 채널로 알림을 보내는 Python 서비스입니다.

## 📁 프로젝트 구조

```
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
```

## 🎯 주요 기능

- **실시간 재고 모니터링**: 설정된 주기마다 Sony 제품의 재고 상태를 확인
- **Discord 알림**: 재고 상태 변경 시 즉시 Discord 채널로 알림 발송
- **다양한 텍스트 추출**: 여러 방법으로 웹페이지에서 재고 정보 추출
- **헬스체크**: 정해진 시간에 서비스 정상 동작 확인
- **Docker 지원**: 컨테이너 환경에서 안정적인 실행
- **운영 중 테스트**: 서비스 실행 중 테스트 메시지 발송 기능

## 📋 사전 요구사항

- Python 3.11+
- Docker & Docker Compose (선택사항)
- Discord Webhook URL
- Chrome 브라우저 (Docker 환경에서는 자동 설치)

## 🚀 빠른 시작

### 1. 프로젝트 클론 및 초기 설정
```bash
git clone <repository-url>
cd sony-stock-monitor

# 프로젝트 초기화 (디렉토리 생성)
python setup.py init

# 의존성 패키지 설치
python setup.py install
```

### 2. 환경 설정
```bash
# 대화형 설정 도구 실행
python setup.py setup
```

### 3. 테스트
```bash
# 전체 시스템 테스트
python setup.py test
```

### 4. 실행
```bash
# Python으로 직접 실행
python src/main.py

# 또는 Docker로 실행
cd docker
docker-compose up -d
```

## 🔧 상세 설정

### Discord Webhook 설정

1. Discord 서버에서 채널 설정 → 연동 → 웹후크 생성
2. 생성된 Webhook URL을 `.env` 파일의 `DISCORD_WEBHOOK_URL`에 입력

### Sony 제품 페이지 정보 설정

1. 모니터링할 Sony 제품 페이지 URL을 `WEBSITE_URL`에 입력
2. 재고 상태를 나타내는 요소의 CSS Selector를 `STOCK_SELECTOR`에 입력

### 환경 변수 설정

`.env` 파일에서 다음 값들을 설정하세요:

```bash
# Sony 제품 페이지 URL
WEBSITE_URL=https://www.sony.co.kr/electronics/product/example

# 재고 상태를 확인할 CSS Selector
STOCK_SELECTOR=.stock-status

# 재고 확인 주기 (분 단위)
CHECK_INTERVAL_MINUTES=3

# Discord Webhook URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# 헬스체크 시간 (쉼표로 구분, 24시간 형식)
HEALTH_CHECK_TIMES=09:00,12:00,15:00,18:00,21:00,00:00

# 알림 조건 설정
# - stock_available_only: 재고가 있을 때만 알림 (기본값)
# - always: 매번 체크할 때마다 알림 (재고 있음/품절 모두)
NOTIFICATION_MODE=stock_available_only

# 중복 알림 방지 설정 (분 단위)
# 같은 상태에 대해 중복 알림을 방지할 시간 간격
DUPLICATE_PREVENTION_MINUTES=30
```

## 📢 알림 모드 설명

### 간단한 두 가지 모드

| 모드 | 설명 | 사용 예시 |
|------|------|-----------|
| `stock_available_only` | 재고가 있을 때만 알림 (기본값) | 재고 확보가 중요할 때 |
| `always` | 매번 체크시마다 현재 상태 알림 | 지속적인 상태 확인이 필요할 때 |

### 중복 방지 기능
- `DUPLICATE_PREVENTION_MINUTES` 설정으로 같은 상태의 중복 알림 방지
- 설정한 시간 간격 내 같은 상태 알림을 차단

### 알림 예시

#### stock_available_only 모드
```
🟢 **재고 있음!** 🟢
⏰ 2025-06-23 14:30:15
🔗 https://www.sony.co.kr/electronics/product/example
📋 알림 모드: 재고 있을때만
```

#### always 모드
```
🔴 **품절** 🔴
⏰ 2025-06-23 14:35:22
🔗 https://www.sony.co.kr/electronics/product/example
📋 알림 모드: 매번 확인시마다
```

## 🧪 테스트 및 모니터링

### 설정 테스트
```bash
# 개별 테스트
python setup.py test-discord  # Discord 연결 테스트
python setup.py test-stock    # 재고 모니터링 테스트

# 전체 테스트
python setup.py test
```

### 운영 중 테스트 발송

#### 대화형 모드 (추천)
```bash
python src/test_sender.py
```

#### 명령행 사용
```bash
# 재고 있음 테스트
python src/test_sender.py --stock-available

# 품절 테스트
python src/test_sender.py --out-of-stock

# 실제 재고 확인
python src/test_sender.py --actual-check

# 알림 모드 테스트
python src/test_sender.py --notification-mode

# 모든 테스트
python src/test_sender.py --all

# 사용자 정의 메시지
python src/test_sender.py --custom "사용자 정의 메시지"
```

#### Docker 환경에서 테스트
```bash
# 컨테이너 내부에서 실행
docker-compose exec sony-stock-monitor python src/test_sender.py

# 일회성 테스트
docker-compose run --rm sony-stock-monitor python src/test_sender.py --actual-check
```

## 🐳 Docker 실행

### Docker Compose 사용 (추천)
```bash
# 서비스 시작
cd docker
docker-compose up -d

# 로그 확인
docker-compose logs -f sony-stock-monitor

# 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart
```

### Docker 직접 사용
```bash
# 이미지 빌드
docker build -f docker/Dockerfile -t sony-stock-monitor .

# 컨테이너 실행
docker run -d --name sony-stock-monitor \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  sony-stock-monitor
```

## 📊 모니터링 및 로그

### 로그 확인
```bash
# 로컬 실행 시
tail -f logs/stock_monitor.log

# Docker 실행 시
docker-compose logs -f sony-stock-monitor
```

### 서비스 상태 확인
```bash
# Docker 컨테이너 상태
docker-compose ps

# 헬스체크 상태
docker-compose exec sony-stock-monitor python -c "print('Service is running')"
```

## 🔍 재고 확인 로직

서비스는 다음과 같은 방법으로 재고 정보를 확인합니다:

### 다양한 텍스트 추출 방법
1. `element.text`
2. `get_attribute("textContent")`
3. `get_attribute("innerText")`
4. `get_attribute("innerHTML")`
5. JavaScript `textContent`
6. JavaScript `innerText`

### 재고 판단 기준
- 추출된 텍스트에 "일시품절"이 포함되어 있으면 → **품절**
- "일시품절"이 없으면 → **재고 있음**

## 📱 Discord 알림 예시

### 서비스 시작
```
🚀 **Sony 재고 모니터링 서비스 시작** 🚀
⏰ 2025-06-23 09:00:00
📊 모니터링 URL: https://www.sony.co.kr/electronics/product/example
🔄 체크 주기: 3분
```

### 재고 상태 알림
```
🟢 **재고 있음!** 🟢
⏰ 2025-06-23 14:30:15
🔗 https://www.sony.co.kr/electronics/product/example
```

### 헬스체크
```
💚 **재고 모니터링 서비스 정상 동작** 💚
⏰ 2025-06-23 12:00:00
📊 모니터링 URL: https://www.sony.co.kr/electronics/product/example
```

### 테스트 메시지
```
🟢 **[테스트] 재고 있음!** 🟢
⏰ 2025-06-23 14:30:15
🔗 https://www.sony.co.kr/electronics/product/example

⚠️ 이것은 테스트 메시지입니다.
```

## 🛠️ 트러블슈팅

### 일반적인 문제

1. **ChromeDriver 오류**
   - Docker 환경에서는 자동으로 해결됨
   - 로컬 환경에서는 Chrome 브라우저와 ChromeDriver 버전 확인

2. **재고 정보를 찾을 수 없음**
   - CSS Selector가 올바른지 확인
   - 웹페이지 구조 변경 여부 확인
   - 페이지 로딩 시간 고려

3. **Discord 메시지 전송 실패**
   - Webhook URL이 올바른지 확인
   - 네트워크 연결 상태 확인
   - Discord Rate Limit 확인

4. **Docker 실행 오류**
   - 환경 변수 파일(.env) 존재 확인
   - Docker 서비스 실행 상태 확인
   - 포트 충돌 여부 확인

### 디버깅 방법

```bash
# 로그 레벨 증가 (main.py에서 수정)
logging.basicConfig(level=logging.DEBUG)

# 테스트 실행으로 문제 파악
python src/test_sender.py --actual-check

# Docker 컨테이너 내부 접근
docker-compose exec sony-stock-monitor /bin/bash
```

## 📈 성능 최적화

### 권장 설정
- **재고 확인 주기**: 3-5분 (너무 짧으면 IP 차단 위험)
- **메모리**: 최소 512MB, 권장 1GB
- **CPU**: 최소 0.25 코어, 권장 0.5 코어

### 모니터링 메트릭
- 응답 시간
- 메모리 사용량
- 디스크 I/O
- 네트워크 트래픽

## 🔒 보안 고려사항

- `.env` 파일은 버전 관리에 포함하지 마세요
- Discord Webhook URL은 안전하게 보관하세요
- 가능한 경우 최소 권한 원칙을 적용하세요
- 정기적으로 패키지를 업데이트하세요

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 📞 지원 및 문의

문제 발생 시 다음을 확인해 주세요:

1. **로그 파일**: `logs/stock_monitor.log`
2. **환경 변수**: `.env` 파일 설정
3. **네트워크 연결**: Sony 웹사이트 및 Discord 접근 가능 여부
4. **테스트 실행**: `python setup.py test`

추가 도움이 필요한 경우 Issues를 통해 문의해 주세요.