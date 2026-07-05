# -*- coding: utf-8 -*-
"""Тесты для модуля transactions с полной типизацией mypy."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import BadZipFile

import pandas as pd
import pytest

from src.transactions import transactions, transactions_ecxel

# ==================== ТЕСТЫ transactions() (CSV) ====================


def test_transactions_success(tmp_path: Path) -> None:
    """Успешное чтение CSV."""
    csv_path: Path = tmp_path / "test.csv"
    csv_path.write_text("id;state\n1;EXECUTED\n2;PENDING\n", encoding="utf-8")

    result: list[dict[str, Any]] = transactions(str(csv_path))

    assert result == [
        {"id": "1", "state": "EXECUTED"},
        {"id": "2", "state": "PENDING"},
    ]


def test_transactions_empty_file(tmp_path: Path) -> None:
    """Чтение пустого CSV (только заголовки)."""
    csv_path: Path = tmp_path / "empty.csv"
    csv_path.write_text("id;state\n", encoding="utf-8")

    result: list[dict[str, Any]] = transactions(str(csv_path))

    assert result == []


def test_transactions_file_not_found() -> None:
    """Обработка отсутствия файла."""
    result: list[dict[str, Any]] = transactions("/nonexistent/path.csv")
    assert result == []


def test_transactions_encoding_error(tmp_path: Path) -> None:
    """Обработка ошибки кодировки."""
    csv_path: Path = tmp_path / "bad_encoding.csv"
    # Байты, несовместимые с UTF-8
    csv_path.write_bytes(b"\xff\xfe\x00\x01invalid")

    result: list[dict[str, Any]] = transactions(str(csv_path))

    assert result == []


# ==================== ТЕСТЫ transactions_ecxel() (Excel) ====================


def test_transactions_ecxel_success(tmp_path: Path) -> None:
    """Успешное чтение Excel."""
    excel_path: Path = tmp_path / "test.xlsx"
    df: pd.DataFrame = pd.DataFrame(
        [
            {"id": 1, "state": "EXECUTED"},
            {"id": 2, "state": "PENDING"},
        ]
    )
    df.to_excel(excel_path, index=False)

    result: list[dict[str, Any]] = transactions_ecxel(str(excel_path))

    assert result == [
        {"id": 1, "state": "EXECUTED"},
        {"id": 2, "state": "PENDING"},
    ]


def test_transactions_ecxel_file_not_found() -> None:
    """Обработка отсутствия Excel-файла."""
    result: list[dict[str, Any]] = transactions_ecxel("/nonexistent.xlsx")
    assert result == []


def test_transactions_ecxel_permission_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Обработка ошибки доступа."""
    excel_path: Path = tmp_path / "locked.xlsx"
    excel_path.write_bytes(b"fake")

    def raise_permission_error(*args: Any, **kwargs: Any) -> None:
        raise PermissionError("Нет доступа")

    monkeypatch.setattr(pd, "read_excel", raise_permission_error)

    result: list[dict[str, Any]] = transactions_ecxel(str(excel_path))
    assert result == []


def test_transactions_ecxel_bad_zip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Обработка повреждённого файла (BadZipFile)."""
    excel_path: Path = tmp_path / "corrupted.xlsx"
    excel_path.write_bytes(b"not a zip file")

    def raise_bad_zip(*args: Any, **kwargs: Any) -> None:
        raise BadZipFile("Файл повреждён")

    monkeypatch.setattr(pd, "read_excel", raise_bad_zip)

    result: list[dict[str, Any]] = transactions_ecxel(str(excel_path))
    assert result == []


def test_transactions_ecxel_unexpected_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Обработка непредвиденной ошибки."""
    excel_path: Path = tmp_path / "test.xlsx"
    excel_path.write_bytes(b"fake")

    def raise_unexpected(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Непредвиденная ошибка")

    monkeypatch.setattr(pd, "read_excel", raise_unexpected)

    result: list[dict[str, Any]] = transactions_ecxel(str(excel_path))
    assert result == []
