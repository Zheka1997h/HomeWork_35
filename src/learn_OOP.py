import json
from pathlib import Path
from typing import Dict, Any, List


class Product:
    """Класс, представляющий товар."""

    # === Атрибуты класса ===
    product_count: int = 0  # Общее количество созданных товаров

    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

        # Автоматически увеличиваем счётчик при создании объекта
        Product.product_count += 1

    def __str__(self):
        return (f"Продукт: {self.name}\n"
                f"Описание: {self.description}\n"
                f"Цена: {self.price}\n"
                f"Количество: {self.quantity}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """Создание объекта Product из словаря."""
        return cls(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            quantity=data["quantity"]
        )


class Category:
    """Класс, представляющий категорию товаров."""

    # === Атрибуты класса ===
    category_count: int = 0  # Общее количество созданных категорий

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.products: List[Product] = []

        # Автоматически увеличиваем счётчик при создании объекта
        Category.category_count += 1

    def add_product(self, product: Product):
        """Добавить товар в категорию."""
        self.products.append(product)

    def get_total_products(self) -> int:
        """Возвращает количество товаров в данной категории."""
        return len(self.products)

    def __str__(self):
        return f"Категория: {self.name} | Товаров: {self.get_total_products()}"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "products": [p.to_dict() for p in self.products]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Category':
        """Создание объекта Category из словаря."""
        category = cls(
            name=data["name"],
            description=data["description"]
        )
        for product_data in data.get("products", []):
            product = Product.from_dict(product_data)
            category.add_product(product)
        return category


class Read_Json_file:
    """Класс для чтения JSON файла и управления данными."""

    def __init__(self):
        self.categories: List[Category] = []

    def add_category(self, category: Category):
        """Добавить категорию."""
        self.categories.append(category)

    def get_all_categories(self) -> List[Category]:
        """Получить все категории."""
        return self.categories

    def get_total_products(self) -> int:
        """Общее количество товаров во всех категориях."""
        return sum(cat.get_total_products() for cat in self.categories)

    @classmethod
    def load_from_json(cls, file_path: str) -> 'Read_Json_file':
        """Читает JSON файл и создаёт объект Read_Json_file."""
        path = Path(file_path)

        if not path.exists():
            print(f"❌ Файл не найден: {file_path}")
            return cls()

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            manager = cls()

            if isinstance(data, dict):
                categories_data = data.get("categories", [])
            elif isinstance(data, list):
                categories_data = data
            else:
                print(f"❌ Неизвестный формат JSON: {type(data)}")
                return cls()

            for category_data in categories_data:
                category = Category.from_dict(category_data)
                manager.add_category(category)

            print(f"✅ Загружено {len(manager.categories)} категорий")
            return manager

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка формата JSON: {e}")
            return cls()

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return cls()

    def __str__(self):
        return f"Менеджер: {len(self.categories)} категорий, {self.get_total_products()} товаров"


if __name__ == "__main__":
    # Сбрасываем счётчики перед запуском
    Product.product_count = 0
    Category.category_count = 0

    manager = Read_Json_file.load_from_json(
        r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\products.json"
    )

    print(manager)
    print()

    for category in manager.get_all_categories():
        print(category)
        for product in category.products:
            print(f"  - {product.name}: {product.price} р (в наличии: {product.quantity})")
        print()

    # Вывод атрибутов класса
    print(f"Всего создано категорий: {Category.category_count}")
    print(f"Всего создано товаров: {Product.product_count}")