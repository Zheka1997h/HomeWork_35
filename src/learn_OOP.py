import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class Product:
    """Класс, представляющий товар."""

    # === Атрибуты класса ===
    product_count: int = 0  # Общее количество созданных товаров

    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name = name
        self.description = description
        self.quantity = quantity

        # Инициализируем приватный атрибут цены перед вызовом сеттера
        self.__price: float = 0.0
        # Используем сеттер для установки цены (чтобы сработала валидация)
        self.price = price

        Product.product_count += 1

    def __str__(self) -> str:
        return (
            f"Продукт: {self.name}\n"
            f"Описание: {self.description}\n"
            f"Цена: {self.__price}\n"
            f"Количество: {self.quantity}"
        )

    # === Геттер и Сеттер для цены ===
    @property
    def price(self) -> float:
        """Геттер для приватного атрибута цены."""
        return self.__price

    @price.setter
    def price(self, new_price: float) -> None:
        """Сеттер для приватного атрибута цены."""
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return

        # * Дополнительное задание: подтверждение при понижении цены
        if self.__price > 0 and new_price < self.__price:
            confirm = input(f"Цена понижается с {self.__price} до {new_price}. Подтвердите (y/n): ")
            if confirm.lower() != "y":
                print("Изменение цены отменено.")
                return

        self.__price = new_price

    # === Класс-метод ===
    @classmethod
    def new_product(
        cls, product_dict: Dict[str, Any], existing_products: Optional[List["Product"]] = None
    ) -> "Product":
        """
        Создает объект Product из словаря.
        Если передан список существующих товаров, проверяет на дубликаты.
        """
        if existing_products:
            for product in existing_products:
                if product.name == product_dict["name"]:
                    # Товар уже существует: складываем количество
                    product.quantity += product_dict["quantity"]
                    # При конфликте цен выбираем более высокую
                    if product_dict["price"] > product.price:
                        product.price = product_dict["price"]
                    return product

        # Если дубликата нет, создаем новый объект
        return cls(
            name=product_dict["name"],
            description=product_dict["description"],
            price=product_dict["price"],
            quantity=product_dict["quantity"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "price": self.__price,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """Создание объекта Product из словаря (для обратной совместимости)."""
        return cls.new_product(data)


class Category:
    """Класс, представляющий категорию товаров."""

    # === Атрибуты класса ===
    category_count: int = 0  # Общее количество созданных категорий
    product_count: int = 0  # Общее количество товаров во ВСЕХ категориях

    def __init__(self, name: str, description: str, products: Optional[List[Product]] = None):
        self.name = name
        self.description = description

        # Приватный атрибут списка товаров
        self.__products: List[Product] = []

        # Добавляем товары через метод add_product, чтобы корректно работал счетчик
        if products:
            for product in products:
                self.add_product(product)

        Category.category_count += 1

    def add_product(self, product: Product) -> None:
        """Добавляет продукт в приватный список и увеличивает счетчик."""
        self.__products.append(product)
        Category.product_count += 1

    @property
    def products(self) -> str:
        """Геттер, возвращающий строку со всеми продуктами в заданном формате."""
        result_str = ""
        for p in self.__products:
            result_str += f"{p.name}, {p.price} руб. Остаток: {p.quantity} шт.\n"
        return result_str

    def get_total_products(self) -> int:
        """Возвращает количество товаров в данной категории."""
        return len(self.__products)

    def __str__(self) -> str:
        return f"Категория: {self.name} | Товаров: {self.get_total_products()}"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для JSON."""
        return {
            "name": self.name,
            "description": self.description,
            "products": [p.to_dict() for p in self.__products],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
        """Создание объекта Category из словаря."""
        products = [Product.from_dict(p) for p in data.get("products", [])]
        return cls(
            name=data["name"],
            description=data["description"],
            products=products,
        )


class Read_Json_file:
    """Класс для чтения JSON файла и управления данными."""

    def __init__(self) -> None:
        self.categories: List[Category] = []

    def add_category(self, category: Category) -> None:
        self.categories.append(category)

    def get_all_categories(self) -> List[Category]:
        return self.categories

    def get_total_products(self) -> int:
        return sum(cat.get_total_products() for cat in self.categories)

    @classmethod
    def load_from_json(cls, file_path: str) -> "Read_Json_file":
        path = Path(file_path)
        if not path.exists():
            print(f"❌ Файл не найден: {file_path}")
            return cls()

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            manager = cls()
            categories_data = data.get("categories", []) if isinstance(data, dict) else data

            for category_data in categories_data:
                category = Category.from_dict(category_data)
                manager.add_category(category)

            print(f"✅ Загружено {len(manager.categories)} категорий")
            return manager

        except Exception as e:
            print(f"❌ Ошибка при загрузке JSON: {e}")
            return cls()

    def __str__(self) -> str:
        return f"Менеджер: {len(self.categories)} категорий, {self.get_total_products()} товаров"


if __name__ == "__main__":
    # Сбрасываем счётчики перед запуском
    Product.product_count = 0
    Category.category_count = 0
    Category.product_count = 0

    # Загрузка данных (путь к вашему файлу)
    manager = Read_Json_file.load_from_json(r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\products.json")

    print(manager)
    print()

    for category in manager.get_all_categories():
        print(category)
        # Используем геттер products для вывода списка
        print(category.products)

    print(f"Всего создано категорий: {Category.category_count}")
    print(f"Всего создано товаров: {Product.product_count}")
    print(f"Всего товаров во всех категориях: {Category.product_count}")
