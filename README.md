# Sony 재고 모니터링 서비스

Sony 공식 홈페이지의 제품 재고를 실시간으로 모니터링하고 Discord 채널로 알림을 보내는 Python 서비스입니다.

## 📁 프로젝트 구조

```
sony-stock-monitor/
├── README.md                    # 프로젝트 설명서
├── .gitignore                  # Git 무시 파일
├── .env.example                # 환경변수 예제 파일
├── .env                        # 실제 환경변수 파일 (git에서 제외)
├── setup.py                    # 프로젝트 설정 및 테스트 스크립트
├── requirements.txt            # Python 패키지 의존성
├── src/                        # 📂 소스 코드 디렉토리
│   ├── __init__.py            # Python 패키지 초기화
│   ├── main.py                # 메인 애플리케이션
│   ├── stock_monitor.py       # 재고 모니터링 클래스
│   ├── discord_notifier.py    # Discord 알림 클래스
│   ├── test_sender.py         # 테스트 발송 스크립트
│   ├── config_manager.py      # 런타임 설정 관리자
│   └── runtime_config_tool.py # 런타임 설정 변경 도구
├── docker/                     # 📂 Docker 관련 파일들
│   ├── Dockerfile             # Docker 컨테이너 설정
│   └── docker-compose.yml     # Docker Compose 설정
└── logs/                      # 📂 로그 디렉토리 (자동 생성)
    └── stock_monitor.log      # 애플리케이션 로그
```

## 🎯 주요 기능

- **실시간 재고 모니터링**: 설정된 주기마다 Sony 제품의 재고 상태를 확인
- **Discord 알림**: 설정된 조건에 따라 Discord 채널로 알림 발송
- **다양한 텍스트 추출**: 여러 방법으로 웹페이지에서 재고 정보 추출
- **헬스체크**: 정해진 시간에 서비스 정상 동작 확인
- **Docker 지원**: 컨테이너 환경에서 안정적인 실행
- **동적 설정 변경**: 서비스 중단 없이 실시간 설정 변경
- **운영 중 테스트**: 서비스 실행 중 테스트 메시지 발송 기능

## 📋 사전 요구사항

- **Docker & Docker Compose** (필수)
- **Discord Webhook URL** (필수)
- Python 3.11+ (로컬 실행 시에만)
- Chrome 브라우저 (Docker 환경에서는 자동 설치)

## 🚀 빠른 시작

### 1단계: 프로젝트 준비
```bash
# 프로젝트 다운로드
git clone <repository-url>
cd sony-stock-monitor
```

### 2단계: 환경 설정
```bash
# 환경 변수 파일 생성
cp .env.example .env

# 환경 변수 편집
nano .env
```

**`.env` 파일 필수 설정:**
```bash
# Sony 제품 페이지 URL
WEBSITE_URL=https://store.sony.co.kr/product-view/102263765

# 재고 상태를 확인할 CSS Selector
STOCK_SELECTOR=.availability-status

# Discord Webhook URL
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN

# 재고 확인 주기 (분 단위)
CHECK_INTERVAL_MINUTES=3

# 헬스체크 시간 (쉼표로 구분, 24시간 형식)
HEALTH_CHECK_TIMES=09:00,12:00,15:00,18:00,21:00,00:00

# 알림 조건 설정
NOTIFICATION_MODE=stock_available_only
```

### 3단계: Docker 실행
```bash
# 이미지 빌드 및 서비스 시작
cd docker
docker-compose up -d

# 실행 상태 확인
docker ps

# 로그 확인
docker logs -f sony-stock-monitor
```

## 🔧 상세 설정

### Discord Webhook 설정

1. **Discord 서버에서 Webhook 생성**
   - 채널 설정 → 연동 → 웹후크 → 새 웹후크
   - 웹후크 URL 복사

2. **환경변수에 설정**
   ```bash
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
   ```

### Sony 제품 페이지 설정

1. **모니터링할 제품 URL 확인**
   - Sony 스토어에서 제품 페이지 접속
   - URL 복사하여 `WEBSITE_URL`에 설정

