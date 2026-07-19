import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

# Импортируем классы из вашего модуля
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.learn_OOP import Product, Category, Read_Json_file


# ==================== ТЕСТЫ ДЛЯ Product ====================

class TestProduct:
    """Тесты класса Product."""

    def test_product_init(self):
        """Тест создания объекта Product."""
        product = Product("Смартфон", "Описание", 79990.0, 15)

        assert product.name == "Смартфон"
        assert product.description == "Описание"
        assert product.price == 79990.0
        assert product.quantity == 15

    def test_product_str(self):
        """Тест строкового представления."""
        product = Product("Смартфон", "Описание", 100.0, 5)
        result = str(product)

        assert "Смартфон" in result
        assert "Описание" in result
        assert "100.0" in result
        assert "5" in result

    def test_product_to_dict(self):
        """Тест преобразования в словарь."""
        product = Product("Ноутбук", "Игровой", 129990.0, 8)
        result = product.to_dict()

        assert result == {
            "name": "Ноутбук",
            "description": "Игровой",
            "price": 129990.0,
            "quantity": 8
        }

    def test_product_from_dict(self):
        """Тест создания из словаря."""
        data = {
            "name": "Наушники",
            "description": "Беспроводные",
            "price": 15990.0,
            "quantity": 30
        }
        product = Product.from_dict(data)

        assert product.name == "Наушники"
        assert product.description == "Беспроводные"
        assert product.price == 15990.0
        assert product.quantity == 30

    def test_product_roundtrip(self):
        """Тест: to_dict -> from_dict = исходный объект."""
        original = Product("Товар", "Описание", 100.0, 10)
        restored = Product.from_dict(original.to_dict())

        assert restored.name == original.name
        assert restored.price == original.price


# ==================== ТЕСТЫ ДЛЯ Category ====================

class TestCategory:
    """Тесты класса Category."""

    def test_category_init(self):
        """Тест создания категории."""
        category = Category("Электроника", "Гаджеты")

        assert category.name == "Электроника"
        assert category.description == "Гаджеты"
        assert category.products == []

    def test_add_product(self):
        """Тест добавления товара."""
        category = Category("Электроника", "Гаджеты")
        product = Product("Смартфон", "Описание", 100.0, 5)

        category.add_product(product)

        assert len(category.products) == 1
        assert category.products[0].name == "Смартфон"

    def test_get_total_products(self):
        """Тест подсчёта товаров."""
        category = Category("Электроника", "Гаджеты")

        assert category.get_total_products() == 0

        category.add_product(Product("Т1", "О", 10.0, 1))
        category.add_product(Product("Т2", "О", 20.0, 2))

        assert category.get_total_products() == 2

    def test_category_str(self):
        """Тест строкового представления."""
        category = Category("Электроника", "Гаджеты")
        category.add_product(Product("Т1", "О", 10.0, 1))

        result = str(category)

        assert "Электроника" in result
        assert "1" in result

    def test_category_to_dict(self):
        """Тест преобразования в словарь."""
        category = Category("Электроника", "Гаджеты")
        category.add_product(Product("Т1", "О", 10.0, 1))

        result = category.to_dict()

        assert result["name"] == "Электроника"
        assert result["description"] == "Гаджеты"
        assert len(result["products"]) == 1
        assert result["products"][0]["name"] == "Т1"

    def test_category_from_dict(self):
        """Тест создания из словаря."""
        data = {
            "name": "Электроника",
            "description": "Гаджеты",
            "products": [
                {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1},
                {"name": "Т2", "description": "О", "price": 20.0, "quantity": 2}
            ]
        }
        category = Category.from_dict(data)

        assert category.name == "Электроника"
        assert category.get_total_products() == 2
        assert category.products[0].name == "Т1"

    def test_category_from_dict_empty_products(self):
        """Тест создания из словаря без товаров."""
        data = {"name": "Пустая", "description": "Без товаров"}
        category = Category.from_dict(data)

        assert category.get_total_products() == 0


# ==================== ТЕСТЫ ДЛЯ Read_Json_file ====================

