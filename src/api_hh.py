"""Модуль для взаимодействия с API hh.ru."""

from typing import Any

import requests


class HHApi:
    """Класс для работы с публичным API hh.ru.

    Предоставляет методы для получения информации о компаниях
    и их вакансиях.
    """

    BASE_URL = "https://api.hh.ru"

    @classmethod
    def get_employer_info(cls, employer_id: int) -> dict[str, Any]:
        """Получает информацию о работодателе по его ID.

        Args:
            employer_id: Идентификатор работодателя на hh.ru.

        Returns:
            Словарь с информацией о работодателе.

        Raises:
            requests.HTTPError: Если запрос завершился с ошибкой.
        """
        url = f"{cls.BASE_URL}/employers/{employer_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_employer_vacancies(
        cls,
        employer_id: int,
        per_page: int = 100,
        pages: int = 5,
    ) -> list[dict[str, Any]]:
        """Получает список вакансий работодателя.

        Args:
            employer_id: Идентификатор работодателя на hh.ru.
            per_page: Количество вакансий на странице (максимум 100).
            pages: Количество страниц для обработки.

        Returns:
            Список словарей с информацией о вакансиях.
        """
        vacancies: list[dict[str, Any]] = []
        for page in range(pages):
            params = {
                "employer_id": employer_id,
                "per_page": per_page,
                "page": page,
            }
            response = requests.get(
                f"{cls.BASE_URL}/vacancies",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            vacancies.extend(data.get("items", []))
            if page + 1 >= data.get("pages", 0):
                break
        return vacancies

    @staticmethod
    def parse_salary(salary: dict[str, Any] | None) -> int | None:
        """Преобразует информацию о зарплате в единый вид (в рублях).

        Args:
            salary: Словарь с информацией о зарплате из API.

        Returns:
            Среднее значение зарплаты в рублях или None,
            если зарплата не указана.
        """
        if salary is None or salary.get("currency") != "RUR":
            return None
        from_salary = salary.get("from")
        to_salary = salary.get("to")
        if from_salary and to_salary:
            return (from_salary + to_salary) // 2
        if from_salary:
            return from_salary
        if to_salary:
            return to_salary
        return None

