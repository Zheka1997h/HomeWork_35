import json
import sys
from abc import ABC
from pathlib import Path
from typing import Any, Iterator, List

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.learn_OOP import (BaseEntity, BaseProduct, Category, CreationMixin, LawnGrass, Order, Product, Read_Json_file,
                           Smartphone, ZeroQuantityError)


@pytest.fixture(autouse=True)
def reset_counters() -> Iterator[None]:
    """Сбрасывает счётчики классов перед каждым тестом."""
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
        with pytest.raises(TypeError):
            BaseProduct("Тест", "Описание", 100.0, 1)  # type: ignore[abstract]

    def test_is_abstract(self) -> None:
        assert issubclass(BaseProduct, ABC)
        assert len(getattr(BaseProduct, "__abstractmethods__")) > 0

    def test_has_abstract_init(self) -> None:
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "__init__" in abstract_methods

    def test_has_abstract_str(self) -> None:
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "__str__" in abstract_methods

    def test_has_abstract_add(self) -> None:
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "__add__" in abstract_methods

    def test_has_abstract_to_dict(self) -> None:
        abstract_methods: Any = getattr(BaseProduct, "__abstractmethods__")
        assert "to_dict" in abstract_methods


# ==================== ТЕСТЫ ДЛЯ BaseEntity ====================


class TestBaseEntity:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            BaseEntity("Тест", "Описание")  # type: ignore[abstract]

    def test_is_abstract(self) -> None:
        assert issubclass(BaseEntity, ABC)
        assert len(getattr(BaseEntity, "__abstractmethods__")) > 0

    def test_has_abstract_init(self) -> None:
        abstract_methods: Any = getattr(BaseEntity, "__abstractmethods__")
        assert "__init__" in abstract_methods

    def test_has_abstract_str(self) -> None:
        abstract_methods: Any = getattr(BaseEntity, "__abstractmethods__")
        assert "__str__" in abstract_methods


# ==================== ТЕСТЫ ДЛЯ CreationMixin ====================


class TestCreationMixin:
    def test_product_creation_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        Product("Продукт1", "Описание продукта", 1200, 10)
        captured = capsys.readouterr()
        assert "Product('Продукт1', 'Описание продукта', 1200, 10)" in captured.out

    def test_smartphone_creation_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        captured = capsys.readouterr()
        assert "Smartphone('iPhone', 'Флагман', 99990.0, 5)" in captured.out

    def test_lawn_grass_creation_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        captured = capsys.readouterr()
        assert "LawnGrass('Green Lawn', 'Газон', 500.0, 10)" in captured.out

    def test_mixin_in_product_mro(self) -> None:
        assert CreationMixin in Product.__mro__

    def test_mixin_in_smartphone_mro(self) -> None:
        assert CreationMixin in Smartphone.__mro__

    def test_mixin_in_lawn_grass_mro(self) -> None:
        assert CreationMixin in LawnGrass.__mro__


# ==================== ТЕСТЫ ДЛЯ Product ====================


