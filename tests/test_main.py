# -*- coding: utf-8 -*-
"""Компактные тесты main.py через классы со 100% покрытием."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator
from unittest.mock import MagicMock

import pytest

# ==================== ФИКСТУРЫ ====================


@pytest.fixture
def sample_data() -> list[dict[str, Any]]:
    """Пример данных транзакций."""
    return [
        {
            "id": 1,
            "date": "2024-01-15T12:30:00",
            "description": "Перевод организации",
            "state": "EXECUTED",
            "operationAmount": {"amount": "1000.00", "currency": {"code": "RUB"}},
        },
        {
            "id": 2,
            "date": "2024-01-14T10:00:00",
            "description": "Перевод с карты",
            "state": "CANCELED",
            "operationAmount": {"amount": "500.00", "currency": {"code": "USD"}},
        },
        {
            "id": 3,
            "date": "2024-01-16T15:45:00",
            "description": "Оплата услуг",
            "state": "PENDING",
            "operationAmount": {"amount": "250.00", "currency": {"code": "EUR"}},
        },
    ]


@pytest.fixture
def main_module() -> Any:
    """Импортирует main и возвращает модуль как Any для доступа к динамическим атрибутам."""
    import sys

    for key in list(sys.modules.keys()):
        if key == "src.main" or key.startswith("src.main."):
            del sys.modules[key]
    import src.main

    return src.main


@pytest.fixture(autouse=True)
def reset_state(main_module: Any) -> Iterator[None]:
    """Сбрасывает app_state перед каждым тестом."""
    main_module.app_state = {"transactions_data": [], "filtered_data": []}
    yield
    main_module.app_state = {"transactions_data": [], "filtered_data": []}


# ==================== КЛАСС 1: УТИЛИТЫ ====================


class TestUtilities:
    """Тесты утилит вывода и очистки консоли."""

    def test_header(self, capsys: pytest.CaptureFixture[str], main_module: Any) -> None:
        main_module.header("Test")
        out: str = capsys.readouterr().out
        assert "Test" in out and "──" in out

    def test_info(self, capsys: pytest.CaptureFixture[str], main_module: Any) -> None:
        main_module.info("msg")
        assert "msg" in capsys.readouterr().out

    def test_err(self, capsys: pytest.CaptureFixture[str], main_module: Any) -> None:
        main_module.err("error")
        assert "error" in capsys.readouterr().out

    def test_ok(self, capsys: pytest.CaptureFixture[str], main_module: Any) -> None:
        main_module.ok("success")
        assert "success" in capsys.readouterr().out

    def test_clear_screen_windows(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("os.name", "nt")
        mock_run: MagicMock = MagicMock()
        monkeypatch.setattr("subprocess.run", mock_run)
        main_module.clear_screen()
        mock_run.assert_called_once_with("cls", shell=True, check=False)

    def test_clear_screen_linux(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("os.name", "posix")
        mock_run = MagicMock()
        monkeypatch.setattr("subprocess.run", mock_run)
        main_module.clear_screen()
        mock_run.assert_called_once_with("clear", shell=False, check=False)

    def test_clear_screen_fallback(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("subprocess.run", MagicMock(side_effect=Exception()))
        main_module.clear_screen()


# ==================== КЛАСС 2: ОБЁРТКИ ====================


class TestWrappers:
    """Тесты функций-обёрток с @log."""

    def test_load_json_data(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "read_json_file", lambda x: [{"id": 1}])
        result: list[dict[str, Any]] = main_module.load_json_data("t.json")
        assert result == [{"id": 1}]

    def test_load_csv_data(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "transactions", lambda x: [{"id": 1}])
        result: list[dict[str, Any]] = main_module.load_csv_data("t.csv")
        assert result == [{"id": 1}]

    def test_load_excel_data(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "transactions_ecxel", lambda x: [{"id": 1}])
        result: list[dict[str, Any]] = main_module.load_excel_data("t.xlsx")
        assert result == [{"id": 1}]

    def test_search_ops(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "process_bank_search", lambda d, s: [{"id": 1}])
        result: list[dict[str, Any]] = main_module.search_ops([], "t")
        assert result == [{"id": 1}]

    def test_filter_state(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "filter_by_state", lambda d, s: [{"id": 1}])
        result: list[dict[str, Any]] = main_module.filter_state([], "EXECUTED")
        assert result == [{"id": 1}]

    def test_sort_date(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "sort_by_date", lambda d, desc: [{"id": 1}])
        result: list[dict[str, Any]] = main_module.sort_date([], True)
        assert result == [{"id": 1}]

    def test_filter_currency(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "filter_by_currency", lambda d, c: iter([{"id": 1}]))
        result: list[dict[str, Any]] = main_module.filter_currency([], "USD")
        assert result == [{"id": 1}]

    def test_mask_card(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "get_mask_card_number", lambda x: "masked")
        result: str = main_module.mask_card("123")
        assert result == "masked"

    def test_mask_acc(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "get_mask_account", lambda x: "masked")
        result: str = main_module.mask_acc("123")
        assert result == "masked"

    def test_mask_card_type(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "mask_account_card", lambda x: "masked")
        result: str = main_module.mask_card_type("Visa 123")
        assert result == "masked"

    def test_get_rate(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "get_exchange_rate", lambda x: 75.5)
        result: float = main_module.get_rate("USD")
        assert result == 75.5

    def test_count_categories(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "process_bank_operations", lambda d, c: {"cat": 5})
        result: dict[str, int] = main_module.count_categories([], ["cat"])
        assert result == {"cat": 5}

    def test_save_json_data(self, tmp_path: Path, main_module: Any) -> None:
        test_file: Path = tmp_path / "test.json"
        count: int = main_module.save_json_data([{"id": 1}], str(test_file))
        assert count == 1
        assert test_file.exists()

    def test_save_json_data_creates_folder(self, tmp_path: Path, main_module: Any) -> None:
        test_file: Path = tmp_path / "subdir" / "test.json"
        main_module.save_json_data([{"id": 1}], str(test_file))
        assert test_file.exists()


# ==================== КЛАСС 3: ЗАГРУЗКА И ВЫВОД ====================


class TestLoadAndDisplay:
    """Тесты загрузки файлов и вывода транзакций."""

    def test_load_file_success(self, tmp_path: Path, main_module: Any) -> None:
        test_file: Path = tmp_path / "test.json"
        test_file.write_text("[]", encoding="utf-8")
        main_module.load_file("JSON", str(test_file), lambda x: [{"id": 1}])
        assert main_module.app_state["transactions_data"] == [{"id": 1}]

    def test_load_file_not_found(self, main_module: Any) -> None:
        loader: MagicMock = MagicMock()
        main_module.load_file("JSON", "/nonexistent.json", loader)
        loader.assert_not_called()

    def test_load_file_exception(self, tmp_path: Path, main_module: Any) -> None:
        test_file: Path = tmp_path / "test.json"
        test_file.write_text("[]", encoding="utf-8")
        main_module.load_file("JSON", str(test_file), MagicMock(side_effect=Exception("err")))

    def test_print_transactions_empty(self, capsys: pytest.CaptureFixture[str], main_module: Any) -> None:
        main_module.print_transactions([])
        assert capsys.readouterr().out == ""

    def test_print_transactions_with_data(
        self,
        sample_data: list[dict[str, Any]],
        capsys: pytest.CaptureFixture[str],
        main_module: Any,
    ) -> None:
        main_module.print_transactions(sample_data, limit=10)
        out: str = capsys.readouterr().out
        assert "Перевод организации" in out and "RUB" in out

    def test_print_transactions_limit(
        self,
        sample_data: list[dict[str, Any]],
        capsys: pytest.CaptureFixture[str],
        main_module: Any,
    ) -> None:
        main_module.print_transactions(sample_data, limit=2)
        assert "и ещё 1 записей" in capsys.readouterr().out

    def test_print_transactions_missing_fields(self, capsys: pytest.CaptureFixture[str], main_module: Any) -> None:
        main_module.print_transactions([{"id": 1}])
        assert "?" in capsys.readouterr().out


# ==================== КЛАСС 4: ДЕЙСТВИЯ ЗАГРУЗКИ И ПОКАЗА ====================


class TestLoadActions:
    """Тесты действий загрузки и показа."""

    def test_action_load_json(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        test_file: Path = tmp_path / "operations.json"
        test_file.write_text("[]", encoding="utf-8")
        monkeypatch.setattr(main_module, "DEFAULT_JSON_PATH", str(test_file))
        monkeypatch.setattr(main_module, "read_json_file", lambda x: [{"id": 1}])
        main_module.action_load_json()
        assert len(main_module.app_state["transactions_data"]) == 1

    def test_action_load_csv(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        test_file: Path = tmp_path / "transactions.csv"
        test_file.write_text("", encoding="utf-8")
        monkeypatch.setattr(main_module, "DEFAULT_CSV_PATH", str(test_file))
        monkeypatch.setattr(main_module, "transactions", lambda x: [{"id": 1}])
        main_module.action_load_csv()
        assert len(main_module.app_state["transactions_data"]) == 1

    def test_action_load_excel(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        test_file: Path = tmp_path / "transactions_excel.xlsx"
        test_file.write_bytes(b"")
        monkeypatch.setattr(main_module, "DEFAULT_EXCEL_PATH", str(test_file))
        monkeypatch.setattr(main_module, "transactions_ecxel", lambda x: [{"id": 1}])
        main_module.action_load_excel()
        assert len(main_module.app_state["transactions_data"]) == 1

    def test_action_show_all_empty(self, main_module: Any) -> None:
        main_module.action_show_all()

    def test_action_show_all_with_data(self, sample_data: list[dict[str, Any]], main_module: Any) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        main_module.action_show_all()


# ==================== КЛАСС 5: ПОИСК И ФИЛЬТРАЦИЯ ====================


class TestSearchFilterActions:
    """Тесты действий поиска и фильтрации."""

    def test_action_search_no_data(self, main_module: Any) -> None:
        main_module.action_search()

    def test_action_search_empty_input(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": [],
        }
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_search()

    def test_action_search_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": [],
        }
        monkeypatch.setattr("builtins.input", lambda _: "Перевод")
        monkeypatch.setattr(main_module, "search_ops", lambda d, s: [sample_data[0]])
        main_module.action_search()
        assert main_module.app_state["filtered_data"] == [sample_data[0]]

    def test_action_filter_state_no_data(self, main_module: Any) -> None:
        main_module.action_filter_state()

    def test_action_filter_state_invalid(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": [],
        }
        monkeypatch.setattr("builtins.input", lambda _: "9")
        main_module.action_filter_state()

    def test_action_filter_state_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": [],
        }
        monkeypatch.setattr("builtins.input", lambda _: "1")
        monkeypatch.setattr(main_module, "filter_state", lambda d, s: [sample_data[0]])
        main_module.action_filter_state()
        assert main_module.app_state["filtered_data"] == [sample_data[0]]

    def test_action_sort_date_no_data(self, main_module: Any) -> None:
        main_module.action_sort_date()

    def test_action_sort_date_invalid(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr("builtins.input", lambda _: "9")
        main_module.action_sort_date()

    def test_action_sort_date_descending(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr("builtins.input", lambda _: "1")
        monkeypatch.setattr(main_module, "sort_date", lambda d, desc: sample_data)
        main_module.action_sort_date()

    def test_action_sort_date_ascending(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr("builtins.input", lambda _: "2")
        monkeypatch.setattr(main_module, "sort_date", lambda d, desc: sample_data)
        main_module.action_sort_date()

    def test_action_filter_currency_no_data(self, main_module: Any) -> None:
        main_module.action_filter_currency()

    def test_action_filter_currency_empty(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": [],
        }
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_filter_currency()

    def test_action_filter_currency_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": [],
        }
        monkeypatch.setattr("builtins.input", lambda _: "USD")
        monkeypatch.setattr(main_module, "filter_currency", lambda d, c: [sample_data[1]])
        main_module.action_filter_currency()
        assert main_module.app_state["filtered_data"] == [sample_data[1]]


# ==================== КЛАСС 6: МАСКИРОВКА И ДАТА ====================


class TestMaskAndDateActions:
    """Тесты действий маскировки и даты."""

    def test_action_mask_card_empty(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_mask_card()

    def test_action_mask_card_success(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "1234567890123456")
        monkeypatch.setattr(main_module, "mask_card", lambda x: "1234 56** **** 3456")
        main_module.action_mask_card()

    def test_action_mask_card_error(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "123")
        monkeypatch.setattr(main_module, "mask_card", MagicMock(side_effect=ValueError("err")))
        main_module.action_mask_card()

    def test_action_mask_account_empty(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_mask_account()

    def test_action_mask_account_success(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "12345678901234567890")
        monkeypatch.setattr(main_module, "mask_acc", lambda x: "**7890")
        main_module.action_mask_account()

    def test_action_mask_account_error(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "123")
        monkeypatch.setattr(main_module, "mask_acc", MagicMock(side_effect=ValueError("err")))
        main_module.action_mask_account()

    def test_action_mask_card_type_empty(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_mask_card_type()

    def test_action_mask_card_type_success(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "Visa 1234567890123456")
        monkeypatch.setattr(
            main_module,
            "mask_card_type",
            lambda x: "Visa 1234 56** **** 3456",
        )
        main_module.action_mask_card_type()

    def test_action_mask_card_type_error(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "Invalid")
        monkeypatch.setattr(
            main_module,
            "mask_card_type",
            MagicMock(side_effect=ValueError("err")),
        )
        main_module.action_mask_card_type()

    def test_action_convert_date_empty(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_convert_date()

    def test_action_convert_date_success(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "2024-01-15T12:30:00")
        monkeypatch.setattr(main_module, "get_date", lambda x: "15.01.2024")
        main_module.action_convert_date()

    def test_action_convert_date_error(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "invalid")
        monkeypatch.setattr(main_module, "get_date", MagicMock(side_effect=ValueError("err")))
        main_module.action_convert_date()


# ==================== КЛАСС 7: ВАЛЮТЫ И АНАЛИТИКА ====================


class TestCurrencyAndAnalytics:
    """Тесты действий валют и аналитики."""

    def test_action_get_rate_empty(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_get_rate()

    def test_action_get_rate_success(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "USD")
        monkeypatch.setattr(main_module, "get_rate", lambda x: 75.5)
        main_module.action_get_rate()

    def test_action_get_rate_error(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "USD")
        monkeypatch.setattr(main_module, "get_rate", MagicMock(side_effect=Exception("err")))
        main_module.action_get_rate()

    def test_action_convert_to_rub_no_data(self, main_module: Any) -> None:
        main_module.action_convert_to_rub()

    def test_action_convert_to_rub_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr(main_module, "convert_transaction_to_rub", lambda t: 1000.0)
        main_module.action_convert_to_rub()

    def test_action_convert_to_rub_error(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr(
            main_module,
            "convert_transaction_to_rub",
            MagicMock(side_effect=Exception("err")),
        )
        main_module.action_convert_to_rub()

    def test_action_count_categories_no_data(self, main_module: Any) -> None:
        main_module.action_count_categories()

    def test_action_count_categories_empty(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr("builtins.input", lambda _: "")
        main_module.action_count_categories()

    def test_action_count_categories_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr("builtins.input", lambda _: "Перевод,Оплата")
        monkeypatch.setattr(
            main_module,
            "count_categories",
            lambda d, c: {"Перевод": 2, "Оплата": 1},
        )
        main_module.action_count_categories()

    def test_action_statistics_no_data(self, main_module: Any) -> None:
        main_module.action_statistics()

    def test_action_statistics_success(self, sample_data: list[dict[str, Any]], main_module: Any) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        main_module.action_statistics()

    def test_action_descriptions_no_data(self, main_module: Any) -> None:
        main_module.action_descriptions()

    def test_action_descriptions_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr(
            main_module,
            "transaction_descriptions",
            lambda d: iter(["Desc1", "Desc2"]),
        )
        main_module.action_descriptions()


# ==================== КЛАСС 8: ГЕНЕРАТОР, СОХРАНЕНИЕ, МЕНЮ ====================


class TestGeneratorSaveMenu:
    """Тесты генератора, сохранения, меню и main()."""

    def test_action_generate_cards_invalid(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "abc")
        main_module.action_generate_cards()

    def test_action_generate_cards_stop_less(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        inputs: Iterator[str] = iter(["10", "5"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        main_module.action_generate_cards()

    def test_action_generate_cards_too_many(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        inputs = iter(["1", "200"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        main_module.action_generate_cards()

    def test_action_generate_cards_success(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        inputs = iter(["1", "3"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        monkeypatch.setattr(
            main_module,
            "card_number_generator",
            lambda s, e: iter(["0000 0000 0000 0001", "0000 0000 0000 0002"]),
        )
        main_module.action_generate_cards()

    def test_action_save_no_data(self, main_module: Any) -> None:
        main_module.action_save()

    def test_action_save_success(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        main_module: Any,
    ) -> None:
        test_file: Path = tmp_path / "result.json"
        monkeypatch.setattr(main_module, "DEFAULT_SAVE_PATH", str(test_file))
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        main_module.action_save()
        assert test_file.exists()

    def test_action_save_error(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        main_module: Any,
    ) -> None:
        monkeypatch.setattr(main_module, "DEFAULT_SAVE_PATH", "/invalid/path/result.json")
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        main_module.action_save()

    def test_action_clear(self, sample_data: list[dict[str, Any]], main_module: Any) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        main_module.action_clear()
        assert main_module.app_state["transactions_data"] == []
        assert main_module.app_state["filtered_data"] == []

    def test_print_menu_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        main_module: Any,
    ) -> None:
        monkeypatch.setattr(main_module, "clear_screen", lambda: None)
        main_module.print_menu()
        out: str = capsys.readouterr().out
        assert "БАНКОВСКИЙ ПРОЦЕССОР" in out and "не загружены" in out

    def test_print_menu_with_data(
        self,
        sample_data: list[dict[str, Any]],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        main_module: Any,
    ) -> None:
        main_module.app_state = {
            "transactions_data": sample_data,
            "filtered_data": sample_data,
        }
        monkeypatch.setattr(main_module, "clear_screen", lambda: None)
        main_module.print_menu()
        out = capsys.readouterr().out
        assert "Загружено: 3" in out and "Отфильтровано: 3" in out

    def test_main_exit(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "clear_screen", lambda: None)
        monkeypatch.setattr(main_module, "print_menu", lambda: None)
        monkeypatch.setattr(main_module, "pause", lambda: None)
        monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
        monkeypatch.setattr("builtins.input", lambda _: "0")
        main_module.main()

    def test_main_invalid_choice(self, monkeypatch: pytest.MonkeyPatch, main_module: Any) -> None:
        monkeypatch.setattr(main_module, "clear_screen", lambda: None)
        monkeypatch.setattr(main_module, "print_menu", lambda: None)
        monkeypatch.setattr(main_module, "pause", lambda: None)
        monkeypatch.setattr("os.makedirs", lambda *a, **k: None)
        inputs = iter(["99", "0"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        main_module.main()

    def test_constants(self, main_module: Any) -> None:
        assert main_module.DEFAULT_JSON_PATH
        assert main_module.DEFAULT_CSV_PATH
        assert main_module.DEFAULT_EXCEL_PATH
        assert main_module.DEFAULT_SAVE_PATH

    def test_menu_structure(self, main_module: Any) -> None:
        menu: list[tuple[str, str, Any]] = main_module.MENU
        assert len(menu) == 21
        assert menu[0][0] == "1"
        assert menu[-1][0] == "0"
        assert menu[-1][2] is None
