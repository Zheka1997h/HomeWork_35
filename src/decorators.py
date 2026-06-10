# decorators.py
import datetime
import functools
import logging
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования вызовов функций.

    Args:
        filename: имя файла для записи логов. Если None, логи выводятся в консоль.

    Returns:
        Декоратор, который логирует вызовы функции.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if filename:
                logger = logging.getLogger(func_name)
                logger.handlers.clear()  # Очищаем старые обработчики

                handler = logging.FileHandler(filename, mode="a")
                formatter = logging.Formatter("%(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            else:
                logger = None

            try:
                result = func(*args, **kwargs)
                log_message = f"{timestamp} {func_name} ok"
                if logger:
                    logger.info(log_message)
                    handler.close()
                    logger.removeHandler(handler)
                else:
                    print(log_message)
                return result
            except Exception as e:
                error_type = type(e).__name__
                inputs = f"Inputs: {args}, {kwargs}"
                log_message = f"{timestamp} {func_name} error: {error_type}. {inputs}"
                if logger:
                    logger.error(log_message)
                    handler.close()
                    logger.removeHandler(handler)
                else:
                    print(log_message)
                raise

        return wrapper

    return decorator
