"""Тесты для модуля transactions."""

from typing import Any, Union
from unittest.mock import MagicMock, patch
from zipfile import BadZipFile

import pytest

from src.transactions import transactions, transactions_ecxel

# ============================================================================
# ТЕСТЫ ДЛЯ transactions()
# ============================================================================


@patch("src.transactions.csv.DictReader")
@patch("builtins.open")
def test_transactions_success(
    mock_open: MagicMock,
    mock_dict_reader: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Успешное чтение CSV."""
    data: list[dict[str, str]] = [
        {"id": "1", "state": "EXECUTED"},
        {"id": "2", "state": "PENDING"},
    ]
    mock_dict_reader.return_value = iter(data)

    result: list[dict[str, Any]] = transactions("test.csv")

    assert result == data
    assert "EXECUTED" in capsys.readouterr().out


@patch("src.transactions.csv.DictReader")
@patch("builtins.open")
def test_transactions_empty(
    mock_open: MagicMock,
    mock_dict_reader: MagicMock,
) -> None:
    """Пустой CSV файл."""
    mock_dict_reader.return_value = iter([])
    result: list[dict[str, Any]] = transactions("empty.csv")
    assert result == []


@pytest.mark.parametrize(
    "error, message",
    [
        (FileNotFoundError, "Неверный путь файла"),
        (UnicodeDecodeError("utf-8", b"", 0, 1, "err"), "Неверный формат кодировки"),
    ],
)
@patch("builtins.open")
def test_transactions_errors(
    mock_open: MagicMock,
    error: Union[type[BaseException], BaseException],
    message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ошибки при чтении CSV."""
    mock_open.side_effect = error
    result: list[dict[str, Any]] = transactions("bad.csv")
    assert result == []
    assert message in capsys.readouterr().out


# ============================================================================
# ТЕСТЫ ДЛЯ transactions_ecxel()
# ============================================================================


@patch("src.transactions.pd.read_excel")
def test_transactions_excel_success(mock_read_excel: MagicMock) -> None:
    """Успешное чтение Excel."""
    mock_df: MagicMock = MagicMock()
    mock_df.to_dict.return_value = [{"id": 1}, {"id": 2}]
    mock_read_excel.return_value = mock_df

    result: list[dict[str, Any]] = transactions_ecxel("test.xlsx")

    assert result == [{"id": 1}, {"id": 2}]
    mock_df.to_dict.assert_called_once_with(orient="records")


@pytest.mark.parametrize(
    "error, message",
    [
        (FileNotFoundError, "Файл не найден"),
        (PermissionError, "Нет доступа к файлу"),
        (BadZipFile, "Файл поврежден"),
        (Exception("oops"), "Непредвиденная ошибка"),
    ],
)
@patch("src.transactions.pd.read_excel")
def test_transactions_excel_errors(
    mock_read_excel: MagicMock,
    error: Union[type[BaseException], BaseException],
    message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ошибки при чтении Excel."""
    mock_read_excel.side_effect = error
    result: list[dict[str, Any]] = transactions_ecxel("bad.xlsx")
    assert result == []
    assert message in capsys.readouterr().out
