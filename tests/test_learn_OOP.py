import json
import sys
from abc import ABC
from pathlib import Path
from typing import Any, Iterator, List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Если файл с классами называется main.py, замени импорт на:
# from main import ...
from src.learn_OOP import (
    BaseEntity,
    BaseProduct,
    Category,
    CreationMixin,
    LawnGrass,
    Order,
    Product,
    Read_Json_file,
    Smartphone,
)


@pytest.fixture(autouse=True)
def reset_counters() -> Iterator[None]:
    """Сбрасывает счётчики классов перед каждым тестом."""
    # Явно указываем тип int для классовых атрибутов, чтобы mypy не ругался
    BaseProduct.product_count = 0  # type: ignore[attr-defined]
    Category.category_count = 0  # type: ignore[attr-defined]
    Category.product_count = 0  # type: ignore[attr-defined]
    yield
    BaseProduct.product_count = 0  # type: ignore[attr-defined]
    Category.category_count = 0  # type: ignore[attr-defined]
    Category.product_count = 0  # type: ignore[attr-defined]


# ==================== ТЕСТЫ ДЛЯ BaseProduct ====================


class TestBaseProduct:
    def test_cannot_instantiate_abstract_class(self) -> None:
        """Нельзя создать экземпляр абстрактного класса BaseProduct."""
        with pytest.raises(TypeError):
            BaseProduct("Тест", "Описание", 100.0, 1)  # type: ignore[abstract]

    def test_is_abstract(self) -> None:
        """BaseProduct является абстрактным классом."""
        assert issubclass(BaseProduct, ABC)
        # __abstractmethods__ — это динамический атрибут ABC, mypy его не видит
        assert len(getattr(BaseProduct, "__abstractmethods__")) > 0  # type: ignore[attr-defined]

    def test_has_abstract_init(self) -> None:
        """BaseProduct имеет абстрактный __init__."""
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "__init__" in abstract_methods

    def test_has_abstract_str(self) -> None:
        """BaseProduct имеет абстрактный __str__."""
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "__str__" in abstract_methods

    def test_has_abstract_add(self) -> None:
        """BaseProduct имеет абстрактный __add__."""
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "__add__" in abstract_methods

    def test_has_abstract_to_dict(self) -> None:
        """BaseProduct имеет абстрактный to_dict."""
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "to_dict" in abstract_methods


# ==================== ТЕСТЫ ДЛЯ BaseEntity ====================


class TestBaseEntity:
    def test_cannot_instantiate_abstract_class(self) -> None:
        """Нельзя создать экземпляр абстрактного класса BaseEntity."""
        with pytest.raises(TypeError):
            BaseEntity("Тест", "Описание")  # type: ignore[abstract]

    def test_is_abstract(self) -> None:
        """BaseEntity является абстрактным классом."""
        assert issubclass(BaseEntity, ABC)
        assert len(getattr(BaseEntity, "__abstractmethods__")) > 0  # type: ignore[attr-defined]

    def test_has_abstract_init(self) -> None:
        """BaseEntity имеет абстрактный __init__."""
        abstract_methods: Any = getattr(BaseEntity, "__abstractmethods__")
        assert "__init__" in abstract_methods

    def test_has_abstract_str(self) -> None:
        """BaseEntity имеет абстрактный __str__."""
        abstract_methods: Any = getattr(BaseEntity, "__abstractmethods__")
        assert "__str__" in abstract_methods


# ==================== ТЕСТЫ ДЛЯ CreationMixin ====================