2. **재고 상태 CSS Selector 찾기**
   - 브라우저 개발자 도구 (F12) 실행
   - 재고 상태 텍스트 요소 검사
   - CSS Selector 복사하여 `STOCK_SELECTOR`에 설정

### 환경 변수 상세 설명

| 변수명 | 설명 | 예시 | 필수 |
|--------|------|------|------|
| `WEBSITE_URL` | 모니터링할 Sony 제품 페이지 URL | `https://store.sony.co.kr/product-view/102263765` | ✅ |
| `STOCK_SELECTOR` | 재고 상태 확인용 CSS Selector | `.availability-status` | ✅ |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | `https://discord.com/api/webhooks/...` | ✅ |
| `CHECK_INTERVAL_MINUTES` | 재고 확인 주기 (분) | `3` | ❌ |
| `HEALTH_CHECK_TIMES` | 헬스체크 시간 | `09:00,12:00,15:00,18:00,21:00,00:00` | ❌ |
| `NOTIFICATION_MODE` | 알림 모드 | `stock_available_only` | ❌ |

## 📢 알림 모드 설명

### 간단한 두 가지 모드

| 모드 | 설명 | 사용 예시 |
|------|------|-----------|
| `stock_available_only` | 재고가 있을 때만 알림 (기본값) | 재고 확보가 중요할 때 |
| `always` | 매번 체크시마다 현재 상태 알림 | 지속적인 상태 확인이 필요할 때 |

### 알림 예시

#### stock_available_only 모드
```
🟢 **재고 있음!** 🟢
⏰ 2025-06-24 14:30:15
🔗 https://store.sony.co.kr/product-view/102263765
📋 알림 모드: 재고 있을때만
```

#### always 모드
```
🔴 **품절** 🔴
⏰ 2025-06-24 14:35:22
🔗 https://store.sony.co.kr/product-view/102263765
📋 알림 모드: 매번 확인시마다
```

## 🐳 Docker 사용법

### Docker Compose 사용 (추천)

#### 서비스 관리
```bash
# 서비스 시작
cd docker
docker-compose up -d

# 서비스 중지
docker-compose down

# 서비스 재시작
docker restart sony-stock-monitor

# 이미지 재빌드 후 시작
docker-compose up --build -d
```

#### 상태 확인
```bash
# 컨테이너 상태 확인
docker ps

# 실시간 로그 확인
docker logs -f sony-stock-monitor

# 리소스 사용량 확인
docker stats sony-stock-monitor
```

### Docker 직접 사용

#### 이미지 빌드
```bash
# 현재 플랫폼용 빌드
docker build -f docker/Dockerfile -t sony-stock-monitor:latest .

# ARM64 환경 (M1/M2 Mac, ARM 서버)
docker build --platform linux/arm64 -f docker/Dockerfile -t sony-stock-monitor:latest .

# AMD64 환경 (Intel/AMD 서버)
docker build --platform linux/amd64 -f docker/Dockerfile -t sony-stock-monitor:latest .
```

#### 컨테이너 실행
```bash
# 기본 실행
docker run -d \
  --name sony-stock-monitor \
  --env-file .env \
  -e TZ=Asia/Seoul \
  -v $(pwd)/logs:/app/logs \
  -v /etc/localtime:/etc/localtime:ro \
  sony-stock-monitor:latest

# 컨테이너 관리
docker stop sony-stock-monitor
docker start sony-stock-monitor
docker restart sony-stock-monitor
docker rm -f sony-stock-monitor
```

### 시놀로지 NAS Container Manager

#### 이미지 빌드 (NAS에서)
1. **File Station**에서 프로젝트 파일 업로드
2. **Container Manager** → **이미지** → **추가** → **파일에서 추가**
3. **Dockerfile 경로**: `/docker/sony-stock-monitor/docker/Dockerfile`
4. **이미지명**: `sony-stock-monitor:latest`
5. **빌드** 실행

