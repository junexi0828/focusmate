"""로깅 설정 및 구조화된 로깅 유틸리티.

ISO/IEC 25010: Maintainability, Reliability
"""

import logging
import sys
from typing import Any, Dict, Optional

from app.core.config import settings


def setup_logging() -> None:
    """애플리케이션 로깅 설정."""
    import logging

    # 로그 레벨 설정
    log_level = getattr(logging, settings.APP_LOG_LEVEL.upper(), logging.INFO)

    # 기본 포맷 설정
    log_format = (
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s " "[%(filename)s:%(lineno)d]"
    )

    # 구조화된 로깅 포맷 (JSON 형식, 프로덕션 환경)
    if settings.APP_ENV == "production":
        # 프로덕션에서는 JSON 형식으로 로깅 (Cloudflare, Vercel 등에서 파싱 용이)
        import json
        import logging.handlers

        class JSONFormatter(logging.Formatter):
            """JSON 형식 로그 포맷터."""

            def format(self, record: logging.LogRecord) -> str:
                """로그 레코드를 JSON 형식으로 변환."""
                log_data = {
                    "timestamp": self.formatTime(record, self.datefmt),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                # 추가 컨텍스트가 있으면 포함 (hasattr로 안전하게 확인)
                if hasattr(record, "request_id"):
                    log_data["request_id"] = getattr(record, "request_id")
                if hasattr(record, "user_id"):
                    log_data["user_id"] = getattr(record, "user_id")
                if hasattr(record, "error_code"):
                    log_data["error_code"] = getattr(record, "error_code")
                if hasattr(record, "error_details"):
                    log_data["error_details"] = getattr(record, "error_details")

                # 예외 정보가 있으면 포함
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)

                return json.dumps(log_data, ensure_ascii=False)

        formatter = JSONFormatter()
    else:
        # 개발 환경에서는 읽기 쉬운 포맷
        formatter = logging.Formatter(log_format)

    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 기존 핸들러 제거
    root_logger.handlers.clear()

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 프로덕션 환경에서는 파일 핸들러도 추가 (선택적)
    if settings.APP_ENV == "production":
        try:
            from logging.handlers import RotatingFileHandler
            import os

            log_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs"
            )
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                os.path.join(log_dir, "app.log"),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            # 파일 핸들러 생성 실패해도 계속 진행
            pass

    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 가져오기.

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any,
) -> None:
    """컨텍스트 정보와 함께 로그 기록.

    Args:
        logger: 로거 인스턴스
        level: 로그 레벨 (logging.INFO, logging.ERROR 등)
        message: 로그 메시지
        **context: 추가 컨텍스트 정보
    """
    extra = {k: v for k, v in context.items()}
    logger.log(level, message, extra=extra)


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Exception,
    **context: Any,
) -> None:
    """에러와 컨텍스트 정보를 함께 로그 기록.

    Args:
        logger: 로거 인스턴스
        message: 로그 메시지
        error: 예외 객체
        **context: 추가 컨텍스트 정보
    """
    extra = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **{k: v for k, v in context.items()},
    }
    logger.error(message, exc_info=error, extra=extra)
