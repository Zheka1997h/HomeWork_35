# -*- coding: utf-8 -*-
"""Компактные тесты декоратора log() со 100% покрытием."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterator

import pytest

from src.decorators import log

# ==================== ФИКСТУРА ИЗОЛЯЦИИ ====================


@pytest.fixture(autouse=True)
def isolate_loggers(tmp_path: Path) -> Iterator[Dict[str, str]]:
    """Изолирует логгеры в tmp_path для каждого теста.

    Args:
        tmp_path: Фикстура pytest для создания временных файлов.

    Yields:
        Словарь с путями к лог-файлам.
    """
    success_path: Path = tmp_path / "success.log"
    errors_path: Path = tmp_path / "erros.log"

    success_log: str = str(success_path)
    errors_log: str = str(errors_path)

    # Очищаем старые хэндлеры
    logger_name: str
    for logger_name in ["success", "errors"]:
        logger: logging.Logger = logging.getLogger(logger_name)
        handler: logging.Handler
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    # Создаём новые хэндлеры с временными путями
    success_logger: logging.Logger = logging.getLogger("success")
    success_handler: logging.FileHandler = logging.FileHandler(success_log, mode="a", encoding="utf-8")
    success_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    success_logger.addHandler(success_handler)

    error_logger: logging.Logger = logging.getLogger("errors")
    error_handler: logging.FileHandler = logging.FileHandler(errors_log, mode="a", encoding="utf-8")
    error_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    error_logger.addHandler(error_handler)

    # Сохраняем пути для доступа из тестов
    monkeypatch_paths: Dict[str, str] = {
        "success_log": success_log,
        "errors_log": errors_log,
    }

    yield monkeypatch_paths

    # Очистка после теста
    for logger_name in ["success", "errors"]:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


# ==================== ТЕСТЫ ====================


def test_successful_execution(isolate_loggers: Dict[str, str]) -> None:
    """Тест успешного выполнения: возврат значения + запись в success.log."""

    @log()
    def add(a: int, b: int) -> int:
        return a + b

    result: int = add(3, 5)

    assert result == 8, "Декоратор не должен менять возвращаемое значение"

    content: str = open(isolate_loggers["success_log"], encoding="utf-8").read()
    assert "add ok" in content
    assert "args=(3, 5)" in content
    assert "kwargs={}" in content


def test_error_execution(isolate_loggers: Dict[str, str]) -> None:
    """Тест ошибки: исключение пробрасывается + запись в errors.log."""

    @log()
    def fail() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        fail()

    content: str = open(isolate_loggers["errors_log"], encoding="utf-8").read()
    assert "fail error: ValueError" in content
    assert "args=()" in content
    assert "Message: boom" in content


def test_kwargs_logging(isolate_loggers: Dict[str, str]) -> None:
    """Тест логирования именованных аргументов."""

    @log()
    def greet(name: str, age: int = 25) -> str:
        return f"{name}-{age}"

    result: str = greet("Alice", age=30)

    assert result == "Alice-30"

    content: str = open(isolate_loggers["success_log"], encoding="utf-8").read()
    assert "greet ok" in content
    assert "args=('Alice',)" in content
    assert "kwargs={'age': 30}" in content


def test_preserves_metadata() -> None:
    """Тест, что functools.wraps сохраняет имя и docstring."""

    @log()
    def my_func() -> None:
        """Моя документация."""

    assert my_func.__name__ == "my_func"
    assert my_func.__doc__ == "Моя документация."


def test_logs_separation(isolate_loggers: Dict[str, str]) -> None:
    """Тест, что успехи и ошибки пишутся в разные файлы."""

    @log()
    def ok_func() -> int:
        return 1

    @log()
    def err_func() -> None:
        raise RuntimeError("err")

    ok_func()
    with pytest.raises(RuntimeError):
        err_func()

    success_content: str = open(isolate_loggers["success_log"], encoding="utf-8").read()
    error_content: str = open(isolate_loggers["errors_log"], encoding="utf-8").read()

    assert "ok_func ok" in success_content
    assert "err_func error" not in success_content

    assert "err_func error: RuntimeError" in error_content
    assert "ok_func ok" not in error_content
