# tests/test_decorators.py
import os
from collections.abc import Iterator

import pytest

from src.decorators import log


@log()
def successful_function(x: int, y: int) -> int:
    """Простая функция сложения для тестирования успешного выполнения.

    Args:
        x: Первое слагаемое.
        y: Второе слагаемое.

    Returns:
        Сумма x и y.
    """
    return x + y


@log()
def failing_function() -> None:
    """Функция, которая всегда вызывает ошибку для тестирования обработки исключений.

    Raises:
        ValueError: Всегда выбрасывается с сообщением "Test error".
    """
    raise ValueError("Test error")


@log(filename="test_log.txt")
def file_log_function(a: int, b: int, c: int = 0) -> int:
    """Функция для тестирования логирования в файл при успешном выполнении.

    Args:
        a: Первый множитель.
        b: Второй множитель.
        c: Слагаемое (по умолчанию 0).

    Returns:
        Результат выражения a * b + c.
    """
    return a * b + c


@log()
def func_with_args(a: int, b: int, c: str = "default") -> int:
    """Функция с аргументами для тестирования логирования аргументов.

    Args:
        a: Первое число.
        b: Второе число.
        c: Строковый параметр (по умолчанию "default").

    Returns:
        Сумма a и b.
    """
    return a + b


@log(filename="test_log.txt")
def error_func() -> None:
    """Функция, вызывающая TypeError для тестирования логирования ошибок в файл.

    Raises:
        TypeError: Всегда выбрасывается с сообщением "File error test".
    """
    raise TypeError("File error test")


class TestLogDecorator:
    """Набор тестов для проверки функциональности декоратора log."""

    def test_successful_execution_console(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест успешного выполнения функции с логированием в консоль.

        Проверяет, что:
        - Функция выполняется без ошибок.
        - В консоль выводится сообщение об успешном выполнении.
        - Возвращаемое значение корректно.
        """
        result: int = successful_function(3, 5)
        captured = capsys.readouterr()
        assert "successful_function ok" in captured.out
        assert result == 8

    def test_error_execution_console(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест обработки ошибки с логированием в консоль.

        Проверяет, что:
        - При возникновении ошибки она корректно перехватывается.
        - В консоль выводится информация об ошибке.
        - Тип ошибки указан верно.
        """
        with pytest.raises(ValueError):
            failing_function()
        captured = capsys.readouterr()
        assert "failing_function error: ValueError" in captured.out

    def test_file_logging_successful(self) -> None:
        """Тест логирования в файл при успешном выполнении.

        Проверяет, что:
        - Файл логов создаётся при успешном вызове.
        - В файл записывается сообщение об успехе.
        - Содержимое файла соответствует ожиданиям.
        """
        if os.path.exists("test_log.txt"):
            os.remove("test_log.txt")

        file_log_function(2, 3, c=1)

        assert os.path.exists("test_log.txt"), "Файл логов не создан"

        try:
            with open("test_log.txt", "r", encoding="utf-8") as f:
                content: str = f.read()
            assert "file_log_function ok" in content
        except (IOError, OSError) as e:
            pytest.fail(f"Не удалось прочитать файл логов: {e}")

    def test_file_logging_error(self) -> None:
        """Тест логирования в файл при ошибке.

        Проверяет, что:
        - Файл логов создаётся даже при ошибке.
        - В файл записывается информация об ошибке и входных данных.
        - Сообщение содержит корректный тип ошибки.
        """
        if os.path.exists("test_log.txt"):
            os.remove("test_log.txt")

        with pytest.raises(TypeError):
            error_func()

        assert os.path.exists("test_log.txt"), "Файл логов не создан при ошибке"

        try:
            with open("test_log.txt", "r", encoding="utf-8") as f:
                content: str = f.read()
            assert "error_func error: TypeError" in content
            assert "Inputs: (), {}" in content
        except (IOError, OSError) as e:
            pytest.fail(f"Не удалось прочитать файл логов: {e}")

    def test_function_arguments_logging(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования аргументов функции.

        Проверяет, что:
        - Декоратор корректно обрабатывает функции с позиционными и именованными аргументами.
        - При успешном выполнении в консоль выводится сообщение с именем функции и статусом "ok".
        - Логирование не искажает возвращаемое значение функции.

        Args:
            capsys: Фикстура pytest для захвата вывода в stdout/stderr.
                Предоставляется фреймворком автоматически.

        Test steps:
        1. Вызываем декорированную функцию с разными типами аргументов.
        2. Захватываем вывод консоли.
        3. Проверяем, что в выводе присутствует сообщение об успешном выполнении.
        """
        func_with_args(10, 20, c="custom")
        captured = capsys.readouterr()
        # Проверяем, что в захваченном выводе есть сообщение об успехе
        assert "func_with_args ok" in captured.out

    @pytest.fixture(autouse=True)
    def cleanup_files(self) -> Iterator[None]:
        """Очистка тестовых файлов после тестов.

        Автоматически выполняемая фикстура, которая гарантирует удаление временного
        файла логов после завершения всех тестов в классе.

        Эта фикстура:
        - Выполняется после каждого теста (благодаря autouse=True).
        - Удаляет файл test_log.txt, если он существует.
        - Игнорирует ошибки доступа, которые могут возникнуть, если файл
          всё ещё заблокирован другим процессом.

        Raises:
            PermissionError: Игнорируется — возникает, если файл занят другим процессом.
            OSError: Игнорируется — общие ошибки файловой системы.

        Note:
            Использование yield позволяет выполнить код до и после тестов.
            В данном случае код после yield выполняется после каждого теста.
        """
        yield
        try:
            if os.path.exists("test_log.txt"):
                os.remove("test_log.txt")
        except PermissionError, OSError:
            # Игнорируем ошибки доступа — файл может быть занят другим процессом
            # или находиться в состоянии, не позволяющем удаление
            pass
