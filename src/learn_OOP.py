import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class Product:
    """Класс, представляющий товар."""

    product_count: int = 0

    def __init__(self, name: str, description: str, price: float, quantity: int):
        self.name = name
        self.description = description
        self.quantity = quantity

        self.__price: float = 0.0
        self.price = price

        Product.product_count += 1

    # === ИСПРАВЛЕННЫЙ __str__ ===
    def __str__(self) -> str:
        return f"{self.name}, {self.__price} руб. Остаток: {self.quantity} шт."

    # === ИСПРАВЛЕННЫЙ __add__ ===
    def __add__(self, other: "Product") -> float:
        """Возвращает общую стоимость товаров на складе."""
        if type(self) != type(other):
            raise TypeError(
                f"Нельзя складывать товары разных типов"
                f"{type(self).__name__}"
            )
        return (self.price * self.quantity + (other.price * other.quantity))

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, new_price: float) -> None:
        if new_price <= 0:
            print("Цена не должна быть нулевая или отрицательная")
            return

        if self.__price > 0 and new_price < self.__price:
            confirm = input(f"Цена понижается с {self.__price} до {new_price}. Подтвердите (y/n): ")
            if confirm.lower() != "y":
                print("Изменение цены отменено.")
                return

        self.__price = new_price

    @classmethod
    def new_product(
        cls, product_dict: Dict[str, Any], existing_products: Optional[List["Product"]] = None
    ) -> "Product":
        if existing_products:
            for product in existing_products:
                if product.name == product_dict["name"]:
                    product.quantity += product_dict["quantity"]
                    if product_dict["price"] > product.price:
                        product.price = product_dict["price"]
                    return product

        return cls(
            name=product_dict["name"],
            description=product_dict["description"],
            price=product_dict["price"],
            quantity=product_dict["quantity"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "price": self.__price,
            "quantity": self.quantity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        product_type = data.get("type","Product")

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
        elif product_type == "LawnGrass":
            return LawnGrass(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                quantity=data["quantity"],
                country=data["country"],
                germination_period=data["germination_period"],
                color=data["color"]
            )
        else:
            return cls.new_product(data)


class Category:
    """Класс, представляющий категорию товаров."""

    category_count: int = 0
    product_count: int = 0

    def __init__(self, name: str, description: str, products: Optional[List[Product]] = None):
        self.name = name
        self.description = description
        self.__products: List[Product] = []

        if products:
            for product in products:
                self.add_product(product)

        Category.category_count += 1

    # === ИСПРАВЛЕННЫЙ __str__ ===
    def __str__(self) -> str:
        total_quantity = sum(product.quantity for product in self.__products)
        return f"{self.name}, количество продуктов: {total_quantity} шт."

    def add_product(self, product: Product) -> None:
        if not isinstance(product, Product):
            raise TypeError(
                f"В категорию можно добавлять только объекты Product или его наследников,"
                f"а не {type(product).__name__}"
            )
        self.__products.append(product)
        Category.product_count += 1

    # === ОПТИМИЗИРОВАННЫЙ ГЕТТЕР ===
    @property
    def products(self) -> str:
        return "\n".join(str(p) for p in self.__products)

    def get_total_products(self) -> int:
        return len(self.__products)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "products": [p.to_dict() for p in self.__products],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Category":
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


class Smartphone(Product):

    def __init__(self,
                 name: str,
                 description: str,
                 price:float,
                 quantity:int,
                 efficiency: float,
                 model: str,
                 memory: int,
                 color: str,):
     super().__init__(name, description, price,quantity)
     self.efficiency = efficiency
     self.model = model
     self.memory = memory
     self.color = color


    def __str__(self) -> str:
        return (
            f"{self.name}({self.model},{self.color},"
            f"{self.memory}GB), {self.price} руб. Остаток: {self.quantity} шт."
        )

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "type":"Smartphone",
            "efficiency":self.efficiency,
            "model":self.model,
            "memory":self.memory,
            "color": self.color
        })
        return data




