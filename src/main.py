from typing import List, Union, Type
from src.api_handlers import AeroplanesAPI
from src.models import Aeroplane
from src.storage import JSONSaver


def print_menu() -> None:
    """Вывод меню в консоль"""
    print("\n--- Меню управления полетами ---")
    print("1. Загрузить данные о самолетах для страны")
    print("2. Показать топ N самолетов по высоте")
    print("3. Найти самолеты по стране регистрации")
    print("4. Сохранить текущий список в файл")
    print("5. Загрузить список из файла")
    print("0. Выход")


def get_user_input(prompt: str, input_type: Type[Union[str, int, float]] = str) -> Union[str, int, float]:
    """Получение ввода от пользователя с обработкой ошибок"""
    while True:
        try:
            value = input(prompt)
            if input_type == int:
                return int(value)
            elif input_type == float:
                return float(value)
            else:
                return value
        except ValueError:
            print(f"Ошибка ввода. Пожалуйста, введите значение типа {input_type.__name__}.")


def main() -> None:
    """Основная функция взаимодействия с пользователем"""
    api = AeroplanesAPI()
    saver = JSONSaver()
    current_aeroplanes: List[Aeroplane] = []

    while True:
        print_menu()
        choice = get_user_input("Выберите действие: ", str)

        if choice == '1':
            country = input("Введите название страны (на английском, например Spain): ")
            print("Загрузка данных... Это может занять время.")
            raw_data = api.get_aeroplanes(country)
            if raw_data:
                current_aeroplanes = Aeroplane.cast_to_object_list(raw_data)
                print(f"Загружено {len(current_aeroplanes)} самолетов.")
            else:
                print("Не удалось получить данные или страна не найдена.")

        elif choice == '2':
            if not current_aeroplanes:
                print("Сначала загрузите данные (пункт 1) или загрузите из файла (пункт 5).")
                continue

            n = get_user_input("Введите количество самолетов для топа (N): ", int)
            # Сортировка по высоте (по убыванию)
            sorted_planes = sorted(current_aeroplanes, key=lambda x: x.altitude, reverse=True)
            top_planes = sorted_planes[:n]

            print(f"\n--- Топ {n} самолетов по высоте ---")
            for i, plane in enumerate(top_planes, 1):
                callsign = plane.callsign or 'No Call'
                print(
                    f"{i}. {callsign} | Alt: {plane.altitude:.2f}m | "
                    f"Country: {plane.origin_country}"
                )

        elif choice == '3':
            if not current_aeroplanes:
                print("Нет данных для фильтрации.")
                continue

            filter_country = input("Введите страну регистрации для поиска: ")
            filtered = [p for p in current_aeroplanes if filter_country.lower() in p.origin_country.lower()]

            print(f"\n--- Самолеты, зарегистрированные в {filter_country} ---")
            if not filtered:
                print("Ничего не найдено.")
            else:
                for plane in filtered:
                    callsign = plane.callsign or 'No Call'
                    print(
                        f"- {callsign} | Alt: {plane.altitude:.2f}m | "
                        f"Speed: {plane.speed:.2f} m/s"
                    )

        elif choice == '4':
            if not current_aeroplanes:
                print("Нечего сохранять.")
                continue
            count = 0
            for plane in current_aeroplanes:
                try:
                    saver.add_aeroplane(plane)
                    count += 1
                except Exception as e:
                    print(f"Ошибка сохранения самолета {plane.icao24}: {e}")
            print(f"Сохранено {count} записей в {saver.filename}")

        elif choice == '5':
            current_aeroplanes = saver.get_all()
            print(f"Загружено {len(current_aeroplanes)} записей из файла.")

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()