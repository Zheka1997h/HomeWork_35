import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.learn_OOP import Category, LawnGrass, Product, Read_Json_file, Smartphone


@pytest.fixture(autouse=True)
def reset_counters() -> Iterator[None]:
    """Сбрасывает счётчики классов перед каждым тестом."""
    Product.product_count = 0
    Category.category_count = 0
    Category.product_count = 0
    yield
    Product.product_count = 0
    Category.category_count = 0
    Category.product_count = 0


# ==================== ТЕСТЫ ДЛЯ Product ====================


class TestProduct:

    def test_init_basic(self):
        """Базовая инициализация Product."""
        product = Product("Смартфон", "Описание", 79990.0, 15)
        assert product.name == "Смартфон"
        assert product.description == "Описание"
        assert product.price == 79990.0
        assert product.quantity == 15

    def test_init_zero_price(self, capsys: pytest.CaptureFixture[str]):
        """Инициализация с нулевой ценой."""
        product = Product("Тест", "Описание", 0, 1)
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 0.0

    def test_init_negative_price(self, capsys: pytest.CaptureFixture[str]):
        """Инициализация с отрицательной ценой."""
        product = Product("Тест", "Описание", -50, 1)
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 0.0

    def test_str(self):
        """Проверка __str__."""
        product = Product("Смартфон", "Описание", 100.0, 5)
        assert str(product) == "Смартфон, 100.0 руб. Остаток: 5 шт."

    def test_add_same_type(self):
        """Сложение двух Product."""
        p1 = Product("Товар1", "Описание", 100, 10)
        p2 = Product("Товар2", "Описание", 200, 2)
        assert p1 + p2 == 100 * 10 + 200 * 2 == 1400

    def test_add_different_type_raises(self):
        """Нельзя сложить Product с другим типом."""
        p1 = Product("Товар1", "Описание", 100, 10)
        with pytest.raises(TypeError):
            p1 + "not a product"

    def test_to_dict(self):
        """Проверка to_dict."""
        product = Product("Ноутбук", "Игровой", 129990.0, 8)
        result = product.to_dict()
        assert result == {
            "name": "Ноутбук",
            "description": "Игровой",
            "price": 129990.0,
            "quantity": 8,
        }

    def test_from_dict_product(self):
        """Создание Product из словаря."""
        data = {"name": "Наушники", "description": "Беспроводные", "price": 15990.0, "quantity": 30}
        product = Product.from_dict(data)
        assert isinstance(product, Product)
        assert product.name == "Наушники"
        assert product.price == 15990.0
        assert product.quantity == 30

    def test_from_dict_smartphone(self):
        """Создание Smartphone из словаря."""
        data = {
            "type": "Smartphone",
            "name": "iPhone",
            "description": "Флагман",
            "price": 99990.0,
            "quantity": 5,
            "efficiency": 95.5,
            "model": "15 Pro",
            "memory": 256,
            "color": "Black",
        }
        product = Product.from_dict(data)
        assert isinstance(product, Smartphone)
        assert product.model == "15 Pro"
        assert product.memory == 256

    def test_from_dict_lawn_grass(self):
        """Создание LawnGrass из словаря."""
        data = {
            "type": "LawnGrass",
            "name": "Green Lawn",
            "description": "Газон",
            "price": 500.0,
            "quantity": 10,
            "country": "Germany",
            "germination_period": 14,
            "color": "Green",
        }
        product = Product.from_dict(data)
        assert isinstance(product, LawnGrass)
        assert product.country == "Germany"
        assert product.germination_period == 14

    def test_price_setter_positive(self):
        """Установка положительной цены."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 150.0
        assert product.price == 150.0

    def test_price_setter_zero(self, capsys: pytest.CaptureFixture[str]):
        """Установка нулевой цены."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 0
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 100.0

    def test_price_setter_negative(self, capsys: pytest.CaptureFixture[str]):
        """Установка отрицательной цены."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = -50
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 100.0

    def test_price_setter_increase_no_confirm(self):
        """Повышение цены не требует подтверждения."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 150.0
        assert product.price == 150.0

    def test_price_setter_lower_with_confirm_yes(self, monkeypatch: pytest.MonkeyPatch):
        """Понижение цены с подтверждением 'y'."""
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "y")
        product.price = 80.0
        assert product.price == 80.0

    def test_price_setter_lower_with_confirm_uppercase(self, monkeypatch: pytest.MonkeyPatch):
        """Понижение цены с подтверждением 'Y'."""
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "Y")
        product.price = 80.0
        assert product.price == 80.0

    def test_price_setter_lower_with_confirm_no(self, monkeypatch: pytest.MonkeyPatch,
                                                capsys: pytest.CaptureFixture[str]):
        """Понижение цены с отменой 'n'."""
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "n")
        product.price = 80.0
        captured = capsys.readouterr()
        assert "Изменение цены отменено." in captured.out
        assert product.price == 100.0

    def test_new_product_create_new(self):
        """new_product создаёт новый товар."""
        data = {"name": "Молоко", "description": "1л", "price": 80.5, "quantity": 100}
        p = Product.new_product(data)
        assert p.name == "Молоко"
        assert Product.product_count == 1

    def test_new_product_update_existing(self):
        """new_product обновляет существующий товар."""
        existing = [Product("Хлеб", "Белый", 40, 10)]
        new_data = {"name": "Хлеб", "description": "Ржаной", "price": 50, "quantity": 5}
        result = Product.new_product(new_data, existing_products=existing)
        assert result is existing[0]
        assert result.quantity == 15
        assert result.price == 50.0

    def test_new_product_existing_higher_price_kept(self):
        """new_product сохраняет большую цену."""
        existing = [Product("Хлеб", "Белый", 50, 10)]
        new_data = {"name": "Хлеб", "description": "Ржаной", "price": 40, "quantity": 5}
        result = Product.new_product(new_data, existing_products=existing)
        assert result is existing[0]
        assert result.quantity == 15
        assert result.price == 50.0


