import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.models import Aeroplane


class BaseStorage(ABC):
    """
    Абстрактный класс для хранения данных.
    """

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить самолет в хранилище"""
        pass

    @abstractmethod
    def get_all(self) -> List[Aeroplane]:
        """Получить все самолеты"""
        pass

    @abstractmethod
    def delete_aeroplane(self, icao24: str) -> bool:
        """Удалить самолет по ICAO24"""
        pass

    @abstractmethod
    def find_by_criteria(self, **kwargs: Any) -> List[Aeroplane]:
        """Поиск по критериям"""
        pass


class JSONSaver(BaseStorage):
    """
    Реализация хранения в JSON файле.
    """

    def __init__(self, filename: str = "airplanes_data.json") -> None:
        self.filename = filename
        if not os.path.exists(self.filename):
            self._save_to_file([])

    def _load_from_file(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError, FileNotFoundError:
            return []

    def _save_to_file(self, data: List[Dict[str, Any]]) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _convert_to_dict(self, aeroplane: Aeroplane) -> Dict[str, Any]:
        """Преобразует объект Aeroplane в словарь для JSON"""
        return {
            "icao24": aeroplane.icao24,
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "baro_altitude": aeroplane.baro_altitude,
            "velocity": aeroplane.velocity,
            "on_ground": aeroplane.on_ground,
        }

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = self._load_from_file()
        if not any(p.get("icao24") == aeroplane.icao24 for p in data):
            data.append(self._convert_to_dict(aeroplane))
            self._save_to_file(data)

    def get_all(self) -> List[Aeroplane]:
        raw_data = self._load_from_file()
        planes: List[Aeroplane] = []
        for item in raw_data:
            if not isinstance(item, dict):
                continue
            try:
                p = Aeroplane(
                    icao24=str(item.get("icao24", "")),
                    callsign=item.get("callsign"),
                    origin_country=str(item.get("origin_country", "")),
                    time_position=None,
                    last_contact=0,
                    longitude=None,
                    latitude=None,
                    baro_altitude=item.get("baro_altitude"),
                    on_ground=bool(item.get("on_ground", False)),
                    velocity=item.get("velocity"),
                    true_track=None,
                    vertical_rate=None,
                )
                planes.append(p)
            except ValueError, TypeError, KeyError:
                continue
        return planes

    def delete_aeroplane(self, icao24: str) -> bool:
        data = self._load_from_file()
        initial_len = len(data)
        new_data = [p for p in data if isinstance(p, dict) and p.get("icao24") != icao24]

        if len(new_data) < initial_len:
            self._save_to_file(new_data)
            return True
        return False

    def find_by_criteria(self, **kwargs: Any) -> List[Aeroplane]:
        """
        Поиск по критериям. Например: country='Russia', min_alt=1000
        """
        all_planes = self.get_all()
        filtered: List[Aeroplane] = []

        for plane in all_planes:
            match = True
            if "country" in kwargs:
                target_country = kwargs["country"]
                if isinstance(target_country, str) and target_country.lower() not in plane.origin_country.lower():
                    match = False
            if "min_alt" in kwargs:
                min_alt = kwargs["min_alt"]
                if isinstance(min_alt, (int, float)) and plane.altitude < min_alt:
                    match = False
            if "max_alt" in kwargs:
                max_alt = kwargs["max_alt"]
                if isinstance(max_alt, (int, float)) and plane.altitude > max_alt:
                    match = False

            if match:
                filtered.append(plane)
        return filtered
