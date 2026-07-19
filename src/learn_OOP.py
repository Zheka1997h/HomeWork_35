import json
from pathlib import Path
from typing import List, Dict, Any


class Product:

    name:str #Имя продукта (поле)
    description:str #Описание продукта (поле)
    price: float#Цена продукта (поле)
    quantity: int # Количество продукта (поле)

    """Свойства(атрибуты) класса Product"""
    def __init__(self, name: str, description: str, price: float, quantity:int):
        self.name = name
        self.description = description
        self.price = price
        self. quantity = quantity

    """Вывод заданных свойств класса Product"""
    def __str__(self):
        return f"Продукт: {self.name} \nОписание: {self.description}\nЦена: {self.price}\nКоличество: {self.quantity}"
    pass

    def to_dict(self)-> Dict[str, Any]:
        """Преобразование в словарь для JSON"""
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any])-> 'Product':
        """Создание объекта Product из словаря."""
        return cls(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            quantity=data["quantity"]
        )




class Category:

    name: str  # Имя продукта (поле)
    description: str  # Описание продукта (поле)
    products: str

    def __init__(self, name: str, description:str):
        self.name = name
        self.description = description
        self.products: list[Product] = []

    def add_product(self, product: Product):
        """Добавляем категорию"""
        self.products.append(product)

    def get_total_products(self)-> int:
        """Возвращает количество товаров"""
        return len(self.products)


    def __str__(self):
        return f"Категория:{self.name} | Товаров: {self.get_total_products()}"

    def to_dict(self)-> Dict[str, Any]:
        """Преобразование в словарь для JSON"""
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
        # Создаем товары из JSON

        for product_data in data.get("products", []):
            product = Product.from_dict(product_data)
            category.add_product(product)
        return  category




    pass


class Read_Json_file:
    """Класс для чтения JSON файла."""

    # ⚠️ ВАЖНО: добавьте этот метод!
    def __init__(self):
        self.categories: list[Category] = []  # ← вот это создаёт атрибут

    def add_category(self, category: Category):
        """Добавить категорию."""
        self.categories.append(category)

    def get_all_categories(self) -> list[Category]:
        """Получить все категории."""
        return self.categories

    def get_total_products(self) -> int:
        """Общее количество товаров."""
        return sum(cat.get_total_products() for cat in self.categories)

    @classmethod
    def load_from_json(cls, file_path: str) -> 'Read_Json_file':
        """Читает JSON файл."""
        path = Path(file_path)

        if not path.exists():
            print(f"❌ Файл не найден: {file_path}")
            return cls()  # ✅ Теперь работает, т.к. __init__ есть

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            manager = cls()
            if isinstance(data, dict):
                # Если это словарь — ищем ключ "categories"
                categories_data = data.get("categories", [])
            elif isinstance(data, list):
                # Если это список — используем его напрямую
                categories_data = data
            else:
                print(f"❌ Неизвестный формат JSON: {type(data)}")
                return cls()

            for categories_data in categories_data:
                category = Category.from_dict(categories_data)
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



manager = Read_Json_file.load_from_json(r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\products.json")

print(manager)
print()


for category in manager.get_all_categories():
    print(category)
    for product in category.products:
        print(f" - {product.name}: {product.price} р (в наличии: {product.quantity}")
    print()