#### 컨테이너 생성 (NAS에서)
1. **Container Manager** → **컨테이너** → **새로 만들기**
2. **이미지**: `sony-stock-monitor:latest` 선택
3. **환경 변수**: `.env` 파일 내용 입력
4. **볼륨 설정**: `/docker/sony-stock-monitor/logs` → `/app/logs`
5. **자동 재시작** 활성화
6. **시작**

## 🧪 테스트 및 모니터링

### 초기 설정 테스트 (로컬 환경)

#### 자동 설정 및 테스트
```bash
# 프로젝트 초기화
python setup.py init

# 패키지 설치
python setup.py install

# 대화형 환경 설정
python setup.py setup

# 전체 시스템 테스트
python setup.py test
```

#### 개별 테스트
```bash
# Discord 연결 테스트
python setup.py test-discord

# 재고 모니터링 테스트
python setup.py test-stock
```

### 운영 중 테스트 발송

#### 대화형 테스트 (추천)
```bash
# 로컬 환경
python src/test_sender.py

# Docker 환경
docker exec sony-stock-monitor python src/test_sender.py
```

#### 명령행 테스트
```bash
# 재고 있음 테스트
docker exec sony-stock-monitor python src/test_sender.py --stock-available

# 품절 테스트
docker exec sony-stock-monitor python src/test_sender.py --out-of-stock

# 실제 재고 확인
docker exec sony-stock-monitor python src/test_sender.py --actual-check

# 알림 모드 테스트
docker exec sony-stock-monitor python src/test_sender.py --notification-mode

# 타임존 테스트
docker exec sony-stock-monitor python src/test_sender.py --timezone

# 모든 테스트
docker exec sony-stock-monitor python src/test_sender.py --all

# 사용자 정의 메시지
docker exec sony-stock-monitor python src/test_sender.py --custom "사용자 정의 메시지"
```

### 로그 모니터링

#### 실시간 로그 확인
```bash
# Docker 로그
docker logs -f sony-stock-monitor

# 로그 파일 직접 확인
tail -f logs/stock_monitor.log

# 컨테이너 내부 로그
docker exec sony-stock-monitor tail -f /app/logs/stock_monitor.log
```

#### 로그 분석
```bash
# 재고 확인 관련 로그
docker logs sony-stock-monitor | grep "재고 확인"

# 에러 로그만 확인
docker logs sony-stock-monitor | grep "ERROR"

# 특정 날짜 로그
docker logs --since "2025-06-24T00:00:00" sony-stock-monitor
```

## ⚙️ 운영 중 설정 변경

### 방법 1: .env 파일 수정 후 재시작 (간단)

```bash
# 1. .env 파일 수정
nano .env

# 2. 컨테이너 재시작만 (이미지 재빌드 불필요)
docker restart sony-stock-monitor

# 3. 변경사항 확인
docker logs -f sony-stock-monitor
```

### 방법 2: 런타임 설정 변경 도구 (고급)

#### 대화형 설정 변경
```bash
# 컨테이너 내부에서 실행
docker exec sony-stock-monitor python src/runtime_config_tool.py

# 로컬 환경에서 실행
python src/runtime_config_tool.py
```

#### 명령행으로 빠른 변경
```bash
# 알림 모드 변경
docker exec sony-stock-monitor python src/runtime_config_tool.py --notification-mode always

# 체크 주기 변경 (5분으로)
docker exec sony-stock-monitor python src/runtime_config_tool.py --check-interval 5

# 헬스체크 시간 변경
docker exec sony-stock-monitor python src/runtime_config_tool.py --health-times "10:00,14:00,18:00,22:00"

# 모니터링 URL 및 Selector 변경
docker exec sony-stock-monitor python src/runtime_config_tool.py --url "https://store.sony.co.kr/product-view/12345" --selector ".new-selector"

# 현재 설정 확인
docker exec sony-stock-monitor python src/runtime_config_tool.py --show

# 설정 초기화
docker exec sony-stock-monitor python src/runtime_config_tool.py --reset
```

### 방법 3: Docker Compose Override