# ==================== ТЕСТЫ ДЛЯ Smartphone ====================


class TestSmartphone:

    def test_init(self):
        """Инициализация Smartphone."""
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        assert phone.name == "iPhone"
        assert phone.price == 99990.0
        assert phone.quantity == 5
        assert phone.efficiency == 95.5
        assert phone.model == "15 Pro"
        assert phone.memory == 256
        assert phone.color == "Black"

    def test_str(self):
        """Проверка __str__ для Smartphone."""
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        result = str(phone)
        assert "iPhone" in result
        assert "15 Pro" in result
        assert "Black" in result
        assert "256GB" in result
        assert "99990.0" in result
        assert "5 шт." in result

    def test_to_dict(self):
        """Проверка to_dict для Smartphone."""
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        result = phone.to_dict()
        assert result["type"] == "Smartphone"
        assert result["name"] == "iPhone"
        assert result["price"] == 99990.0
        assert result["efficiency"] == 95.5
        assert result["model"] == "15 Pro"
        assert result["memory"] == 256
        assert result["color"] == "Black"

    def test_add_same_class(self):
        """Два смартфона можно складывать."""
        s1 = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        s2 = Smartphone("B", "d", 200.0, 3, 95.0, "M2", 256, "White")
        assert s1 + s2 == 100 * 2 + 200 * 3

    def test_add_different_class_raises_error(self):
        """Нельзя сложить смартфон и траву."""
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        grass = LawnGrass("B", "d", 200.0, 3, "DE", 14, "Green")
        with pytest.raises(TypeError):
            phone + grass

    def test_add_product_raises_error(self):
        """Нельзя сложить смартфон и обычный Product."""
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        product = Product("B", "d", 200.0, 3)
        with pytest.raises(TypeError):
            phone + product


# ==================== ТЕСТЫ ДЛЯ LawnGrass ====================


