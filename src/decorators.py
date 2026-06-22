import datetime
import functools
import logging
from typing import Any, Callable


def log(filename: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для логирования вызовов функций.

    Args:
        filename: Путь к файлу логов. Если None, логи выводятся в консоль.

    Returns:
        Декоратор, который логирует вызовы функции.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            func_name: str = func.__name__
            timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            logger: logging.Logger | None = None
            handler: logging.FileHandler | None = None

            if filename:
                logger = logging.getLogger(func_name)
                logger.handlers.clear()  # Очищаем старые обработчики

                handler = logging.FileHandler(filename, mode="a")
                formatter = logging.Formatter("%(message)s")
                handler.setFormatter(formatter)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)

            try:
                result: Any = func(*args, **kwargs)
                log_message: str = f"{timestamp} {func_name} ok"
                if logger and handler:
                    logger.info(log_message)
                    handler.close()
                    logger.removeHandler(handler)
                else:
                    print(log_message)
                return result
            except Exception as e:
                error_type: str = type(e).__name__
                inputs: str = f"Inputs: {args}, {kwargs}"
                log_message = f"{timestamp} {func_name} error: {error_type}. {inputs}"
                if logger and handler:
                    logger.error(log_message)
                    handler.close()
                    logger.removeHandler(handler)
                else:
                    print(log_message)
                raise

        return wrapper

    return decorator
