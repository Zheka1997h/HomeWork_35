# -*- coding: utf-8 -*-
import datetime
import functools
import logging
import os
from typing import Any, Callable

# Создаём папку logs, если её нет
os.makedirs("logs", exist_ok=True)


# ==================== ЛОГГЕР УСПЕШНЫХ ОПЕРАЦИЙ ====================
success_logger = logging.getLogger("success")
success_logger.setLevel(logging.INFO)
success_logger.propagate = False

# Очищаем старые обработчики, если есть
if not success_logger.handlers:
    success_handler = logging.FileHandler("logs/success.log", mode="a", encoding="utf-8", errors="replace")
    success_formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    success_handler.setFormatter(success_formatter)
    success_logger.addHandler(success_handler)


# ==================== ЛОГГЕР ОШИБОК ====================
error_logger = logging.getLogger("errors")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False

if not error_logger.handlers:
    error_handler = logging.FileHandler("logs/errors.log", mode="a", encoding="utf-8", errors="replace")
    error_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)


def log() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для логирования вызовов функций.

    Успешные вызовы пишутся в logs/success.log
    Ошибки пишутся в logs/errors.log
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name: str = func.__name__
            timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # noqa: F841

            try:
                result: Any = func(*args, **kwargs)

                # ✅ Успех → success.log
                success_logger.info(f"{func_name} ok | args={args} kwargs={kwargs}")

                return result

            except Exception as e:
                error_type: str = type(e).__name__
                inputs: str = f"args={args} kwargs={kwargs}"

                # ❌ Ошибка → errors.log
                error_logger.error(f"{func_name} error: {error_type}. {inputs}. Message: {e}")

                raise

        return wrapper

    return decorator
