from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

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
        # Добавляем заголовки, чтобы нас не заблокировали сразу
        self.session.headers.update({
            'User-Agent': 'CourseProjectBot/1.0 (student@example.com)'
        })

    def get_coordinates(self, country_name: str) -> Optional[Dict[str, Any]]:
        """
        Получает boundingbox страны через Nominatim API.
        Возвращает словарь с ключами 'south', 'north', 'west', 'east'.
        """
        try:
            params = {
                'q': country_name,
                'format': 'json',
                'limit': 1
            }
            response = self.session.get(self.NOMINATIM_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list) or len(data) == 0:
                return None

            item = data[0]
            if not isinstance(item, dict):
                return None

            # boundingbox comes as [min_lat, max_lat, min_lon, max_lon]
            bbox_raw = item.get('boundingbox')

            if bbox_raw and isinstance(bbox_raw, list) and len(bbox_raw) == 4:
                try:
                    return {
                        'south': float(bbox_raw[0]),
                        'north': float(bbox_raw[1]),
                        'west': float(bbox_raw[2]),
                        'east': float(bbox_raw[3])
                    }
                except (ValueError, TypeError):
                    return None

            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates: {e}")
            return None

    def get_aircraft_data(self, bbox: List[float]) -> Optional[Dict[str, Any]]:
        """
        Получает данные о самолетах в прямоугольнике bbox.
        bbox format: [lamin, lomin, lamax, lomax] -> [min_lat, min_lon, max_lat, max_lon]
        """
        try:
            # OpenSky принимает параметры lamin, lomin, lamax, lomax
            params = {
                'lamin': bbox[0],  # min lat
                'lomin': bbox[1],  # min lon
                'lamax': bbox[2],  # max lat
                'lomax': bbox[3]  # max lon
            }
            response = self.session.get(self.OPENSKY_URL, params=params, timeout=15)

            # OpenSky часто возвращает 429 (Too Many Requests) или 503
            if response.status_code == 429:
                print("Warning: OpenSky rate limit exceeded. Try again later.")
                return {'states': []}

            response.raise_for_status()
            json_data = response.json()

            if isinstance(json_data, dict):
                return json_data
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching aircraft data: {e}")
            return None

    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """
        Комплексный метод: получает координаты страны, затем самолеты.
        Возвращает сырые данные (dict), которые потом нужно преобразовать.
        """
        coords = self.get_coordinates(country_name)
        if not coords:
            print(f"Could not find coordinates for country: {country_name}")
            return []

        # Формируем bbox для OpenSky: [min_lat, min_lon, max_lat, max_lon]
        bbox_list = [
            float(coords['south']),
            float(coords['west']),
            float(coords['north']),
            float(coords['east'])
        ]

        raw_data = self.get_aircraft_data(bbox_list)
        if raw_data:
            # Возвращаем весь ответ, так как cast_to_object_list ожидает dict с ключом 'states'
            return [raw_data]

        return []