class TestProduct:
    def test_init_basic(self) -> None:
        product = Product("Смартфон", "Описание", 79990.0, 15)
        assert product.name == "Смартфон"
        assert product.description == "Описание"
        assert product.price == 79990.0
        assert product.quantity == 15

    # ========== ЗАДАНИЕ 1: ValueError при нулевом количестве ==========
    def test_init_zero_quantity_raises_value_error(self) -> None:
        """При создании продукта с нулевым количеством выбрасывается ValueError."""
        with pytest.raises(ValueError, match="Товар с нулевым количеством не может быть добавлен"):
            Product("Тест", "Описание", 100.0, 0)

    def test_init_zero_quantity_message(self) -> None:
        """Проверка точного текста сообщения ValueError."""
        try:
            Product("Тест", "Описание", 100.0, 0)
        except ValueError as e:
            assert str(e) == "Товар с нулевым количеством не может быть добавлен"
        else:
            pytest.fail("ValueError не был выброшен")

    def test_init_zero_quantity_not_created(self) -> None:
        """Продукт с нулевым количеством не создаётся и не увеличивает счётчик."""
        with pytest.raises(ValueError):
            Product("Тест", "Описание", 100.0, 0)
        assert BaseProduct.product_count == 0  # type: ignore[attr-defined]

    def test_init_zero_price(self, capsys: pytest.CaptureFixture[str]) -> None:
        product = Product("Тест", "Описание", 0, 1)
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 0.0

    def test_init_negative_price(self, capsys: pytest.CaptureFixture[str]) -> None:
        product = Product("Тест", "Описание", -50, 1)
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 0.0

    def test_str(self) -> None:
        product = Product("Смартфон", "Описание", 100.0, 5)
        assert str(product) == "Смартфон, 100.0 руб. Остаток: 5 шт."

    def test_add_same_type(self) -> None:
        p1 = Product("Товар1", "Описание", 100, 10)
        p2 = Product("Товар2", "Описание", 200, 2)
        assert p1 + p2 == 1400

    def test_add_different_type_raises(self) -> None:
        p1 = Product("Товар1", "Описание", 100, 10)
        with pytest.raises(TypeError):
            _ = p1 + "not a product"  # type: ignore[operator]

    def test_to_dict(self) -> None:
        product = Product("Ноутбук", "Игровой", 129990.0, 8)
        assert product.to_dict() == {
            "name": "Ноутбук",
            "description": "Игровой",
            "price": 129990.0,
            "quantity": 8,
        }

    def test_from_dict_product(self) -> None:
        data: dict[str, Any] = {
            "name": "Наушники",
            "description": "Беспроводные",
            "price": 15990.0,
            "quantity": 30,
        }
        product = Product.from_dict(data)
        assert isinstance(product, Product)
        assert product.name == "Наушники"

    def test_from_dict_smartphone(self) -> None:
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
        product = Product.from_dict(data)
        assert isinstance(product, Smartphone)

    def test_from_dict_lawn_grass(self) -> None:
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
        product = Product.from_dict(data)
        assert isinstance(product, LawnGrass)

    def test_price_setter_positive(self) -> None:
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 150.0
        assert product.price == 150.0

    def test_price_setter_zero(self, capsys: pytest.CaptureFixture[str]) -> None:
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = 0
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 100.0

    def test_price_setter_negative(self, capsys: pytest.CaptureFixture[str]) -> None:
        product = Product("Тест", "Описание", 100.0, 1)
        product.price = -50
        captured = capsys.readouterr()
        assert "Цена не должна быть нулевая или отрицательная" in captured.out
        assert product.price == 100.0

    def test_price_setter_lower_with_confirm_yes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "y")
        product.price = 80.0
        assert product.price == 80.0

    def test_price_setter_lower_with_confirm_no(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        product = Product("Тест", "Описание", 100.0, 1)
        monkeypatch.setattr("builtins.input", lambda _: "n")
        product.price = 80.0
        captured = capsys.readouterr()
        assert "Изменение цены отменено." in captured.out
        assert product.price == 100.0

    def test_new_product_create_new(self) -> None:
        data: dict[str, Any] = {"name": "Молоко", "description": "1л", "price": 80.5, "quantity": 100}
        p = Product.new_product(data)
        assert p.name == "Молоко"
        assert BaseProduct.product_count == 1  # type: ignore[attr-defined]

    def test_new_product_update_existing(self) -> None:
        existing: List[Product] = [Product("Хлеб", "Белый", 40, 10)]
        new_data: dict[str, Any] = {
            "name": "Хлеб",
            "description": "Ржаной",
            "price": 50,
            "quantity": 5,
        }
        result = Product.new_product(new_data, existing_products=existing)
        assert result is existing[0]
        assert result.quantity == 15
        assert result.price == 50.0

    def test_product_inherits_base_product(self) -> None:
        product = Product("Тест", "Описание", 10.0, 1)
        assert isinstance(product, BaseProduct)

    def test_product_inherits_creation_mixin(self) -> None:
        product = Product("Тест", "Описание", 10.0, 1)
        assert isinstance(product, CreationMixin)


# ==================== ТЕСТЫ ДЛЯ Smartphone ====================


class TestSmartphone:
    def test_init(self) -> None:
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        assert phone.name == "iPhone"
        assert phone.model == "15 Pro"
        assert phone.memory == 256
        assert phone.color == "Black"

    def test_str(self) -> None:
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        result = str(phone)
        assert "iPhone" in result
        assert "256GB" in result

    def test_to_dict(self) -> None:
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        result = phone.to_dict()
        assert result["type"] == "Smartphone"

    def test_add_same_class(self) -> None:
        s1 = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        s2 = Smartphone("B", "d", 200.0, 3, 95.0, "M2", 256, "White")
        assert s1 + s2 == 800

    def test_add_different_class_raises_error(self) -> None:
        phone = Smartphone("A", "d", 100.0, 2, 90.0, "M1", 128, "Black")
        grass = LawnGrass("B", "d", 200.0, 3, "DE", 14, "Green")
        with pytest.raises(TypeError):
            _ = phone + grass

    def test_zero_quantity_raises(self) -> None:
        """Smartphone с нулевым количеством также выбрасывает ValueError."""
        with pytest.raises(ValueError, match="Товар с нулевым количеством не может быть добавлен"):
            Smartphone("A", "d", 100.0, 0, 90.0, "M1", 128, "Black")


# ==================== ТЕСТЫ ДЛЯ LawnGrass ====================


class TestLawnGrass:
    def test_init(self) -> None:
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        assert grass.name == "Green Lawn"
        assert grass.country == "Germany"

    def test_str(self) -> None:
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        result = str(grass)
        assert "Green Lawn" in result
        assert "Germany" in result

    def test_to_dict(self) -> None:
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        result = grass.to_dict()
        assert result["type"] == "LawnGrass"

    def test_add_same_class(self) -> None:
        g1 = LawnGrass("A", "d", 100.0, 2, "RU", 10, "Green")
        g2 = LawnGrass("B", "d", 200.0, 3, "DE", 14, "Green")
        assert g1 + g2 == 800

    def test_zero_quantity_raises(self) -> None:
        """LawnGrass с нулевым количеством также выбрасывает ValueError."""
        with pytest.raises(ValueError, match="Товар с нулевым количеством не может быть добавлен"):
            LawnGrass("A", "d", 100.0, 0, "RU", 10, "Green")


# ==================== ТЕСТЫ ДЛЯ Category ====================


class TestCategory:
    def test_init_empty(self) -> None:
        category = Category("Электроника", "Гаджеты")
        assert category.name == "Электроника"
        assert category.products == ""

    def test_init_with_products(self) -> None:
        p1 = Product("Смартфон", "Описание", 79990.0, 15)
        p2 = Product("Ноутбук", "Игровой", 129990.0, 8)
        category = Category("Электроника", "Гаджеты", products=[p1, p2])
        assert category.get_total_products() == 2

    def test_add_product(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Добавление товара в категорию печатает сообщение об успехе."""
        category = Category("Электроника", "Гаджеты")
        p1 = Product("Т1", "О", 10.0, 1)
        category.add_product(p1)
        captured = capsys.readouterr()
        assert category.get_total_products() == 1
        assert "успешно добавлен" in captured.out
        assert "Обработка добавления товара завершена." in captured.out

    # ========== ИЗМЕНЕНО: TypeError теперь печатается, а не выбрасывается ==========
    def test_add_product_invalid_type_string(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При добавлении строки печатается ошибка, товар не добавляется."""
        category = Category("Электроника", "Гаджеты")
        category.add_product("Не продукт")  # type: ignore[arg-type]
        captured = capsys.readouterr()
        assert "Ошибка:" in captured.out
        assert "Можно добавлять только объекты класса Product" in captured.out
        assert "Обработка добавления товара завершена." in captured.out
        assert category.get_total_products() == 0

    def test_add_product_invalid_type_int(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При добавлении числа печатается ошибка, товар не добавляется."""
        category = Category("Электроника", "Гаджеты")
        category.add_product(123)  # type: ignore[arg-type]
        captured = capsys.readouterr()
        assert "Ошибка:" in captured.out
        assert category.get_total_products() == 0

    def test_add_product_invalid_type_none(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При добавлении None печатается ошибка, товар не добавляется."""
        category = Category("Электроника", "Гаджеты")
        category.add_product(None)  # type: ignore[arg-type]
        captured = capsys.readouterr()
        assert "Ошибка:" in captured.out
        assert category.get_total_products() == 0

    # ========== ДОП. ЗАДАНИЕ (*): ZeroQuantityError в add_product ==========
    def test_add_product_zero_quantity(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При добавлении товара с нулевым количеством печатается ошибка."""
        category = Category("Электроника", "Гаджеты")
        product = Product("Т1", "О", 10.0, 5)
        product.quantity = 0  # Имитируем нулевое количество после создания
        category.add_product(product)
        captured = capsys.readouterr()
        assert "Ошибка:" in captured.out
        assert "нулевое количество" in captured.out
        assert "Обработка добавления товара завершена." in captured.out
        assert category.get_total_products() == 0

    def test_add_product_zero_quantity_not_added(self) -> None:
        """Товар с нулевым количеством фактически не попадает в категорию."""
        category = Category("Электроника", "Гаджеты")
        product = Product("Т1", "О", 10.0, 5)
        product.quantity = 0
        category.add_product(product)
        assert category.get_total_products() == 0

    # ========== ЗАДАНИЕ 2: average_price ==========
    def test_average_price_with_products(self) -> None:
        """Средний ценник считается корректно."""
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[
                Product("Т1", "О", 100.0, 5),
                Product("Т2", "О", 200.0, 3),
                Product("Т3", "О", 300.0, 2),
            ],
        )
        assert category.average_price() == 200.0

    def test_average_price_empty_category(self) -> None:
        """Для пустой категории возвращается 0."""
        category = Category("Пустая", "Без товаров")
        assert category.average_price() == 0.0

    def test_average_price_single_product(self) -> None:
        """Для одного товара средний ценник равен его цене."""
        category = Category("Один", "Товар", products=[Product("Т1", "О", 150.0, 1)])
        assert category.average_price() == 150.0

    def test_str_empty(self) -> None:
        category = Category("Электроника", "Гаджеты")
        assert str(category) == "Электроника, количество продуктов: 0 шт."

    def test_str_with_products(self) -> None:
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[
                Product("Т1", "О", 10.0, 5),
                Product("Т2", "О", 20.0, 3),
            ],
        )
        assert str(category) == "Электроника, количество продуктов: 8 шт."

    def test_products_property_with_items(self) -> None:
        category = Category("Фрукты", "Еда")
        p1 = Product("Яблоко", "Красное", 50, 15)
        p2 = Product("Банан", "Желтый", 80, 20)
        category.add_product(p1)
        category.add_product(p2)
        result = category.products
        assert "Яблоко" in result
        assert "Банан" in result

    def test_to_dict(self) -> None:
        category = Category(
            "Электроника",
            "Гаджеты",
            products=[Product("Т1", "О", 10.0, 1)],
        )
        result = category.to_dict()
        assert result["name"] == "Электроника"
        assert len(result["products"]) == 1

    def test_from_dict(self) -> None:
        data: dict[str, Any] = {
            "name": "Электроника",
            "description": "Гаджеты",
            "products": [
                {"name": "Т1", "description": "О", "price": 10.0, "quantity": 1},
                {"name": "Т2", "description": "О", "price": 20.0, "quantity": 2},
            ],
        }
        category = Category.from_dict(data)
        assert category.get_total_products() == 2

    def test_category_inherits_base_entity(self) -> None:
        category = Category("Электроника", "Гаджеты")
        assert isinstance(category, BaseEntity)


# ==================== ТЕСТЫ ДЛЯ Order ====================


class TestOrder:
    def test_init(self) -> None:
        product = Product("Смартфон", "Описание", 79990.0, 15)
        order = Order("Заказ1", "Первый заказ", product, 3)
        assert order.name == "Заказ1"
        assert order.product is product
        assert order.quantity == 3
        assert order.total_cost == 79990.0 * 3

    def test_str(self) -> None:
        product = Product("Смартфон", "Описание", 100.0, 10)
        order = Order("Заказ1", "Описание заказа", product, 2)
        result = str(order)
        assert "Заказ 'Заказ1'" in result
        assert "количество: 2 шт." in result
        assert "итоговая стоимость: 200.0 руб." in result

    # ========== ДОП. ЗАДАНИЕ (*): Order с нулевым количеством ==========
    def test_order_zero_quantity(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Заказ с нулевым количеством печатает ошибку, quantity становится 0."""
        product = Product("Смартфон", "Описание", 100.0, 10)
        order = Order("Заказ1", "Описание", product, 0)
        captured = capsys.readouterr()
        assert "Ошибка" in captured.out
        assert "нулевое количество" in captured.out
        assert "Обработка создания заказа завершена." in captured.out
        assert order.quantity == 0
        assert order.total_cost == 0.0

    def test_order_success_creation_message(self, capsys: pytest.CaptureFixture[str]) -> None:
        """При успешном создании заказа печатается сообщение."""
        product = Product("Смартфон", "Описание", 100.0, 10)
        Order("Заказ1", "Описание", product, 2)
        captured = capsys.readouterr()
        assert "успешно создан" in captured.out
        assert "Обработка создания заказа завершена." in captured.out

    def test_total_cost_with_smartphone(self) -> None:
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        order = Order("Заказ", "Покупка телефона", phone, 2)
        assert order.total_cost == 99990.0 * 2

    def test_order_inherits_base_entity(self) -> None:
        product = Product("Тест", "Описание", 10.0, 1)
        order = Order("Заказ", "Описание", product, 1)
        assert isinstance(order, BaseEntity)


# ==================== ТЕСТЫ ДЛЯ ZeroQuantityError ====================


class TestZeroQuantityError:
    def test_is_exception_subclass(self) -> None:
        """ZeroQuantityError наследует Exception."""
        assert issubclass(ZeroQuantityError, Exception)

    def test_message_contains_product_name(self) -> None:
        """Сообщение исключения содержит имя товара."""
        error = ZeroQuantityError("Молоко")
        assert "Молоко" in str(error)

    def test_can_be_raised_and_caught(self) -> None:
        """Исключение можно выбросить и поймать."""
        with pytest.raises(ZeroQuantityError):
            raise ZeroQuantityError("Тестовый товар")


# ==================== ТЕСТЫ ДЛЯ Read_Json_file ====================


class TestReadJsonFile:
    def test_init(self) -> None:
        manager = Read_Json_file()
        assert manager.categories == []

    def test_add_category(self) -> None:
        manager = Read_Json_file()
        manager.add_category(Category("К1", "О1"))
        assert len(manager.categories) == 1

    def test_get_total_products(self) -> None:
        manager = Read_Json_file()
        p1 = Product("P1", "d", 10.0, 5)
        p2 = Product("P2", "d", 20.0, 3)
        c = Category("A", "d", [p1, p2])
        manager.add_category(c)
        assert manager.get_total_products() == 2

    def test_str(self) -> None:
        manager = Read_Json_file()
        result = str(manager)
        assert "0 категорий" in result
        assert "0 товаров" in result

    def test_load_from_json_file_not_found(self, tmp_path: Path) -> None:
        manager = Read_Json_file.load_from_json(str(tmp_path / "no.json"))
        assert manager.categories == []

    def test_load_from_json_valid(self, tmp_path: Path) -> None:
        data: dict[str, Any] = {
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

    def test_load_from_json_invalid_json(self, tmp_path: Path) -> None:
        json_file = tmp_path / "test.json"
        json_file.write_text("{bad json}", encoding="utf-8")
        manager = Read_Json_file.load_from_json(str(json_file))
        assert manager.categories == []


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================


class TestIntegration:
    def test_product_count_tracking(self) -> None:
        """Отслеживание счётчика Product через BaseProduct."""
        Product("Т1", "О", 10.0, 1)
        Product("Т2", "О", 20.0, 2)
        assert BaseProduct.product_count == 2  # type: ignore[attr-defined]

    def test_category_count_tracking(self) -> None:
        Category("К1", "О1")
        Category("К2", "О2")
        assert Category.category_count == 2  # type: ignore[attr-defined]

    def test_mixed_products_in_category(self) -> None:
        product = Product("Товар", "Описание", 100.0, 10)
        phone = Smartphone("iPhone", "Флагман", 99990.0, 5, 95.5, "15 Pro", 256, "Black")
        grass = LawnGrass("Green Lawn", "Газон", 500.0, 10, "Germany", 14, "Green")
        category = Category("Магазин", "Все товары", products=[product, phone, grass])
        assert category.get_total_products() == 3

    def test_average_price_mixed_products(self) -> None:
        """Средний ценник работает со смешанными типами товаров."""
        product = Product("Товар", "Описание", 100.0, 10)
        phone = Smartphone("iPhone", "Флагман", 200.0, 5, 95.5, "15 Pro", 256, "Black")
        grass = LawnGrass("Green Lawn", "Газон", 300.0, 10, "Germany", 14, "Green")
        category = Category("Магазин", "Все товары", products=[product, phone, grass])
        assert category.average_price() == 200.0

    def test_order_with_category_workflow(self) -> None:
        product = Product("Товар", "Описание", 100.0, 10)
        category = Category("Каталог", "Все товары", products=[product])
        order = Order("Заказ", "Покупка товара", product, 3)
        assert isinstance(category, BaseEntity)
        assert isinstance(order, BaseEntity)
        assert order.total_cost == 300.0
