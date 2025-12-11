# PICU 프로젝트에서 재사용 가능한 개념

**작성일**: 2025-12-08
**목적**: bigdata/PICU 프로젝트에서 FocusMate로 접목 가능한 아키텍처 패턴 및 구현 개념 정리

---

## 📋 개요

PICU 프로젝트는 **2-Tier 분산 데이터 파이프라인** 시스템으로, 여러 검증된 아키텍처 패턴과 구현 방식을 포함하고 있습니다.
이 문서는 FocusMate 프로젝트에 직접 적용 가능한 개념들을 정리합니다.

---

## 🎯 재사용 가능한 핵심 개념

### 1. 설정 관리 시스템 (Config Management)

#### PICU의 ConfigManager 패턴

**위치**: `PICU/cointicker/gui/core/config_manager.py`

**핵심 특징**:
- ✅ **환경 변수 우선순위**: 환경 변수 → 설정 파일 → 기본값
- ✅ **YAML 기반 설정**: 구조화된 설정 관리
- ✅ **자동 템플릿 생성**: example 파일에서 자동 복사
- ✅ **캐싱 메커니즘**: 메모리 + 디스크 캐시 (TTL 기반)
- ✅ **타입 안전성**: 점 표기법으로 중첩 설정 접근

**FocusMate 적용 방안**:

```python
# 현재: Pydantic Settings만 사용
# 개선: ConfigManager 패턴 추가

class ConfigManager:
    """PICU 스타일 설정 관리자"""

    def __init__(self):
        self.config_dir = Path("config")
        self.configs: Dict[str, dict] = {}
        self.cache = CacheManager()

    def get_config(self, config_name: str, key: str = None, default: Any = None):
        """환경 변수 우선, 설정 파일 fallback"""
        # 1. 환경 변수 확인
        env_value = os.environ.get(key.upper().replace(".", "_"))
        if env_value:
            return self._parse_env_value(env_value)

        # 2. YAML 설정 파일 확인
        config = self.load_config(config_name)
        if config and key:
            return self._get_nested_value(config, key.split("."))

        # 3. 기본값 반환
        return default
```

**장점**:
- 개발/프로덕션 환경 분리 용이
- 설정 파일 버전 관리 가능
- 동적 설정 변경 지원

---

### 2. 로깅 시스템 (Logging System)

#### PICU의 통합 로깅 패턴

**위치**: `PICU/cointicker/shared/logger.py`

**핵심 특징**:
- ✅ **중앙 집중식 로거**: `setup_logger()` 유틸리티
- ✅ **파일 + 콘솔 핸들러**: 이중 출력
- ✅ **자동 디렉토리 생성**: 로그 파일 경로 자동 생성
- ✅ **UTF-8 인코딩**: 한글 로그 지원
- ✅ **프로세스별 로그 분리**: 모듈별 독립 로그 파일

**FocusMate 적용 방안**:

```python
# 현재: FastAPI 기본 로깅
# 개선: PICU 스타일 통합 로깅

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO):
    """PICU 스타일 로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (지정된 경우)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# 사용 예시
timer_logger = setup_logger("timer", "logs/timer.log")
room_logger = setup_logger("room", "logs/room.log")
```

**장점**:
- 모듈별 로그 분리로 디버깅 용이
- 파일 로그로 운영 이력 추적
- UTF-8 지원으로 한글 로그 안전

---

### 3. 모니터링 시스템 (Monitoring System)

#### PICU의 ProcessMonitor 패턴

**위치**: `PICU/cointicker/gui/modules/process_monitor.py`

**핵심 특징**:
- ✅ **프로세스 상태 추적**: 실시간 프로세스 모니터링
- ✅ **로그 버퍼링**: 최근 N줄 로그 메모리 보관
- ✅ **통계 수집**: CPU, 메모리, 실행 시간 추적
- ✅ **비동기 모니터링**: 별도 스레드에서 모니터링

**FocusMate 적용 방안**:

```python
# WebSocket 연결 모니터링 추가

class WebSocketMonitor:
    """WebSocket 연결 모니터링"""

    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
        self.stats: Dict[str, Dict] = {}
        self.monitoring_threads: Dict[str, threading.Thread] = {}

    def start_monitoring(self, room_id: str):
        """방별 연결 모니터링 시작"""
        self.stats[room_id] = {
            "start_time": datetime.now().isoformat(),
            "total_connections": 0,
            "current_connections": 0,
            "messages_sent": 0,
            "messages_received": 0
        }

        # 별도 스레드에서 통계 수집
        thread = threading.Thread(
            target=self._collect_stats,
            args=(room_id,),
            daemon=True
        )
        thread.start()
        self.monitoring_threads[room_id] = thread

    def _collect_stats(self, room_id: str):
        """통계 수집 (주기적)"""
        while room_id in self.stats:
            # 연결 수, 메시지 수 등 수집
            self.stats[room_id]["current_connections"] = len(
                self.connections.get(room_id, [])
            )
            time.sleep(5)  # 5초마다 수집
```