class TestLawnGrass:

    def test_init(self):
        """Инициализация LawnGrass."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        assert grass.name == "Green Lawn"
        assert grass.price == 500.0
        assert grass.quantity == 10
        assert grass.country == "Germany"
        assert grass.germination_period == 14
        assert grass.color == "Green"

    def test_str(self):
        """Проверка __str__ для LawnGrass."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        result = str(grass)
        assert "Green Lawn" in result
        assert "Green" in result
        assert "Germany" in result
        assert "500.0" in result
        assert "10 шт." in result

    def test_to_dict(self):
        """Проверка to_dict для LawnGrass."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        result = grass.to_dict()
        assert result["type"] == "LawnGrass"
        assert result["name"] == "Green Lawn"
        assert result["price"] == 500.0
        assert result["country"] == "Germany"
        assert result["germination_period"] == 14
        assert result["color"] == "Green"

    def test_add_same_class(self):
        """Две травы можно складывать."""
        g1 = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        g2 = LawnGrass("B", "d", 200.0, 3, "DE", 14, "Green")
        assert g1 + g2 == 100 * 2 + 200 * 3

    def test_add_different_class_raises_error(self):
        """Нельзя сложить траву и смартфон."""
        grass = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        phone = Smartphone("B", "d", 200.0, 3, 90.0, "M1", 128, "Black")
        with pytest.raises(TypeError):
            grass + phone

    def test_add_product_raises_error(self):
        """Нельзя сложить траву и обычный Product."""
        grass = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        product = Product("B", "d", 200.0, 3)
        with pytest.raises(TypeError):
            grass + product


# ==================== ТЕСТЫ ДЛЯ Category ====================


class TestCategory:

    def test_init_empty(self):
        """Создание категории без товаров."""
        category = Category("Электроника", "Гаджеты")
        assert category.name == "Электроника"
        assert category.description == "Гаджеты"
        assert category.products == ""

    def test_init_with_products(self):
        """Создание категории с товарами."""
        p1 = Product("Смартфон", "Описание", 79990.0, 15)
        p2 = Product("Ноутбук", "Игровой", 129990.0, 8)
        category = Category("Электроника", "Гаджеты", products=[p1, p2])
        assert category.name == "Электроника"
        assert category.get_total_products() == 2

    def test_add_product(self):
        """Добавление товара в категорию."""
        category = Category("Электроника", "Гаджеты")
        p1 = Product("Т1", "О", 10.0, 1)
        category.add_product(p1)
        assert category.get_total_products() == 1

    def test_add_product_invalid_type_string(self):
        """Нельзя добавить строку в категорию."""
        category = Category("Электроника", "Гаджеты")
        with pytest.raises(TypeError):
            category.add_product("Не продукт")

    def test_add_product_invalid_type_int(self):
        """Нельзя добавить число в категорию."""
        category = Category("Электроника", "Гаджеты")
        with pytest.raises(TypeError):
            category.add_product(123)

    def test_add_product_invalid_type_none(self):
        """Нельзя добавить None в категорию."""
        category = Category("Электроника", "Гаджеты")
        with pytest.raises(TypeError):
            category.add_product(None)

    def test_str_empty(self):
        """__str__ для пустой категории."""
        category = Category("Электроника", "Гаджеты")
        assert str(category) == "Электроника, количество продуктов: 0 шт."

    def test_str_with_products(self):
        """__str__ для категории с товарами."""
        category = Category("Электроника", "Гаджеты", products=[
            Product("Т1", "О", 10.0, 5),
            Product("Т2", "О", 20.0, 3),
        ])
        assert str(category) == "Электроника, количество продуктов: 8 шт."

    def test_products_property_empty(self):
        """Геттер products для пустой категории."""
        category = Category("Электроника", "Гаджеты")
        assert category.products == ""

    def test_products_property_with_items(self):
        """Геттер products с товарами."""
        category = Category("Фрукты", "Еда")
        p1 = Product("Яблоко", "Красное", 50, 15)
        p2 = Product("Банан", "Желтый", 80, 20)
        category.add_product(p1)
        category.add_product(p2)
        result = category.products
        assert "Яблоко" in result
        assert "Банан" in result

    def test_to_dict(self):
        """to_dict для категории."""
        category = Category("Электроника", "Гаджеты", products=[Product("Т1", "О", 10.0, 1)])
        result = category.to_dict()
        assert result["name"] == "Электроника"
        assert result["description"] == "Гаджеты"
        assert len(result["products"]) == 1

    def test_from_dict(self):
        """from_dict для категории."""
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

    def test_from_dict_empty_products(self):
        """from_dict для категории без товаров."""
        data = {"name": "Пустая", "description": "Без товаров"}
        category = Category.from_dict(data)
        assert category.get_total_products() == 0


# ==================== ТЕСТЫ ДЛЯ Read_Json_file ====================


class TestReadJsonFile:

    def test_init(self):
        """Инициализация Read_Json_file."""
        manager = Read_Json_file()
        assert manager.categories == []

    def test_add_category(self):
        """Добавление категории."""
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        assert len(manager.categories) == 1

    def test_get_all_categories(self):
        """Получение всех категорий."""
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        manager.add_category(Category("К2", "О2"))
        result = manager.get_all_categories()
        assert len(result) == 2

    def test_get_total_products(self):
        """Получение общего количества товаров."""
        manager = Read_Json_file()
        p1 = Product("P1", "d", 10.0, 5)
        p2 = Product("P2", "d", 20.0, 3)
        c = Category("A", "d", [p1, p2])
        manager.add_category(c)
        assert manager.get_total_products() == 2  # 2 разных товара

    def test_get_total_products_empty(self):
        """Общее количество товаров для пустого менеджера."""
        manager = Read_Json_file()
        assert manager.get_total_products() == 0

    def test_str(self):
        """__str__ для менеджера."""
        manager = Read_Json_file()
        result = str(manager)
        assert "0 категорий" in result
        assert "0 товаров" in result

    def test_load_from_json_file_not_found(self, tmp_path: Path):
        """Загрузка несуществующего файла."""
        manager = Read_Json_file.load_from_json(str(tmp_path / "no.json"))
        assert manager.categories == []

    def test_load_from_json_valid(self, tmp_path: Path):
        """Загрузка валидного JSON."""
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

    def test_load_from_json_list_format(self, tmp_path: Path):
        """Загрузка JSON в формате списка."""
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

    def test_load_from_json_invalid_json(self, tmp_path: Path):
        """Загрузка невалидного JSON."""
        json_file = tmp_path / "test.json"
        json_file.write_text("{bad json}", encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))
        assert manager.categories == []

    def test_load_from_json_with_smartphone(self, tmp_path: Path):
        """Загрузка JSON с Smartphone."""
        data = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [
                        {
                            "type": "Smartphone",
                            "name": "iPhone",
                            "description": "Флагман",
                            "price": 99990.0,
                            "quantity": 5,
                            "efficiency": 95.5,
                            "model": "15 Pro",
                            "memory": 256,
                            "color": "Black",
                        }
                    ],
                }
            ]
        }
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))
        assert len(manager.categories) == 1


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================


class TestIntegration:

    def test_full_workflow(self, tmp_path: Path):
        """Полный workflow с JSON."""
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

    def test_mixed_products_in_category(self):
        """Категория с разными типами товаров."""
        product = Product("Товар", "Описание", 100.0, 10)
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")

        category = Category("Магазин", "Все товары", products=[product, phone, grass])
        assert category.get_total_products() == 3

    def test_product_count_tracking(self):
        """Отслеживание счётчика Product."""
        Product("Т1", "О", 10.0, 1)
        Product("Т2", "О", 20.0, 2)
        assert Product.product_count == 2

    def test_category_count_tracking(self):
        """Отслеживание счётчика Category."""
        Category("К1", "О1")
        Category("К2", "О2")
        assert Category.category_count == 2