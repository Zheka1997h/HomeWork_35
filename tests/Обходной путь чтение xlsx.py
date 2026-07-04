"""Графический просмотрщик Excel с поиском и сортировкой."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

import pandas as pd


class ExcelViewer:
    """Графический просмотрщик Excel с поиском и сортировкой."""

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.df: pd.DataFrame | None = self._load_data()

        if self.df is None:
            return

        self.root: tk.Tk
        self.search_var: tk.StringVar
        self.columns: list[str]
        self.tree: ttk.Treeview
        self.status_label: tk.Label

        self._create_window()
        self._create_widgets()
        self._fill_table()
        self.root.mainloop()

    def _load_data(self) -> pd.DataFrame | None:
        """Загрузка данных из Excel."""
        try:
            return pd.read_excel(self.file_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return None

    def _create_window(self) -> None:
        """Создание главного окна."""
        self.root = tk.Tk()
        self.root.title(f"📊 Excel Viewer: {self.file_path.split('/')[-1]}")
        self.root.geometry("1400x700")
        self.root.configure(bg="#f5f5f5")

    def _create_widgets(self) -> None:
        """Создание элементов интерфейса."""
        assert self.df is not None  # Для mypy

        # Верхняя панель с информацией
        top_frame = tk.Frame(self.root, bg="#f5f5f5")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            top_frame,
            text=f"📊 Строк: {len(self.df)}  |  📋 Колонок: {len(self.df.columns)}",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5",
            fg="#333",
        ).pack(side=tk.LEFT)

        # Поиск
        search_frame = tk.Frame(top_frame, bg="#f5f5f5")
        search_frame.pack(side=tk.RIGHT)

        tk.Label(search_frame, text="🔍 Поиск:", bg="#f5f5f5").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)

        tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("Arial", 10)).pack(side=tk.LEFT)

        # Таблица
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Прокрутки
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Таблица
        self.columns = list(self.df.columns)
        self.tree = ttk.Treeview(
            table_frame,
            columns=self.columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Настройка колонок
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_column(c))
            self.tree.column(col, width=150, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Нижняя панель
        bottom_frame = tk.Frame(self.root, bg="#f5f5f5")
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(
            bottom_frame,
            text=f"Показано: {len(self.df)} из {len(self.df)}",
            bg="#f5f5f5",
            font=("Arial", 9),
        )
        self.status_label.pack(side=tk.LEFT)

        tk.Button(
            bottom_frame,
            text="Закрыть",
            command=self.root.destroy,
            font=("Arial", 10),
            bg="#e0e0e0",
            width=12,
        ).pack(side=tk.RIGHT)

    def _fill_table(self, data: pd.DataFrame | None = None) -> None:
        """Заполнение таблицы данными."""
        assert self.df is not None  # Для mypy

        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Используем переданные данные или весь DataFrame
        df_to_show: pd.DataFrame = data if data is not None else self.df

        # Заполняем
        for _, row in df_to_show.iterrows():
            values: list[str] = [str(v) if pd.notna(v) else "" for v in row]
            self.tree.insert("", tk.END, values=values)

        # Обновляем статус
        self.status_label.config(text=f"Показано: {len(df_to_show)} из {len(self.df)}")

    def _sort_column(self, col: str) -> None:
        """Сортировка по колонке."""
        # Получаем данные
        data: list[tuple[str, str]] = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Пытаемся отсортировать как числа
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] else 0)
        except ValueError:
            data.sort(key=lambda t: t[0].lower())

        # Перестраиваем таблицу
        for index, (val, item_id) in enumerate(data):
            self.tree.move(item_id, "", index)

    def _on_search(self, *args: Any) -> None:
        """Поиск по таблице."""
        assert self.df is not None  # Для mypy

        query: str = self.search_var.get().lower().strip()

        if not query:
            self._fill_table()
            return

        # Фильтруем DataFrame
        mask = self.df.apply(
            lambda row: row.astype(str).str.lower().str.contains(query).any(),
            axis=1,
        )
        filtered_df: pd.DataFrame = self.df[mask]

        self._fill_table(filtered_df)


# Запуск
if __name__ == "__main__":
    file_path: str = r"/data/transactions_excel.xlsx"
    ExcelViewer(file_path)