class LawnGrass(Product):
    def __init__(self,
                 name:str,
                 description:str,
                 price:float,
                 quantity:int,
                 country:str,
                 germination_period:int,
                 color:str,):
     super().__init__(name,description,price,quantity)
     self.country = country
     self.germination_period = germination_period
     self.color = color


    def __str__(self)->str:
        return (
            f"{self.name} ({self.color}, страна: {self.country}),"
            f"{self.price} руб. Остаток: {self.quantity} шт."
        )

    def to_dict(self) -> Dict[str,Any]:
        data = super().to_dict()
        data.update(
            {
                "type":"LawnGrass",
                "country":self.country,
                "germination_period":self.germination_period,
                "color":self.color,
            }
        )
        return data



if __name__ == "__main__":
    Product.product_count = 0
    Category.category_count = 0
    Category.product_count = 0

    manager = Read_Json_file.load_from_json(r"C:\Users\Zheka1998\Desktop\TaskОne_2\data\products.json")

    print(manager)
    print()

    for category in manager.get_all_categories():
        print(category)
        print(category.products)
        print()

    print(f"\nВсего создано категорий: {Category.category_count}")
    print(f"Всего создано товаров: {Product.product_count}")
    print(f"Всего товаров во всех категориях: {Category.product_count}")

    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ НОВОЙ ФУНКЦИОНАЛЬНОСТИ")
    print("=" * 50)

    # Создаём траву
    grass1 = LawnGrass(
        name="Green Lawn",
        description="Газонная трава премиум",
        price=500.0,
        quantity=10,
        country="Germany",
        germination_period=14,
        color="Green",
    )

    grass2 = LawnGrass(
        name="Sport Grass",
        description="Трава для спортивных газонов",
        price=700.0,
        quantity=8,
        country="Netherlands",
        germination_period=10,
        color="Dark Green",
    )

    phone1 = Smartphone(
        name="IPhone 15 Pro",
        description="Флагман Apple",
        price=99990.0,
        quantity=5,
        efficiency=95.5,
        model="IPhone 15 Pro",
        memory=256,
        color="Black",
    )

    phone2 = Smartphone(
        name="Samsung Galaxy S24",
        description="Флагман Samsung",
        price=89990.0,
        quantity=3,
        efficiency=92.0,
        model="Galaxy S24 Ultra",
        memory=512,
        color="Titanium",
    )

    print("\n✅ Созданные товары:")
    print(phone1)
    print(phone2)
    print(grass1)
    print(grass2)

    print("\n✅ Сложение двух смартфонов:")
    total_phones = phone1 + phone2
    print(f"Общая стоимость: {total_phones} руб.")

    print("\n✅ Сложение двух трав:")
    total_grass = grass1 + grass2
    print(f"Общая стоимость: {total_grass} руб.")

    # Проверяем защиту от сложения разных классов
    print("\n❌ Попытка сложить смартфон и траву:")
    try:
        phone1 + grass1
    except TypeError as e:
        print(f"Ошибка: {e}")

    # ✅ ТЕПЕРЬ ЭТО НА ТОМ ЖЕ УРОВНЕ, ЧТО И try/except ВЫШЕ
    print("\n✅ Добавление товаров в категорию:")
    tech_category = Category("Электроника", "Смартфоны и гаджеты")
    tech_category.add_product(phone1)
    tech_category.add_product(phone2)
    print(tech_category)
    print(tech_category.products)

    garden_category = Category("Сад", "Товары для сада")
    garden_category.add_product(grass1)
    garden_category.add_product(grass2)
    print(garden_category)
    print(garden_category.products)

    # Проверяем защиту от добавления посторонних объектов
    print("\n❌ Попытка добавить строку в категорию:")
    try:
        tech_category.add_product("Не продукт")
    except TypeError as e:
        print(f"Ошибка: {e}")

    print("\n❌ Попытка добавить число в категорию:")
    try:
        tech_category.add_product(123)
    except TypeError as e:
        print(f"Ошибка: {e}")

    print("\n✅ Все проверки пройдены!")