class TestCreationMixin:
    def test_product_creation_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При создании Product миксин печатает имя класса и параметры."""
        Product("Продукт1", "Описание продукта", 1200, 10)
        captured = capsys.readouterr()
        assert "Product('Продукт1', 'Описание продукта', 1200, 10)" in captured.out

    def test_smartphone_creation_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При создании Smartphone миксин печатает имя класса и базовые параметры."""
        Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        captured = capsys.readouterr()
        assert "Smartphone('iPhone', 'Флагман', 99990.0, 5)" in captured.out

    def test_lawn_grass_creation_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При создании LawnGrass миксин печатает имя класса и базовые параметры."""
        LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        captured = capsys.readouterr()
        assert "LawnGrass('Green Lawn', 'Газон', 500.0, 10)" in captured.out

    def test_mixin_in_product_mro(self) -> None:
        """CreationMixin находится в цепочке наследования Product."""
        assert CreationMixin in Product.__mro__

    def test_mixin_in_smartphone_mro(self) -> None:
        """CreationMixin находится в цепочке наследования Smartphone."""
        assert CreationMixin in Smartphone.__mro__

    def test_mixin_in_lawn_grass_mro(self) -> None:
        """CreationMixin находится в цепочке наследования LawnGrass."""
        assert CreationMixin in LawnGrass.__mro__


# ==================== ТЕСТЫ ДЛЯ Product ====================


class TestProduct:
    def test_init_basic(self) -> None:
        """Базовая инициализация Product."""
        product = Product("Смартфон", "Описание", 79990.0, 15)
        assert product.name == "Смартфон"
        assert product.description == "Описание"
        assert product.price == 79990.0
        assert product.quantity == 15

    def test_init_zero_price(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Инициализация с нулевой ценой."""
        product = Product("Тест", "Описание", 0, 1)
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 0.0

    def test_init_negative_price(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Инициализация с отрицательной ценой."""
        product = Product("Тест", "Описание", -50, 1)
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 0.0

    def test_str(self) -> None:
        """Проверка __str__."""
        product = Product("Смартфон", "Описание", 100.0, 5)
        assert str(product) == "Смартфон, 100.0 руб. Остаток: 5 шт."

    def test_add_same_type(self) -> None:
        """Сложение двух Product."""
        p1 = Product("Товар1", "Описание", 100, 10)
        p2 = Product("Товар2", "Описание", 200, 2)
        assert p1 + p2 == 100 * 10 + 200 * 2 == 1400

    def test_add_different_type_raises(self) -> None:
        """Нельзя сложить Product с другим типом."""
        p1 = Product("Товар1", "Описание", 100, 10)
        with pytest.raises(TypeError):
            _ = p1 + "not a product"  # type: ignore[operator]

    def test_to_dict(self) -> None:
        """Проверка to_dict."""
        product = Product("Ноутбук", "Игровой", 129990.0, 8)
        result = product.to_dict()
        assert result == {
            "name": "Ноутбук",
            "description": "Игровой",
            "price": 129990.0,
            "quantity": 8,
        }

    def test_from_dict_product(self) -> None:
        """Создание Product из словаря."""
        data: dict[str, Any] = {
            "name": "Наушники",
            "description": "Беспроводные",
            "price": 15990.0,
            "quantity": 30,
        }
        product = Product.from_dict(data)  # type: ignore[attr-defined]
        assert isinstance(product, Product)
        assert product.name == "Наушники"
        assert product.price == 15990.0
        assert product.quantity == 30

    def test_from_dict_smartphone(self) -> None:
        """Создание Smartphone из словаря."""
        data: dict[str, Any] = {
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
        product = Product.from_dict(data)  # type: ignore[attr-defined]
        assert isinstance(product, Smartphone)
        assert product.model == "15 Pro"  # type: ignore[attr-defined]
        assert product.memory == 256  # type: ignore[attr-defined]

    def test_from_dict_lawn_grass(self) -> None:
        """Создание LawnGrass из словаря."""
        data: dict[str, Any] = {
            "type": "LawnGrass",
            "name": "Green Lawn",
            "description": "Газон",
            "price": 500.0,
            "quantity": 10,
            "country": "Germany",
            "germination_period": 14,
            "color": "Green",
        }
        product = Product.from_dict(data)  # type: ignore[attr-defined]
        assert isinstance(product, LawnGrass)
        assert product.country == "Germany"  # type: ignore[attr-defined]
        assert product.germination_period == 14  # type: ignore[attr-defined]

    def test_price_setter_positive(self) -> None:
        """Установка положительной цены."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 150.0
        assert product.price == 150.0

    def test_price_setter_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Установка нулевой цены."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 0
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 100.0

    def test_price_setter_negative(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Установка отрицательной цены."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = -50
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 100.0

    def test_price_setter_increase_no_confirm(self) -> None:
        """Повышение цены не требует подтверждения."""
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 150.0
        assert product.price == 150.0

    def test_price_setter_lower_with_confirm_yes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Понижение цены с подтверждением 'y'."""
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "y")
        product.price = 80.0
        assert product.price == 80.0

    def test_price_setter_lower_with_confirm_uppercase(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Понижение цены с подтверждением 'Y'."""
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "Y")
        product.price = 80.0
        assert product.price == 80.0

    def test_price_setter_lower_with_confirm_no(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Понижение цены с отменой 'n'."""
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "n")
        product.price = 80.0
        captured = capsys.readouterr()
        assert "Изменение цены отменено." in captured.out
        assert product.price == 100.0

    def test_new_product_create_new(self) -> None:
        """new_product создаёт новый товар."""
        data: dict[str, Any] = {"name": "Молоко", "description": "1л", "price": 80.5, "quantity": 100}
        p = Product.new_product(data)  # type: ignore[attr-defined]
        assert p.name == "Молоко"
        assert BaseProduct.product_count == 1  # type: ignore[attr-defined]

    def test_new_product_update_existing(self) -> None:
        """new_product обновляет существующий товар."""
        existing: List[Product] = [Product("Хлеб", "Белый", 40, 10)]
        new_data: dict[str, Any] = {
            "name": "Хлеб",
            "description": "Ржаной",
            "price": 50,
            "quantity": 5,
        }
        result = Product.new_product(new_data, existing_products=existing)  # type: ignore[attr-defined]
        assert result is existing[0]
        assert result.quantity == 15
        assert result.price == 50.0

    def test_new_product_existing_higher_price_kept(self) -> None:
        """new_product сохраняет большую цену."""
        existing: List[Product] = [Product("Хлеб", "Белый", 50, 10)]
        new_data: dict[str, Any] = {
            "name": "Хлеб",
            "description": "Ржаной",
            "price": 40,
            "quantity": 5,
        }
        result = Product.new_product(new_data, existing_products=existing)  # type: ignore[attr-defined]
        assert result is existing[0]
        assert result.quantity == 15
        assert result.price == 50.0

    def test_product_inherits_base_product(self) -> None:
        """Product наследует BaseProduct."""
        product = Product("Тест", "Описание", 10.0, 1)
        assert isinstance(product, BaseProduct)

    def test_product_inherits_creation_mixin(self) -> None:
        """Product наследует CreationMixin."""
        product = Product("Тест", "Описание", 10.0, 1)
        assert isinstance(product, CreationMixin)


# ==================== ТЕСТЫ ДЛЯ Smartphone ====================


class TestSmartphone:
    def test_init(self) -> None:
        """Инициализация Smartphone."""
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        assert phone.name == "iPhone"
        assert phone.price == 99990.0
        assert phone.quantity == 5
        assert phone.efficiency == 95.5
        assert phone.model == "15 Pro"
        assert phone.memory == 256
        assert phone.color == "Black"

    def test_str(self) -> None:
        """Проверка __str__ для Smartphone."""
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        result = str(phone)
        assert "iPhone" in result
        assert "15 Pro" in result
        assert "Black" in result
        assert "256GB" in result
        assert "99990.0" in result
        assert "5 шт." in result

    def test_to_dict(self) -> None:
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

    def test_add_same_class(self) -> None:
        """Два смартфона можно складывать."""
        s1 = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        s2 = Smartphone("B", "d", 200.0, 3, 95.0, "M2", 256, "White")
        assert s1 + s2 == 100 * 2 + 200 * 3

    def test_add_different_class_raises_error(self) -> None:
        """Нельзя сложить смартфон и траву."""
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        grass = LawnGrass("B", "d", 200.0, 3, "DE", 14, "Green")
        with pytest.raises(TypeError):
            _ = phone + grass  # type: ignore[operator]

    def test_add_product_raises_error(self) -> None:
        """Нельзя сложить смартфон и обычный Product."""
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        product = Product("B", "d", 200.0, 3)
        with pytest.raises(TypeError):
            _ = phone + product  # type: ignore[operator]

    def test_smartphone_inherits_product(self) -> None:
        """Smartphone наследует Product."""
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        assert isinstance(phone, Product)

    def test_smartphone_inherits_base_product(self) -> None:
        """Smartphone наследует BaseProduct."""
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        assert isinstance(phone, BaseProduct)


# ==================== ТЕСТЫ ДЛЯ LawnGrass ====================


class TestLawnGrass:
    def test_init(self) -> None:
        """Инициализация LawnGrass."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        assert grass.name == "Green Lawn"
        assert grass.price == 500.0
        assert grass.quantity == 10
        assert grass.country == "Germany"
        assert grass.germination_period == 14
        assert grass.color == "Green"

    def test_str(self) -> None:
        """Проверка __str__ для LawnGrass."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        result = str(grass)
        assert "Green Lawn" in result
        assert "Green" in result
        assert "Germany" in result
        assert "500.0" in result
        assert "10 шт." in result

    def test_to_dict(self) -> None:
        """Проверка to_dict для LawnGrass."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        result = grass.to_dict()
        assert result["type"] == "LawnGrass"
        assert result["name"] == "Green Lawn"
        assert result["price"] == 500.0
        assert result["country"] == "Germany"
        assert result["germination_period"] == 14
        assert result["color"] == "Green"

    def test_add_same_class(self) -> None:
        """Две травы можно складывать."""
        g1 = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        g2 = LawnGrass("B", "d", 200.0, 3, "DE", 14, "Green")
        assert g1 + g2 == 100 * 2 + 200 * 3

    def test_add_different_class_raises_error(self) -> None:
        """Нельзя сложить траву и смартфон."""
        grass = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        phone = Smartphone("B", "d", 200.0, 3, 90.0, "M1", 128, "Black")
        with pytest.raises(TypeError):
            _ = grass + phone  # type: ignore[operator]

    def test_add_product_raises_error(self) -> None:
        """Нельзя сложить траву и обычный Product."""
        grass = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        product = Product("B", "d", 200.0, 3)
        with pytest.raises(TypeError):
            _ = grass + product  # type: ignore[operator]

    def test_lawn_grass_inherits_product(self) -> None:
        """LawnGrass наследует Product."""
        grass = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        assert isinstance(grass, Product)

    def test_lawn_grass_inherits_base_product(self) -> None:
        """LawnGrass наследует BaseProduct."""
        grass = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        assert isinstance(grass, BaseProduct)


# ==================== ТЕСТЫ ДЛЯ Category ====================


class TestCategory:
    def test_init_empty(self) -> None:
        """Создание категории без товаров."""
        category = Category("Электроника", "Гаджеты")
        assert category.name == "Электроника"
        assert category.description == "Гаджеты"
        assert category.products == ""

    def test_init_with_products(self) -> None:
        """Создание категории с товарами."""
        p1 = Product("Смартфон", "Описание", 79990.0, 15)
        p2 = Product("Ноутбук", "Игровой", 129990.0, 8)
        category = Category("Электроника", "Гаджеты", products=[p1, p2])
        assert category.name == "Электроника"
        assert category.get_total_products() == 2

    def test_add_product(self) -> None:
        """Добавление товара в категорию."""
        category = Category("Электроника", "Гаджеты")
        p1 = Product("Т1", "О", 10.0, 1)
        category.add_product(p1)
        assert category.get_total_products() == 1

    def test_add_product_invalid_type_string(self) -> None:
        """Нельзя добавить строку в категорию."""
        category = Category("Электроника", "Гаджеты")
        with pytest.raises(TypeError):
            category.add_product("Не продукт")  # type: ignore[arg-type]

    def test_add_product_invalid_type_int(self) -> None:
        """Нельзя добавить число в категорию."""
        category = Category("Электроника", "Гаджеты")
        with pytest.raises(TypeError):
            category.add_product(123)  # type: ignore[arg-type]

    def test_add_product_invalid_type_none(self) -> None:
        """Нельзя добавить None в категорию."""
        category = Category("Электроника", "Гаджеты")
        with pytest.raises(TypeError):
            category.add_product(None)  # type: ignore[arg-type]

    def test_str_empty(self) -> None:
        """__str__ для пустой категории."""
        category = Category("Электроника", "Гаджеты")
        assert str(category) == "Электроника, количество продуктов: 0 шт."

    def test_str_with_products(self) -> None:
        """__str__ для категории с товарами."""
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[
                Product("Т1", "О", 10.0, 5),
                Product("Т2", "О", 20.0, 3),
            ],
        )
        assert str(category) == "Электроника, количество продуктов: 8 шт."

    def test_products_property_empty(self) -> None:
        """Геттер products для пустой категории."""
        category = Category("Электроника", "Гаджеты")
        assert category.products == ""

    def test_products_property_with_items(self) -> None:
        """Геттер products с товарами."""
        category = Category("Фрукты", "Еда")
        p1 = Product("Яблоко", "Красное", 50, 15)
        p2 = Product("Банан", "Желтый", 80, 20)
        category.add_product(p1)
        category.add_product(p2)
        result = category.products
        assert "Яблоко" in result
        assert "Банан" in result

    def test_to_dict(self) -> None:
        """to_dict для категории."""
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[Product("Т1", "О", 10.0, 1)],
        )
        result = category.to_dict()
        assert result["name"] == "Электроника"
        assert result["description"] == "Гаджеты"
        assert len(result["products"]) == 1

    def test_from_dict(self) -> None:
        """from_dict для категории."""
        data: dict[str, Any] = {
            "name": "Электроника",
            "description": "Гаджеты",
            "products": [
                {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1},
                {"name": "Т2", "description": "О", "price": 20.0, "quantity": 2},
            ],
        }
        category = Category.from_dict(data)  # type: ignore[attr-defined]
        assert category.name == "Электроника"
        assert category.get_total_products() == 2

    def test_from_dict_empty_products(self) -> None:
        """from_dict для категории без товаров."""
        data: dict[str, Any] = {"name": "Пустая", "description": "Без товаров"}
        category = Category.from_dict(data)  # type: ignore[attr-defined]
        assert category.get_total_products() == 0

    def test_category_inherits_base_entity(self) -> None:
        """Category наследует BaseEntity."""
        category = Category("Электроника", "Гаджеты")
        assert isinstance(category, BaseEntity)