**장점**:
- 실시간 서비스 상태 파악
- 성능 병목 지점 식별
- 운영 메트릭 수집

---

### 4. 모듈화 아키텍처 (Modular Architecture)

#### PICU의 GUI 모듈 시스템

**위치**: `PICU/cointicker/gui/modules/`

**핵심 특징**:
- ✅ **인터페이스 기반 설계**: `ModuleInterface` 추상 클래스
- ✅ **의존성 관리**: 모듈 간 의존성 자동 해결
- ✅ **상태 관리**: 시작/중지/재시작 상태 추적
- ✅ **에러 복구**: 자동 재시도 메커니즘

**FocusMate 적용 방안**:

```python
# 기능별 모듈화 (현재는 레이어드 아키텍처만 있음)

class ModuleInterface(ABC):
    """모듈 인터페이스"""

    @abstractmethod
    def initialize(self, config: dict) -> bool:
        """모듈 초기화"""
        pass

    @abstractmethod
    def start(self) -> bool:
        """모듈 시작"""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """모듈 중지"""
        pass

    @property
    @abstractmethod
    def status(self) -> str:
        """모듈 상태"""
        pass

# 타이머 모듈
class TimerModule(ModuleInterface):
    def __init__(self):
        self.status = "stopped"
        self.timer_service = None

    def initialize(self, config: dict) -> bool:
        self.timer_service = TimerService(config)
        return True

    def start(self) -> bool:
        self.timer_service.start()
        self.status = "running"
        return True

    def stop(self) -> bool:
        self.timer_service.stop()
        self.status = "stopped"
        return True

# 모듈 매니저
class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, ModuleInterface] = {}

    def register_module(self, name: str, module: ModuleInterface):
        self.modules[name] = module

    def start_all(self):
        for name, module in self.modules.items():
            module.start()
```

**장점**:
- 기능별 독립 개발 가능
- 테스트 용이성 향상
- 동적 모듈 로드/언로드

---

### 5. 스케줄링 시스템 (Scheduling System)

#### PICU의 Orchestrator 패턴

**위치**: `PICU/cointicker/master-node/orchestrator.py`

**핵심 특징**:
- ✅ **주기적 작업 실행**: cron 스타일 스케줄링
- ✅ **작업 의존성 관리**: 선행 작업 완료 후 실행
- ✅ **에러 처리**: 실패 시 재시도 로직
- ✅ **상태 추적**: 작업 실행 상태 로깅

**FocusMate 적용 방안**:

```python
# 세션 통계 집계 스케줄러

class SessionStatsScheduler:
    """세션 통계 주기적 집계"""

    def __init__(self):
        self.stats_service = StatsService()
        self.running = False

    async def start(self):
        """스케줄러 시작"""
        self.running = True

        # 매 시간마다 통계 집계
        while self.running:
            await self._aggregate_stats()
            await asyncio.sleep(3600)  # 1시간

    async def _aggregate_stats(self):
        """통계 집계"""
        try:
            # 오늘 완료된 세션 집계
            today = datetime.now().date()
            sessions = await self.stats_service.get_sessions_by_date(today)

            # 집계 데이터 생성
            aggregated = {
                "date": today.isoformat(),
                "total_sessions": len(sessions),
                "total_focus_time": sum(s.duration for s in sessions),
                "avg_session_duration": sum(s.duration for s in sessions) / len(sessions) if sessions else 0
            }

            # 저장
            await self.stats_service.save_aggregated_stats(aggregated)

        except Exception as e:
            logger.error(f"통계 집계 실패: {e}")
```

**장점**:
- 주기적 작업 자동화
- 배치 처리 최적화
- 시스템 부하 분산

---

### 6. 캐싱 시스템 (Caching System)

#### PICU의 CacheManager 패턴

**위치**: `PICU/cointicker/gui/core/cache_manager.py`

**핵심 특징**:
- ✅ **TTL 기반 캐싱**: 시간 기반 캐시 만료
- ✅ **팩토리 패턴**: 캐시 미스 시 자동 생성
- ✅ **메모리 효율**: LRU 캐시 전략

**FocusMate 적용 방안**:

```python
# 타이머 상태 캐싱

class TimerCacheManager:
    """타이머 상태 캐싱"""

    def __init__(self):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = 60.0  # 60초

    def get(self, key: str, ttl: float = None, factory: Callable = None):
        """캐시에서 가져오기"""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
            else:
                del self.cache[key]

        # 캐시 미스: 팩토리로 생성
        if factory:
            value = factory()
            self.set(key, value, ttl)
            return value

        return None

    def set(self, key: str, value: Any, ttl: float = None):
        """캐시에 저장"""
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)

# 사용 예시
cache = TimerCacheManager()

# 타이머 상태 캐싱 (1분)
timer_state = cache.get(
    f"timer:{room_id}",
    ttl=60.0,
    factory=lambda: timer_service.get_state(room_id)
)
```

