import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class DiscordNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self._validate_webhook()
        
    def _validate_webhook(self):
        """Webhook URL 유효성 검사"""
        if not self.webhook_url:
            raise ValueError("Discord Webhook URL이 설정되지 않았습니다")
        if not self.webhook_url.startswith('https://discord.com/api/webhooks/'):
            raise ValueError("올바른 Discord Webhook URL 형식이 아닙니다")
            
    def send_message(self, message, max_retries=3):
        """Discord 채널에 메시지 전송"""
        for attempt in range(max_retries):
            try:
                # Discord 메시지 페이로드
                payload = {
                    "content": message,
                    "username": "Sony 재고 알림봇",
                    "avatar_url": "https://www.sony.co.kr/image/4c39f1f7ed0a9b0e24e7d3b97b836b9e?fmt=png-scaleup&wid=20&hei=20"
                }
                
                # Discord Webhook 요청
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )
                
                # 응답 확인
                if response.status_code == 204:
                    logger.info("Discord 메시지 전송 성공")
                    return True
                elif response.status_code == 429:
                    # Rate limit 처리
                    retry_after = response.json().get('retry_after', 1)
                    logger.warning(f"Discord Rate limit - {retry_after}초 후 재시도")
                    time.sleep(retry_after)
                    continue
                else:
                    logger.error(f"Discord 메시지 전송 실패: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"Discord 메시지 전송 타임아웃 (시도 {attempt + 1})")
            except requests.exceptions.RequestException as e:
                logger.error(f"Discord 메시지 전송 오류 (시도 {attempt + 1}): {str(e)}")
            except Exception as e:
                logger.error(f"예상치 못한 오류 (시도 {attempt + 1}): {str(e)}")
                
            # 재시도 대기
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # 점진적 대기 시간 증가
                logger.info(f"{wait_time}초 후 재시도")
                time.sleep(wait_time)
                
        logger.error("모든 Discord 메시지 전송 시도 실패")
        return False
        
    def send_embed_message(self, title, description, color=0x1E90FF, fields=None):
        """Discord Embed 메시지 전송"""
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "Sony 재고 모니터링 서비스"
            }
        }
        
        if fields:
            embed["fields"] = fields
            
        payload = {
            "username": "Sony 재고 알림봇",
            "avatar_url": "https://www.sony.co.kr/image/4c39f1f7ed0a9b0e24e7d3b97b836b9e?fmt=png-scaleup&wid=20&hei=20",
            "embeds": [embed]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info("Discord Embed 메시지 전송 성공")
                return True
            else:
                logger.error(f"Discord Embed 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord Embed 메시지 전송 오류: {str(e)}")
            return False
            
    def test_webhook(self):
        """Webhook 연결 테스트"""
        test_message = f"🧪 **Discord Webhook 연결 테스트** 🧪\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 연결이 정상적으로 작동합니다!"
        return self.send_message(test_message)