# ==================== ТЕСТЫ ДЛЯ Order ====================


class TestOrder:
    def test_init(self) -> None:
        """Инициализация Order."""
        product = Product("Смартфон", "Описание", 79990.0, 15)
        order = Order("Заказ1", "Первый заказ", product, 3)
        assert order.name == "Заказ1"
        assert order.description == "Первый заказ"
        assert order.product is product
        assert order.quantity == 3
        assert order.total_cost == 79990.0 * 3

    def test_str(self) -> None:
        """Проверка __str__ для Order."""
        product = Product("Смартфон", "Описание", 100.0, 10)
        order = Order("Заказ1", "Описание заказа", product, 2)
        result = str(order)
        assert "Заказ 'Заказ1'" in result
        assert "Смартфон" in result
        assert "количество: 2 шт." in result
        assert "итоговая стоимость: 200.0 руб." in result

    def test_total_cost_with_smartphone(self) -> None:
        """Стоимость заказа со смартфоном."""
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        order = Order("Заказ", "Покупка телефона", phone, 2)
        assert order.total_cost == 99990.0 * 2

    def test_total_cost_with_lawn_grass(self) -> None:
        """Стоимость заказа с травой."""
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        order = Order("Заказ", "Озеленение", grass, 4)
        assert order.total_cost == 500.0 * 4

    def test_order_inherits_base_entity(self) -> None:
        """Order наследует BaseEntity."""
        product = Product("Тест", "Описание", 10.0, 1)
        order = Order("Заказ", "Описание", product, 1)
        assert isinstance(order, BaseEntity)

    def test_order_contains_only_one_product(self) -> None:
        """В заказе может быть указан только один товар."""
        product = Product("Тест", "Описание", 10.0, 1)
        order = Order("Заказ", "Описание", product, 1)
        assert isinstance(order.product, Product)
        assert not isinstance(order.product, list)


