from unittest.mock import patch, MagicMock
from zipfile import BadZipFile
import pytest
from src.transactions import transactions, transactions_ecxel


# ============================================================================
# ТЕСТЫ ДЛЯ transactions()
# ============================================================================

@patch("src.transactions.csv.DictReader")
@patch("builtins.open")
def test_transactions_success(mock_open, mock_dict_reader, capsys):
    """Успешное чтение CSV."""
    data = [{"id": "1", "state": "EXECUTED"}, {"id": "2", "state": "PENDING"}]
    mock_dict_reader.return_value = iter(data)

    result = transactions("test.csv")

    assert result == data
    assert "EXECUTED" in capsys.readouterr().out


@patch("src.transactions.csv.DictReader")
@patch("builtins.open")
def test_transactions_empty(mock_open, mock_dict_reader):
    """Пустой CSV файл."""
    mock_dict_reader.return_value = iter([])
    assert transactions("empty.csv") == []


@pytest.mark.parametrize("error, message", [
    (FileNotFoundError, "Неверный путь файла"),
    (UnicodeDecodeError("utf-8", b"", 0, 1, "err"), "Неверный формат кодировки"),
])
@patch("builtins.open")
def test_transactions_errors(mock_open, error, message, capsys):
    """Ошибки при чтении CSV."""
    mock_open.side_effect = error
    assert transactions("bad.csv") == []
    assert message in capsys.readouterr().out


# ============================================================================
# ТЕСТЫ ДЛЯ transactions_ecxel()
# ============================================================================

@patch("src.transactions.pd.read_excel")
def test_transactions_excel_success(mock_read_excel):
    """Успешное чтение Excel."""
    mock_df = MagicMock()
    mock_df.to_dict.return_value = [{"id": 1}, {"id": 2}]
    mock_read_excel.return_value = mock_df

    result = transactions_ecxel("test.xlsx")

    assert result == [{"id": 1}, {"id": 2}]
    mock_df.to_dict.assert_called_once_with(orient="records")


@pytest.mark.parametrize("error, message", [
    (FileNotFoundError, "Файл не найден"),
    (PermissionError, "Нет доступа к файлу"),
    (BadZipFile, "Файл поврежден"),
    (Exception("oops"), "Непредвиденная ошибка"),
])
@patch("src.transactions.pd.read_excel")
def test_transactions_excel_errors(mock_read_excel, error, message, capsys):
    """Ошибки при чтении Excel."""
    mock_read_excel.side_effect = error
    assert transactions_ecxel("bad.xlsx") == []
    assert message in capsys.readouterr().out