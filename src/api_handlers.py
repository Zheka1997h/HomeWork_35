from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import requests


class BaseAPIConnector(ABC):
    """
    Абстрактный класс для работы с API.
    Обязывает реализовать методы получения данных.
    """

    @abstractmethod
    def get_coordinates(self, country_name: str) -> Optional[Dict[str, Any]]:
        """Получить координаты bounding box страны"""
        pass

    @abstractmethod
    def get_aircraft_data(self, bbox: List[float]) -> Optional[Dict[str, Any]]:
        """Получить данные о самолетах в заданном периметре"""
        pass


class AeroplanesAPI(BaseAPIConnector):
    """
    Конкретная реализация коннектора к Nominatim и OpenSky Network.
    """

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CourseProjectBot/1.0 (student@example.com)"})

    def get_coordinates(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Получает boundingbox страны через Nominatim API.
        Возвращает словарь с ключами 'south', 'north', 'west', 'east'.
        """
        try:
            # Явная аннотация типа для params
            params: Dict[str, Union[str, int]] = {"q": country_name, "format": "json", "limit": 1}
            response = self.session.get(self.NOMINATIM_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list) or len(data) == 0:
                return None

            item = data[0]
            if not isinstance(item, dict):
                return None

            bbox_raw = item.get("boundingbox")

            if bbox_raw and isinstance(bbox_raw, list) and len(bbox_raw) == 4:
                try:
                    return {
                        "south": float(bbox_raw[0]),
                        "north": float(bbox_raw[1]),
                        "west": float(bbox_raw[2]),
                        "east": float(bbox_raw[3]),
                    }
                except ValueError, TypeError:
                    return None

            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates: {e}")
            return None

    def get_aircraft_data(self, bbox: List[float]) -> Optional[Dict[str, Any]]:
        """
        Получает данные о самолетах в прямоугольнике bbox.
        """
        try:
            # Явная аннотация типа для params
            params: Dict[str, float] = {"lamin": bbox[0], "lomin": bbox[1], "lamax": bbox[2], "lomax": bbox[3]}
            response = self.session.get(self.OPENSKY_URL, params=params, timeout=15)

            if response.status_code == 429:
                print("Warning: OpenSky rate limit exceeded. Try again later.")
                return {"states": []}

            response.raise_for_status()
            json_data = response.json()

            if isinstance(json_data, dict):
                return json_data
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching aircraft data: {e}")
            return None

    def get_aeroplanes(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Комплексный метод: получает координаты страны, затем самолеты.
        Возвращает сырые данные (dict), которые потом нужно преобразовать.
        """
        coords = self.get_coordinates(country_name)
        if not coords:
            print(f"Could not find coordinates for country: {country_name}")
            return None

        bbox_list = [float(coords["south"]), float(coords["west"]), float(coords["north"]), float(coords["east"])]

        raw_data = self.get_aircraft_data(bbox_list)
        return raw_data
