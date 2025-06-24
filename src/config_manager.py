#!/usr/bin/env python3
"""
런타임 설정 관리자
- 실행 중인 서비스의 설정을 동적으로 변경
- 파일 기반 설정 변경 감지
- 환경변수 실시간 업데이트
"""

import os
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv, set_key
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_file='.env'):
        self.config_file = config_file
        self.runtime_config_file = 'runtime_config.json'
        self.callbacks = []
        self.current_config = {}
        self.load_config()
        
    def load_config(self):
        """현재 설정 로드"""
        load_dotenv(self.config_file)
        
        self.current_config = {
            'NOTIFICATION_MODE': os.getenv('NOTIFICATION_MODE', 'stock_available_only'),
            'CHECK_INTERVAL_MINUTES': int(os.getenv('CHECK_INTERVAL_MINUTES', 3)),
            'HEALTH_CHECK_TIMES': os.getenv('HEALTH_CHECK_TIMES', '09:00,12:00,15:00,18:00,21:00,00:00'),
            'WEBSITE_URL': os.getenv('WEBSITE_URL', ''),
            'STOCK_SELECTOR': os.getenv('STOCK_SELECTOR', ''),
        }
        
        logger.info(f"설정 로드 완료: {self.current_config}")
        
    def save_runtime_config(self, new_config):
        """런타임 설정을 JSON 파일에 저장"""
        try:
            with open(self.runtime_config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            logger.info(f"런타임 설정 저장: {new_config}")
        except Exception as e:
            logger.error(f"런타임 설정 저장 실패: {str(e)}")
            
    def load_runtime_config(self):
        """런타임 설정 로드"""
        try:
            if os.path.exists(self.runtime_config_file):
                with open(self.runtime_config_file, 'r', encoding='utf-8') as f:
                    runtime_config = json.load(f)
                    
                # 환경변수 업데이트
                for key, value in runtime_config.items():
                    os.environ[key] = str(value)
                    if key in self.current_config:
                        self.current_config[key] = value
                    
                logger.info(f"런타임 설정 적용: {runtime_config}")
                return runtime_config
        except Exception as e:
            logger.error(f"런타임 설정 로드 실패: {str(e)}")
        return None
        
    def update_config(self, **kwargs):
        """설정 업데이트"""
        changed = False
        old_config = self.current_config.copy()
        
        for key, value in kwargs.items():
            if key in self.current_config:
                if self.current_config[key] != value:
                    self.current_config[key] = value
                    os.environ[key] = str(value)
                    changed = True
                    logger.info(f"설정 변경: {key} = {old_config[key]} → {value}")
                    
        if changed:
            self.save_runtime_config(self.current_config)
            logger.info(f"런타임 설정 저장 완료")
            
            # 콜백 함수들 실행
            for callback in self.callbacks:
                try:
                    callback(old_config, self.current_config)
                    logger.info("설정 변경 콜백 실행 완료")
                except Exception as e:
                    logger.error(f"콜백 함수 실행 오류: {str(e)}")
                    
        return changed
        
    def register_callback(self, callback):
        """설정 변경 시 실행할 콜백 함수 등록"""
        self.callbacks.append(callback)
        
    def get_config(self, key=None):
        """현재 설정 조회"""
        # runtime_config.json 파일이 있으면 다시 로드
        if os.path.exists(self.runtime_config_file):
            try:
                with open(self.runtime_config_file, 'r', encoding='utf-8') as f:
                    runtime_config = json.load(f)
                    # 런타임 설정으로 current_config 업데이트
                    for k, v in runtime_config.items():
                        if k in self.current_config:
                            self.current_config[k] = v
                            os.environ[k] = str(v)
            except Exception as e:
                logger.error(f"runtime_config.json 읽기 실패: {str(e)}")
        
        if key:
            return self.current_config.get(key)
        return self.current_config.copy()
        
    def reset_to_env_file(self):
        """환경변수 파일로 설정 초기화"""
        if os.path.exists(self.runtime_config_file):
            os.remove(self.runtime_config_file)
        self.load_config()
        logger.info("설정을 .env 파일로 초기화")

class ConfigFileWatcher(FileSystemEventHandler):
    """설정 파일 변경 감지"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        
    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path.endswith('.env') or event.src_path.endswith('runtime_config.json'):
                logger.info(f"설정 파일 변경 감지: {event.src_path}")
                time.sleep(0.1)  # 파일 쓰기 완료 대기
                
                if event.src_path.endswith('runtime_config.json'):
                    self.config_manager.load_runtime_config()
                else:
                    self.config_manager.load_config()

def start_config_watcher(config_manager):
    """설정 파일 감시 시작"""
    event_handler = ConfigFileWatcher(config_manager)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    logger.info("설정 파일 감시 시작")
    return observer

# 싱글톤 인스턴스
_config_manager = None

def get_config_manager():
    """ConfigManager 싱글톤 인스턴스 반환"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

if __name__ == "__main__":
    # 테스트 코드
    import time
    
    logging.basicConfig(level=logging.INFO)
    
    config = ConfigManager()
    
    def config_changed(old_config, new_config):
        print(f"설정 변경됨: {old_config} → {new_config}")
        
    config.register_callback(config_changed)
    
    # 설정 파일 감시 시작
    observer = start_config_watcher(config)
    
    try:
        print("설정 관리자 테스트 시작...")
        print("runtime_config.json 파일을 수정해보세요.")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        print("설정 관리자 종료")