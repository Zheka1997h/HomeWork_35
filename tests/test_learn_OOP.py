import json
import sys
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.learn_OOP import Category, Product, Read_Json_file


@pytest.fixture(autouse=True)
def reset_counters() -> Iterator[None]:
    """Сбрасывает счётчики классов перед каждым тестом."""
    Product.product_count = 0
    Category.category_count = 0
    Category.product_count = 0
    yield


# ==================== ТЕСТЫ ДЛЯ Product ====================


class TestProduct:

    def test_product_init(self) -> None:
        product = Product("Смартфон", "Описание", 79990.0, 15)
        assert product.name == "Смартфон"
        assert product.description == "Описание"
        assert product.price == 79990.0
        assert product.quantity == 15

    def test_product_count_increments(self) -> None:
        """Атрибут класса: счётчик товаров увеличивается при инициализации."""
        assert Product.product_count == 0

        Product("Т1", "О", 10.0, 1)
        assert Product.product_count == 1

        Product("Т2", "О", 20.0, 2)
        assert Product.product_count == 2

        Product("Т3", "О", 30.0, 3)
        assert Product.product_count == 3

    def test_product_str(self) -> None:
        product = Product("Смартфон", "Описание", 100.0, 5)
        result = str(product)
        assert "Смартфон" in result
        assert "100.0" in result
        assert "5" in result

    def test_product_to_dict(self) -> None:
        product = Product("Ноутбук", "Игровой", 129990.0, 8)
        result = product.to_dict()
        assert result == {"name": "Ноутбук", "description": "Игровой", "price": 129990.0, "quantity": 8}
        assert result["price"] == 129990.0

    def test_product_from_dict(self) -> None:
        data = {"name": "Наушники", "description": "Беспроводные", "price": 15990.0, "quantity": 30}
        product = Product.from_dict(data)
        assert product.name == "Наушники"
        assert product.price == 15990.0
        assert product.quantity == 30

    def test_product_from_dict_increments_count(self) -> None:
        """from_dict тоже увеличивает счётчик Product.product_count (вызывает __init__)."""
        Product.from_dict({"name": "Т", "description": "О", "price": 1.0, "quantity": 1})
        assert Product.product_count == 1


# ==================== ТЕСТЫ ДЛЯ Category ====================


class TestCategory:

    def test_category_init_empty(self) -> None:
        """Создание категории без товаров (по умолчанию)."""
        category = Category("Электроника", "Гаджеты")
        assert category.name == "Электроника"
        assert category.description == "Гаджеты"
        assert category.products == []

    def test_category_init_with_products(self) -> None:
        """Создание категории с переданным списком товаров."""
        p1 = Product("Смартфон", "Описание", 79990.0, 15)
        p2 = Product("Ноутбук", "Игровой", 129990.0, 8)
        category = Category("Электроника", "Гаджеты", products=[p1, p2])

        assert category.name == "Электроника"
        assert len(category.products) == 2
        assert category.products[0].name == "Смартфон"
        assert category.products[1].name == "Ноутбук"

    def test_category_count_increments(self) -> None:
        """Атрибут класса: счётчик категорий увеличивается при инициализации."""
        assert Category.category_count == 0

        Category("К1", "О1")
        assert Category.category_count == 1

        Category("К2", "О2")
        assert Category.category_count == 2

    def test_product_count_increments_on_init(self) -> None:
        """Category.product_count увеличивается при создании категории с товарами."""
        assert Category.product_count == 0

        p1 = Product("Т1", "О", 10.0, 1)
        Category("Электроника", "Гаджеты", products=[p1])
        assert Category.product_count == 1

        p2 = Product("Т2", "О", 20.0, 2)
        p3 = Product("Т3", "О", 30.0, 3)
        Category("Одежда", "Мужская", products=[p2, p3])
        assert Category.product_count == 3

    def test_product_count_increments_across_categories(self) -> None:
        """Category.product_count — общий счётчик товаров по всем категориям."""
        p1 = Product("Т1", "О", 10.0, 1)
        p2 = Product("Т2", "О", 20.0, 2)
        p3 = Product("Т3", "О", 30.0, 3)

        Category("К1", "О1", products=[p1])
        Category("К2", "О2", products=[p2, p3])

        assert Category.product_count == 3

    def test_empty_category_does_not_affect_product_count(self) -> None:
        """Создание категории без товаров не меняет Category.product_count."""
        Category("Пустая", "О")
        Category("Тоже пустая", "О")
        assert Category.product_count == 0

    def test_get_total_products(self) -> None:
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[
                Product("Т1", "О", 10.0, 1),
                Product("Т2", "О", 20.0, 2),
            ],
        )
        assert category.get_total_products() == 2

    def test_get_total_products_empty(self) -> None:
        category = Category("Электроника", "Гаджеты")
        assert category.get_total_products() == 0

    def test_category_str(self) -> None:
        category = Category("Электроника", "Гаджеты")
        result = str(category)
        assert "Электроника" in result
        assert "0" in result

    def test_category_str_with_products(self) -> None:
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[
                Product("Т1", "О", 10.0, 1),
                Product("Т2", "О", 20.0, 2),
            ],
        )
        result = str(category)
        assert "Электроника" in result
        assert "2" in result

    def test_category_to_dict(self) -> None:
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[Product("Т1", "О", 10.0, 1)],
        )
        result = category.to_dict()
        assert result["name"] == "Электроника"
        assert result["description"] == "Гаджеты"
        assert len(result["products"]) == 1
        assert result["products"][0]["name"] == "Т1"

    def test_category_to_dict_empty(self) -> None:
        category = Category("Пустая", "Описание")
        result = category.to_dict()
        assert result["products"] == []

    def test_category_from_dict(self) -> None:
        data = {
            "name": "Электроника",
            "description": "Гаджеты",
            "products": [
                {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1},
                {"name": "Т2", "description": "О", "price": 20.0, "quantity": 2},
            ],
        }
        category = Category.from_dict(data)
        assert category.name == "Электроника"
        assert category.get_total_products() == 2
        assert category.products[0].name == "Т1"
        assert category.products[1].price == 20.0

    def test_category_from_dict_empty_products(self) -> None:
        data = {"name": "Пустая", "description": "Без товаров"}
        category = Category.from_dict(data)
        assert category.get_total_products() == 0
        assert category.products == []

    def test_category_from_dict_increments_counts(self) -> None:
        """from_dict увеличивает category_count, product_count и Product.product_count."""
        data = {
            "name": "К1",
            "description": "О",
            "products": [
                {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1},
                {"name": "Т2", "description": "О", "price": 20.0, "quantity": 2},
            ],
        }
        Category.from_dict(data)

        assert Category.category_count == 1
        assert Category.product_count == 2
        assert Product.product_count == 2