**장점**:
- 데이터베이스 부하 감소
- 응답 시간 개선
- 메모리 효율적 관리

---

### 7. 에러 처리 및 재시도 (Error Handling & Retry)

#### PICU의 RetryUtils 패턴

**위치**: `PICU/cointicker/gui/core/retry_utils.py`

**핵심 특징**:
- ✅ **지수 백오프**: 재시도 간격 점진적 증가
- ✅ **최대 재시도 횟수**: 무한 재시도 방지
- ✅ **예외 타입별 처리**: 특정 예외만 재시도

**FocusMate 적용 방안**:

```python
# WebSocket 연결 재시도

from functools import wraps
import asyncio
import time

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """지수 백오프 재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise

                    logger.warning(
                        f"{func.__name__} 실패 (시도 {attempt + 1}/{max_retries}): {e}"
                    )

                    await asyncio.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)

            raise Exception(f"{func.__name__} 최대 재시도 횟수 초과")
        return wrapper
    return decorator

# 사용 예시
@retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
async def send_websocket_message(websocket: WebSocket, message: dict):
    """WebSocket 메시지 전송 (재시도 포함)"""
    await websocket.send_json(message)
```

**장점**:
- 일시적 오류 자동 복구
- 시스템 안정성 향상
- 사용자 경험 개선

---

## 📊 비교표: 현재 vs 개선안

| 개념 | PICU 구현 | FocusMate 현재 | 적용 우선순위 |
|------|----------|---------------|--------------|
| **설정 관리** | ConfigManager (YAML + 환경변수) | Pydantic Settings (환경변수만) | ⭐⭐⭐ 높음 |
| **로깅** | 통합 로거 (파일 + 콘솔) | FastAPI 기본 로깅 | ⭐⭐⭐ 높음 |
| **모니터링** | ProcessMonitor (실시간 추적) | 없음 | ⭐⭐ 중간 |
| **모듈화** | ModuleInterface 기반 | 레이어드 아키텍처만 | ⭐⭐ 중간 |
| **스케줄링** | Orchestrator (주기적 작업) | 없음 | ⭐ 낮음 |
| **캐싱** | CacheManager (TTL 기반) | 없음 | ⭐⭐ 중간 |
| **재시도** | RetryUtils (지수 백오프) | 없음 | ⭐⭐ 중간 |

---

## 🚀 적용 로드맵

### Phase 1: 필수 개선 (즉시 적용)

1. **설정 관리 시스템**
   - ConfigManager 클래스 구현
   - YAML 설정 파일 지원
   - 환경 변수 우선순위 적용

2. **로깅 시스템**
   - 통합 로거 유틸리티 구현
   - 파일 로그 핸들러 추가
   - 모듈별 로그 분리

### Phase 2: 성능 개선 (단기)

3. **캐싱 시스템**
   - TimerCacheManager 구현
   - 타이머 상태 캐싱
   - 통계 데이터 캐싱

4. **에러 처리**
   - RetryUtils 구현
   - WebSocket 재연결 로직
   - 데이터베이스 재시도

### Phase 3: 운영 개선 (중기)

5. **모니터링 시스템**
   - WebSocketMonitor 구현
   - 실시간 통계 수집
   - 성능 메트릭 추적

6. **스케줄링 시스템**
   - SessionStatsScheduler 구현
   - 주기적 통계 집계
   - 배치 작업 처리

---

## 📝 참고 파일

### PICU 프로젝트

- **설정 관리**: `PICU/cointicker/gui/core/config_manager.py`
- **로깅**: `PICU/cointicker/shared/logger.py`
- **모니터링**: `PICU/cointicker/gui/modules/process_monitor.py`
- **캐싱**: `PICU/cointicker/gui/core/cache_manager.py`
- **재시도**: `PICU/cointicker/gui/core/retry_utils.py`
- **스케줄링**: `PICU/cointicker/master-node/orchestrator.py`

### FocusMate 프로젝트

- **현재 설정**: `FocusMate/backend/app/core/config.py`
- **WebSocket**: `FocusMate/backend/app/infrastructure/websocket/manager.py`

---

## ✅ 결론

PICU 프로젝트의 다음 개념들이 FocusMate에 직접 적용 가능합니다:

1. ✅ **설정 관리**: YAML + 환경 변수 하이브리드 방식
2. ✅ **로깅**: 파일 + 콘솔 이중 출력
3. ✅ **모니터링**: 실시간 프로세스 상태 추적
4. ✅ **캐싱**: TTL 기반 메모리 캐싱
5. ✅ **재시도**: 지수 백오프 패턴

이러한 패턴들을 적용하면 FocusMate의 **운영 안정성**과 **유지보수성**이 크게 향상됩니다.