class TestReadJsonFile:
    """Тесты класса Read_Json_file."""

    def test_init(self):
        """Тест создания менеджера."""
        manager = Read_Json_file()

        assert manager.categories == []

    def test_add_category(self):
        """Тест добавления категории."""
        manager = Read_Json_file()
        category = Category("Электроника", "Гаджеты")

        manager.add_category(category)

        assert len(manager.categories) == 1

    def test_get_all_categories(self):
        """Тест получения всех категорий."""
        manager = Read_Json_file()
        cat1 = Category("К1", "О1")
        cat2 = Category("К2", "О2")

        manager.add_category(cat1)
        manager.add_category(cat2)

        result = manager.get_all_categories()
        assert len(result) == 2
        assert result[0].name == "К1"

    def test_get_total_products(self):
        """Тест подсчёта всех товаров."""
        manager = Read_Json_file()

        cat1 = Category("К1", "О1")
        cat1.add_product(Product("Т1", "О", 10.0, 1))
        cat1.add_product(Product("Т2", "О", 20.0, 2))

        cat2 = Category("К2", "О2")
        cat2.add_product(Product("Т3", "О", 30.0, 3))

        manager.add_category(cat1)
        manager.add_category(cat2)

        assert manager.get_total_products() == 3

    def test_str(self):
        """Тест строкового представления."""
        manager = Read_Json_file()
        cat = Category("К1", "О1")
        cat.add_product(Product("Т1", "О", 10.0, 1))
        manager.add_category(cat)

        result = str(manager)

        assert "1 категорий" in result
        assert "1 товаров" in result

    def test_load_from_json_file_not_found(self, tmp_path):
        """Тест: файл не найден."""
        fake_path = tmp_path / "nonexistent.json"
        manager = Read_Json_file.load_from_json(str(fake_path))

        assert manager.categories == []

    def test_load_from_json_dict_format(self, tmp_path):
        """Тест: JSON в формате словаря."""
        data = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [
                        {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1}
                    ]
                }
            ]
        }
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

        manager = Read_Json_file.load_from_json(str(json_file))

        assert len(manager.categories) == 1
        assert manager.categories[0].name == "Электроника"

    def test_load_from_json_list_format(self, tmp_path):
        """Тест: JSON в формате списка."""
        data = [
            {
                "name": "Электроника",
                "description": "Гаджеты",
                "products": [
                    {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1}
                ]
            }
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

        manager = Read_Json_file.load_from_json(str(json_file))

        assert len(manager.categories) == 1

    def test_load_from_json_unknown_format(self, tmp_path):
        """Тест: неизвестный формат JSON."""
        json_file = tmp_path / "test.json"
        json_file.write_text('"просто строка"', encoding='utf-8')

        manager = Read_Json_file.load_from_json(str(json_file))

        assert manager.categories == []

    def test_load_from_json_invalid_json(self, tmp_path):
        """Тест: невалидный JSON."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{invalid json}', encoding='utf-8')

        manager = Read_Json_file.load_from_json(str(json_file))

        assert manager.categories == []

    def test_load_from_json_general_exception(self, tmp_path):
        """Тест: общее исключение при чтении."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"categories": []}', encoding='utf-8')

        # Имитируем ошибку через patch
        with patch('builtins.open', side_effect=PermissionError("Доступ запрещён")):
            manager = Read_Json_file.load_from_json(str(json_file))
            assert manager.categories == []

    def test_load_from_json_empty_categories(self, tmp_path):
        """Тест: JSON без категорий."""
        data = {"categories": []}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data), encoding='utf-8')

        manager = Read_Json_file.load_from_json(str(json_file))

        assert manager.get_total_products() == 0


# ==================== ИНТЕГРАЦИОННЫЙ ТЕСТ ====================

class TestIntegration:
    """Интеграционные тесты."""

    def test_full_workflow(self, tmp_path):
        """Тест полного цикла: загрузка -> обработка."""
        # Создаём тестовый JSON
        data = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [
                        {"name": "Смартфон", "description": "Флагман", "price": 79990.0, "quantity": 15},
                        {"name": "Ноутбук", "description": "Игровой", "price": 129990.0, "quantity": 8}
                    ]
                },
                {
                    "name": "Одежда",
                    "description": "Мужская",
                    "products": [
                        {"name": "Куртка", "description": "Зимняя", "price": 8990.0, "quantity": 25}
                    ]
                }
            ]
        }

        json_file = tmp_path / "products.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

        # Загружаем
        manager = Read_Json_file.load_from_json(str(json_file))

        # Проверяем
        assert len(manager.get_all_categories()) == 2
        assert manager.get_total_products() == 3

        # Проверяем содержимое
        electronics = manager.get_all_categories()[0]
        assert electronics.name == "Электроника"
        assert electronics.get_total_products() == 2

        smartphone = electronics.products[0]
        assert smartphone.name == "Смартфон"
        assert smartphone.price == 79990.0