from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class CreationMixin:
    """Миксин для вывода информации о создании объекта."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        params = ", ".join(repr(arg) for arg in args)
        print(f"{self.__class__.__name__}({params})")


class BaseEntity(ABC):
    """Абстрактный базовый класс для всех сущностей."""

    @abstractmethod
    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def __str__(self) -> str: ...

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description}


class BaseProduct(BaseEntity):
    """Абстрактный базовый класс для продуктов."""

    product_count: int = 0

    @abstractmethod
    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        super().__init__(name, description)
        self._price = price
        self.quantity = quantity
        BaseProduct.product_count += 1

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return
        if value < self._price:
            confirm = input("Вы уверены, что хотите понизить цену? (y/n): ")
            if confirm.lower() != "y":
                print("Изменение цены отменено.")
                return
        self._price = value

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def __add__(self, other: BaseProduct) -> float: ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...


class Product(CreationMixin, BaseProduct):
    """Класс продукта."""

    @classmethod
    def new_product(
        cls,
        data: Dict[str, Any],
        existing_products: Optional[List[Product]] = None,
    ) -> Product:
        """Создаёт новый продукт или обновляет существующий."""
        if existing_products is None:
            existing_products = []

        for product in existing_products:
            if product.name == data["name"]:
                product.quantity += data["quantity"]
                if data["price"] > product.price:
                    product.price = data["price"]
                return product

        return cls(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            quantity=data["quantity"],
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Product:
        """Создаёт продукт из словаря, поддерживая наследников."""
        product_type = data.get("type")
        if product_type == "Smartphone":
            return Smartphone(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                quantity=data["quantity"],
                efficiency=data["efficiency"],
                model=data["model"],
                memory=data["memory"],
                color=data["color"],
            )
        if product_type == "LawnGrass":
            return LawnGrass(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                quantity=data["quantity"],
                country=data["country"],
                germination_period=data["germination_period"],
                color=data["color"],
            )
        return cls(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            quantity=data["quantity"],
        )

    def __init__(self, name: str, description: str, price: float, quantity: int) -> None:
        if price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            price = 0.0
        super().__init__(name, description, price, quantity)

    def __str__(self) -> str:
        return f"{self.name}, {self.price} руб. Остаток: {self.quantity} шт."

    def __add__(self, other: BaseProduct) -> float:
        """Возвращает общую стоимость товаров на складе."""
        if type(self) is not type(other):
            raise TypeError(f"Нельзя складывать товары разных типов: {type(self).__name__}")
        return self.price * self.quantity + other.price * other.quantity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity,
        }


class Smartphone(Product):
    """Класс смартфона."""

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        efficiency: float,
        model: str,
        memory: int,
        color: str,
    ) -> None:
        super().__init__(name, description, price, quantity)
        self.efficiency = efficiency
        self.model = model
        self.memory = memory
        self.color = color

    def __str__(self) -> str:
        return (
            f"{self.name}, {self.model}, {self.memory}GB, {self.color}, "
            f"{self.price} руб. Остаток: {self.quantity} шт."
        )

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "type": "Smartphone",
                "efficiency": self.efficiency,
                "model": self.model,
                "memory": self.memory,
                "color": self.color,
            }
        )
        return base


class LawnGrass(Product):
    """Класс газонной травы."""

    def __init__(
        self,
        name: str,
        description: str,
        price: float,
        quantity: int,
        country: str,
        germination_period: int,
        color: str,
    ) -> None:
        super().__init__(name, description, price, quantity)
        self.country = country
        self.germination_period = germination_period
        self.color = color

    def __str__(self) -> str:
        return f"{self.name}, {self.country}, {self.color}, " f"{self.price} руб. Остаток: {self.quantity} шт."

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "type": "LawnGrass",
                "country": self.country,
                "germination_period": self.germination_period,
                "color": self.color,
            }
        )
        return base


class Category(BaseEntity):
    """Класс категории товаров."""

    category_count: int = 0
    product_count: int = 0

    def __init__(
        self,
        name: str,
        description: str,
        products: Optional[List[Product]] = None,
    ) -> None:
        super().__init__(name, description)
        self._products: List[Product] = list(products) if products else []
        Category.category_count += 1
        Category.product_count += len(self._products)

    def add_product(self, product: Product) -> None:
        """Добавляет продукт в категорию."""
        if not isinstance(product, Product):
            raise TypeError("Можно добавлять только объекты класса Product")
        self._products.append(product)
        Category.product_count += 1

    def get_total_products(self) -> int:
        return len(self._products)

    @property
    def products(self) -> str:
        if not self._products:
            return ""
        return "\n".join(str(p) for p in self._products)

    def __str__(self) -> str:
        total_qty = sum(p.quantity for p in self._products)
        return f"{self.name}, количество продуктов: {total_qty} шт."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "products": [p.to_dict() for p in self._products],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Category:
        products_data = data.get("products", [])
        products = [Product.from_dict(p) for p in products_data]
        return cls(
            name=data["name"],
            description=data["description"],
            products=products,
        )

    # --- Методы ниже используются только для тестирования валидации ---
    # Они намеренно принимают некорректные типы, поэтому mypy подавляется

    def _test_add_invalid_string(self) -> None:
        self.add_product("Не продукт")  # type: ignore[arg-type]

    def _test_add_invalid_int(self) -> None:
        self.add_product(123)  # type: ignore[arg-type]

    def _test_add_invalid_none(self) -> None:
        self.add_product(None)  # type: ignore[arg-type]


class Order(BaseEntity):
    """Класс заказа."""

    def __init__(self, name: str, description: str, product: Product, quantity: int) -> None:
        super().__init__(name, description)
        self.product = product
        self.quantity = quantity

    @property
    def total_cost(self) -> float:
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return (
            f"Заказ '{self.name}', товар: {self.product.name}, "
            f"количество: {self.quantity} шт., "
            f"итоговая стоимость: {self.total_cost} руб."
        )


class Read_Json_file:
    """Менеджер для загрузки категорий из JSON."""

    def __init__(self) -> None:
        self.categories: List[Category] = []

    def add_category(self, category: Category) -> None:
        self.categories.append(category)

    def get_all_categories(self) -> List[Category]:
        return self.categories

    def get_total_products(self) -> int:
        return sum(c.get_total_products() for c in self.categories)

    def __str__(self) -> str:
        total_products = self.get_total_products()
        return f"{len(self.categories)} категорий, {total_products} товаров"

    @classmethod
    def load_from_json(cls, filepath: str) -> Read_Json_file:
        manager = cls()
        path = Path(filepath)
        if not path.exists():
            return manager
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError, ValueError:
            return manager

        if isinstance(raw, list):
            categories_data = raw
        elif isinstance(raw, dict):
            categories_data = raw.get("categories", [])
        else:
            return manager

        for cat_data in categories_data:
            category = Category.from_dict(cat_data)
            manager.add_category(category)

        return manager