# ==================== ТЕСТЫ ДЛЯ Read_Json_file ====================


class TestReadJsonFile:

    def test_init(self) -> None:
        manager = Read_Json_file()
        assert manager.categories == []

    def test_add_category(self) -> None:
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        assert len(manager.categories) == 1

    def test_get_all_categories(self) -> None:
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        manager.add_category(Category("К2", "О2"))
        result = manager.get_all_categories()
        assert len(result) == 2

    def test_get_total_products(self) -> None:
        manager = Read_Json_file()
        cat = Category(
            "К1",
            "О1",
            products=[
                Product("Т1", "О", 10.0, 1),
                Product("Т2", "О", 20.0, 2),
            ],
        )
        manager.add_category(cat)
        assert manager.get_total_products() == 2

    def test_str(self) -> None:
        manager = Read_Json_file()
        result = str(manager)
        assert "0 категорий" in result
        assert "0 товаров" in result

    def test_load_file_not_found(self, tmp_path: Path) -> None:
        manager = Read_Json_file.load_from_json(str(tmp_path / "no.json"))
        assert manager.categories == []

    def test_load_dict_format(self, tmp_path: Path) -> None:
        data = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [{"name": "Т1", "description": "О", "price": 10.0, "quantity": 1}],
                }
            ]
        }
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        manager = Read_Json_file.load_from_json(str(json_file))
        assert len(manager.categories) == 1

    def test_load_list_format(self, tmp_path: Path) -> None:
        data = [
            {
                "name": "К1",
                "description": "О",
                "products": [{"name": "Т1", "description": "О", "price": 10.0, "quantity": 1}],
            }
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        manager = Read_Json_file.load_from_json(str(json_file))
        assert len(manager.categories) == 1

    def test_load_unknown_format(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text('"строка"', encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))
        assert manager.categories == []

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text("{bad json}", encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))
        assert manager.categories == []

    def test_load_general_exception(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text('{"categories": []}', encoding="utf-8")
        with patch("builtins.open", side_effect=PermissionError("Доступ запрещён")):
            manager = Read_Json_file.load_from_json(str(json_file))
            assert manager.categories == []

    def test_load_empty_categories(self, tmp_path: Path) -> None:
        data = {"categories": []}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))
        assert manager.get_total_products() == 0

    def test_load_updates_class_counters(self, tmp_path: Path) -> None:
        """Загрузка из JSON обновляет все атрибуты класса."""
        data = {
            "categories": [
                {
                    "name": "К1",
                    "description": "О",
                    "products": [
                        {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1},
                        {"name": "Т2", "description": "О", "price": 20.0, "quantity": 2},
                    ],
                },
                {
                    "name": "К2",
                    "description": "О",
                    "products": [{"name": "Т3", "description": "О", "price": 30.0, "quantity": 3}],
                },
            ]
        }
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        Read_Json_file.load_from_json(str(json_file))

        assert Category.category_count == 2
        assert Category.product_count == 3
        assert Product.product_count == 3


# ==================== ИНТЕГРАЦИОННЫЙ ТЕСТ ====================


class TestIntegration:

    def test_full_workflow(self, tmp_path: Path) -> None:
        data = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [
                        {"name": "Смартфон", "description": "Флагман", "price": 79990.0, "quantity": 15},
                        {"name": "Ноутбук", "description": "Игровой", "price": 129990.0, "quantity": 8},
                    ],
                },
                {
                    "name": "Одежда",
                    "description": "Мужская",
                    "products": [{"name": "Куртка", "description": "Зимняя", "price": 8990.0, "quantity": 25}],
                },
            ]
        }

        json_file = tmp_path / "products.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        manager = Read_Json_file.load_from_json(str(json_file))

        assert len(manager.get_all_categories()) == 2
        assert manager.get_total_products() == 3
        assert Category.category_count == 2
        assert Category.product_count == 3
        assert Product.product_count == 3

    def test_full_workflow_with_manual_creation(self) -> None:
        """Ручное создание категорий и товаров без JSON."""
        p1 = Product("Смартфон", "Флагман", 79990.0, 15)
        p2 = Product("Ноутбук", "Игровой", 129990.0, 8)
        p3 = Product("Куртка", "Зимняя", 8990.0, 25)

        cat1 = Category("Электроника", "Гаджеты", products=[p1, p2])
        cat2 = Category("Одежда", "Мужская", products=[p3])

        manager = Read_Json_file()
        manager.add_category(cat1)
        manager.add_category(cat2)

        assert manager.get_total_products() == 3
        assert Category.category_count == 2
        assert Category.product_count == 3
        assert Product.product_count == 3
