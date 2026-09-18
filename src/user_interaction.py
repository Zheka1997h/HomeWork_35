"""Модуль для взаимодействия с пользователем."""

from src.manager import DBManager


def show_menu() -> None:
    """Выводит меню на экран."""
    print("\n" + "=" * 50)
    print("Выберите действие:")
    print("1. Список всех компаний и количество вакансий")
    print("2. Список всех вакансий")
    print("3. Средняя зарплата по вакансиям")
    print("4. Вакансии с зарплатой выше средней")
    print("5. Вакансии по ключевому слову")
    print("0. Выход")
    print("=" * 50)


def user_interaction() -> None:
    """Функция взаимодействия с пользователем.

    Предоставляет текстовый интерфейс для работы с БД
    через методы класса DBManager.
    """
    db = DBManager()
    try:
        while True:
            show_menu()
            choice = input("Введите номер действия: ").strip()

            if choice == "1":
                data = db.get_companies_and_vacancies_count()
                print("\nКомпании и количество вакансий:")
                for company, count in data:
                    print(f"  • {company}: {count} вакансий")

            elif choice == "2":
                data = db.get_all_vacancies()
                print("\nВсе вакансии:")
                for company, vacancy, salary, url in data:
                    salary_str = (
                        f"{salary} руб." if salary else "зарплата не указана"
                    )
                    print(
                        f"  • [{company}] {vacancy} — {salary_str}\n"
                        f"    Ссылка: {url}"
                    )

            elif choice == "3":
                avg = db.get_avg_salary()
                if avg is not None:
                    print(f"\nСредняя зарплата: {int(avg)} руб.")
                else:
                    print("\nНет данных о зарплатах.")

            elif choice == "4":
                data = db.get_vacancies_with_higher_salary()
                if not data:
                    print("\nНет вакансий с зарплатой выше средней.")
                else:
                    print("\nВакансии с зарплатой выше средней:")
                    for company, vacancy, salary, url in data:
                        print(
                            f"  • [{company}] {vacancy} — {salary} руб.\n"
                            f"    Ссылка: {url}"
                        )

            elif choice == "5":
                keyword = input("Введите ключевое слово: ").strip()
                if not keyword:
                    print("Ключевое слово не может быть пустым.")
                    continue
                data = db.get_vacancies_with_keyword(keyword)
                if not data:
                    print(f"\nВакансий со словом '{keyword}' не найдено.")
                else:
                    print(f"\nВакансии со словом '{keyword}':")
                    for company, vacancy, salary, url in data:
                        salary_str = (
                            f"{salary} руб." if salary else "зарплата не указана"
                        )
                        print(
                            f"  • [{company}] {vacancy} — {salary_str}\n"
                            f"    Ссылка: {url}"
                        )

            elif choice == "0":
                print("До свидания!")
                break

            else:
                print("Некорректный ввод. Попробуйте снова.")
    finally:
        db.close()