**docker-compose.override.yml** 파일 생성:
```yaml
version: '3.8'

services:
  sony-stock-monitor:
    environment:
      - NOTIFICATION_MODE=always
      - CHECK_INTERVAL_MINUTES=5
      - HEALTH_CHECK_TIMES=10:00,14:00,18:00,22:00
```

```bash
# Override 파일과 함께 재시작
docker-compose down
docker-compose up -d
```

### 실시간 설정 변경 특징

#### ✅ 장점
- **무중단 서비스**: 컨테이너 재시작 없이 설정 변경
- **즉시 적용**: 변경 즉시 새 설정으로 동작
- **Discord 알림**: 설정 변경 시 자동 알림 발송
- **설정 추적**: `runtime_config.json` 파일로 변경사항 기록

#### ⚠️ 주의사항
- **영구 저장**: 컨테이너 재시작 시 `.env` 파일이 우선
- **영구 변경**: 영구적 변경은 `.env` 파일 수정 필요
- **권한**: 컨테이너 내부 파일 수정 권한 필요

## 🔍 재고 확인 로직

### 다양한 텍스트 추출 방법
서비스는 다음 6가지 방법으로 재고 정보를 추출합니다:

1. `element.text`
2. `get_attribute("textContent")`
3. `get_attribute("innerText")`
4. `get_attribute("innerHTML")`
5. JavaScript `textContent`
6. JavaScript `innerText`

### 재고 판단 기준
- 추출된 텍스트에 **"일시품절"** 포함 → **품절**
- **"일시품절"** 없음 → **재고 있음**

## 📱 Discord 알림 예시

### 서비스 시작
```
🚀 **Sony 재고 모니터링 서비스 시작** 🚀
⏰ 2025-06-24 16:33:19
📊 모니터링 URL: https://store.sony.co.kr/product-view/102263765
🔄 체크 주기: 3분
📋 알림 모드: 재고 있을때만
⚙️ 동적 설정 변경: 활성화
```

### 재고 상태 알림
```
🟢 **재고 있음!** 🟢
⏰ 2025-06-24 14:30:15
🔗 https://store.sony.co.kr/product-view/102263765
📋 알림 모드: 재고 있을때만
```

### 헬스체크
```
💚 **재고 모니터링 서비스 정상 동작** 💚
⏰ 2025-06-24 12:00:00
📊 모니터링 URL: https://store.sony.co.kr/product-view/102263765
📋 알림 모드: 재고 있을때만
```

### 설정 변경 알림
```
⚙️ **설정 변경 적용** ⚙️
⏰ 2025-06-24 16:45:30
🔄 체크 주기: 1분
📋 알림 모드: 매번 확인시마다
```

### 테스트 메시지
```
🟢 **[테스트] 재고 있음!** 🟢
⏰ 2025-06-24 14:30:15
🔗 https://store.sony.co.kr/product-view/102263765

⚠️ 이것은 테스트 메시지입니다.
```

## 🛠️ 트러블슈팅

### Docker 관련 문제

#### 빌드 실패
```bash
# 아키텍처 호환성 문제 (ARM64/AMD64)
docker build --platform linux/amd64 -f docker/Dockerfile -t sony-stock-monitor:latest .

# 캐시 없이 재빌드
docker build --no-cache -f docker/Dockerfile -t sony-stock-monitor:latest .

# 빌드 과정 상세 로그
docker build --progress=plain -f docker/Dockerfile -t sony-stock-monitor:latest .
```

#### 컨테이너 실행 오류
```bash
# 환경 변수 확인
docker run --rm --env-file .env sony-stock-monitor env

# 인터랙티브 모드로 디버깅
docker run -it --env-file .env sony-stock-monitor /bin/bash

# 포트 충돌 확인
docker ps -a
netstat -tulpn | grep :8000
```

#### 로그에서 문제 확인
```bash
# 컨테이너 로그 확인
docker logs sony-stock-monitor

# 실시간 에러 로그
docker logs -f sony-stock-monitor | grep ERROR

# 컨테이너 상태 확인
docker ps
```

### 일반적인 문제

#### 1. ChromeDriver 오류
- **Docker 환경**: 자동으로 해결됨 (Chromium 사용)
- **로컬 환경**: Chrome 브라우저와 ChromeDriver 버전 확인

