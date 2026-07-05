# -*- coding: utf-8 -*-
from unittest.mock import MagicMock, mock_open, patch

from src.utils import read_json_file


class TestReadJsonFile:
    """Набор тестов для функции read_json_file."""

    @patch("builtins.open", new_callable=mock_open, read_data='[{"id": 1}]')
    def test_read_json_file_success(self, mock_file: MagicMock) -> None:
        """Тест: успешное чтение корректного JSON-файла."""
        result = read_json_file("data/operations.json")
        assert result == [{"id": 1}]

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_read_json_file_not_found(self, mock_file: MagicMock) -> None:
        """Тест: файл не найден → возвращается пустой список."""
        result = read_json_file("nonexistent.json")
        assert result == []

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_read_json_file_empty(self, mock_file: MagicMock) -> None:
        """Тест: пустой файл → возвращается пустой список."""
        result = read_json_file("empty.json")
        assert result == []

    @patch("builtins.open", new_callable=mock_open, read_data="   \n  ")
    def test_read_json_file_whitespace_only(self, mock_file: MagicMock) -> None:
        """Тест: файл содержит только пробелы → пустой список."""
        result = read_json_file("whitespace.json")
        assert result == []

    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_read_json_file_not_list(self, mock_file: MagicMock) -> None:
        """Тест: JSON содержит словарь, а не список → пустой список."""
        result = read_json_file("dict.json")
        assert result == []

    @patch("builtins.open", new_callable=mock_open, read_data="not a json")
    def test_read_json_file_invalid_json(self, mock_file: MagicMock) -> None:
        """Тест: невалидный JSON → пустой список."""
        result = read_json_file("invalid.json")
        assert result == []

    @patch("builtins.open", side_effect=PermissionError)
    def test_read_json_file_permission_error(self, mock_file: MagicMock) -> None:
        """Тест: ошибка доступа к файлу → пустой список (покрытие except Exception)."""
        result = read_json_file("restricted.json")
        assert result == []