# ==================== ТЕСТЫ ДЛЯ Read_Json_file ====================


class TestReadJsonFile:
    def test_init(self) -> None:
        """Инициализация Read_Json_file."""
        manager = Read_Json_file()
        assert manager.categories == []

    def test_add_category(self) -> None:
        """Добавление категории."""
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        assert len(manager.categories) == 1

    def test_get_all_categories(self) -> None:
        """Получение всех категорий."""
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        manager.add_category(Category("К2", "О2"))
        result = manager.get_all_categories()
        assert len(result) == 2

    def test_get_total_products(self) -> None:
        """Получение общего количества товаров."""
        manager = Read_Json_file()
        p1 = Product("P1", "d", 10.0, 5)
        p2 = Product("P2", "d", 20.0, 3)
        c = Category("A", "d", [p1, p2])
        manager.add_category(c)
        assert manager.get_total_products() == 2

    def test_get_total_products_empty(self) -> None:
        """Общее количество товаров для пустого менеджера."""
        manager = Read_Json_file()
        assert manager.get_total_products() == 0

    def test_str(self) -> None:
        """__str__ для менеджера."""
        manager = Read_Json_file()
        result = str(manager)
        assert "0 категорий" in result
        assert "0 товаров" in result

    def test_load_from_json_file_not_found(self, tmp_path: Path) -> None:
        """Загрузка несуществующего файла."""
        manager = Read_Json_file.load_from_json(str(tmp_path / "no.json"))  # type: ignore[attr-defined]
        assert manager.categories == []

    def test_load_from_json_valid(self, tmp_path: Path) -> None:
        """Загрузка валидного JSON."""
        data: dict[str, Any] = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [
                        {
                            "name": "Т1",
                            "description": "О",
                            "price": 10.0,
                            "quantity": 1,
                        }
                    ],
                }
            ]
        }
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))  # type: ignore[attr-defined]
        assert len(manager.categories) == 1

    def test_load_from_json_list_format(self, tmp_path: Path) -> None:
        """Загрузка JSON в формате списка."""
        data: List[dict[str, Any]] = [
            {
                "name": "К1",
                "description": "О",
                "products": [
                    {
                        "name": "Т1",
                        "description": "О",
                        "price": 10.0,
                        "quantity": 1,
                    }
                ],
            }
        ]
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))  # type: ignore[attr-defined]
        assert len(manager.categories) == 1

    def test_load_from_json_invalid_json(self, tmp_path: Path) -> None:
        """Загрузка невалидного JSON."""
        json_file = tmp_path / "test.json"
        json_file.write_text("{bad json}", encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))  # type: ignore[attr-defined]
        assert manager.categories == []

    def test_load_from_json_with_smartphone(self, tmp_path: Path) -> None:
        """Загрузка JSON с Smartphone."""
        data: dict[str, Any] = {
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
        manager = Read_Json_file.load_from_json(str(json_file))  # type: ignore[attr-defined]
        assert len(manager.categories) == 1


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================


class TestIntegration:
    def test_full_workflow(self, tmp_path: Path) -> None:
        """Полный workflow с JSON."""
        data: dict[str, Any] = {
            "categories": [
                {
                    "name": "Электроника",
                    "description": "Гаджеты",
                    "products": [
                        {
                            "name": "Смартфон",
                            "description": "Флагман",
                            "price": 79990.0,
                            "quantity": 15,
                        },
                        {
                            "name": "Ноутбук",
                            "description": "Игровой",
                            "price": 129990.0,
                            "quantity": 8,
                        },
                    ],
                },
                {
                    "name": "Одежда",
                    "description": "Мужская",
                    "products": [
                        {
                            "name": "Куртка",
                            "description": "Зимняя",
                            "price": 8990.0,
                            "quantity": 25,
                        }
                    ],
                },
            ]
        }
        json_file = tmp_path / "products.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))  # type: ignore[attr-defined]
        assert len(manager.get_all_categories()) == 2
        assert manager.get_total_products() == 3

    def test_mixed_products_in_category(self) -> None:
        """Категория с разными типами товаров."""
        product = Product("Товар", "Описание", 100.0, 10)
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")

        category = Category("Магазин", "Все товары", products=[product, phone, grass])
        assert category.get_total_products() == 3

    def test_product_count_tracking(self) -> None:
        """Отслеживание счётчика Product."""
        Product("Т1", "О", 10.0, 1)
        Product("Т2", "О", 20.0, 2)
        assert Product.product_count == 2  # type: ignore[attr-defined]

    def test_category_count_tracking(self) -> None:
        """Отслеживание счётчика Category."""
        Category("К1", "О1")
        Category("К2", "О2")
        assert Category.category_count == 2  # type: ignore[attr-defined]

    def test_order_with_category_workflow(self) -> None:
        """Совместная работа Category и Order через BaseEntity."""
        product = Product("Товар", "Описание", 100.0, 10)

        category = Category("Каталог", "Все товары", products=[product])
        order = Order("Заказ", "Покупка товара", product, 3)

        assert isinstance(category, BaseEntity)
        assert isinstance(order, BaseEntity)
        assert order.total_cost == 300.0
        assert category.get_total_products() == 1