#### 2. 재고 정보를 찾을 수 없음
- CSS Selector가 올바른지 확인
- 웹페이지 구조 변경 여부 확인
- 페이지 로딩 시간 고려

#### 3. Discord 메시지 전송 실패
- Webhook URL 유효성 확인
- 네트워크 연결 상태 확인
- Discord Rate Limit 확인

#### 4. 타임존 문제
- 컨테이너에 `TZ=Asia/Seoul` 환경변수 설정 확인
- `/etc/localtime` 볼륨 마운트 확인

### 디버깅 방법

#### 로그 레벨 증가
```python
# main.py에서 수정
logging.basicConfig(level=logging.DEBUG)
```

#### 테스트로 문제 파악
```bash
# 실제 재고 확인 테스트
docker exec sony-stock-monitor python src/test_sender.py --actual-check

# 타임존 테스트
docker exec sony-stock-monitor python src/test_sender.py --timezone
```

#### 컨테이너 내부 접근
```bash
# 컨테이너 내부 쉘 접속
docker exec sony-stock-monitor /bin/bash

# 수동으로 서비스 실행
python src/main.py
```

## 📈 성능 최적화

### 권장 설정
- **재고 확인 주기**: 3-5분 (너무 짧으면 IP 차단 위험)
- **Docker 메모리**: 최소 512MB, 권장 1GB
- **Docker CPU**: 최소 0.25 코어, 권장 0.5 코어

### Docker 리소스 제한
```yaml
# docker-compose.yml에서 설정
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### 모니터링 메트릭
```bash
# 리소스 사용량 확인
docker stats sony-stock-monitor

# 디스크 사용량 확인
docker system df

# 로그 파일 크기 관리
docker logs --tail 1000 sony-stock-monitor > latest.log
```

## 🔒 보안 고려사항

- **환경변수 보안**: `.env` 파일은 버전 관리에 포함하지 마세요
- **Webhook 보안**: Discord Webhook URL은 안전하게 보관하세요
- **컨테이너 보안**: 비특권 사용자(appuser)로 실행됩니다
- **네트워크 보안**: 필요한 포트만 외부에 노출
- **정기 업데이트**: Docker 이미지를 정기적으로 재빌드하여 보안 업데이트 적용

## 🚀 배포 시나리오

### 개발 환경
```bash
# 로컬에서 빠른 테스트
python src/main.py
```

### 스테이징 환경
```bash
# Docker Compose로 실제 환경과 유사하게
docker-compose up
```

### 프로덕션 환경
```bash
# 백그라운드 실행 + 자동 재시작
docker-compose up -d

# 또는 시놀로지 NAS Container Manager 사용
```

### 무중단 업데이트
```bash
# 새 이미지 빌드
docker-compose build

# 롤링 업데이트
docker-compose up -d --no-deps sony-stock-monitor
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch
3. Test with both local and Docker environments
4. Commit your changes
5. Push to the branch
6. Create a Pull Request

## 📞 지원 및 문의

문제 발생 시 다음을 순서대로 확인해 주세요:

1. **로그 확인**: `docker logs sony-stock-monitor`
2. **환경 변수**: `.env` 파일 설정 확인
3. **Docker 상태**: `docker ps` 확인
4. **네트워크 연결**: Sony 웹사이트 및 Discord 접근 가능 여부
5. **테스트 실행**: `python src/test_sender.py --actual-check`

### 자주 묻는 질문 (FAQ)

**Q: 재고 알림이 오지 않아요**
A: `--actual-check` 테스트로 재고 상태 확인 후, CSS Selector가 올바른지 검증하세요.

**Q: 시간이 잘못 표시되어요**
A: 타임존 설정을 확인하고 `--timezone` 테스트를 실행하세요.

**Q: 설정을 바꿔도 적용이 안 되어요**
A: 런타임 설정 도구를 사용하거나 컨테이너를 재시작하세요.

추가 도움이 필요한 경우 Issues를 통해 문의해 주세요.