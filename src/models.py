from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class Aeroplane:
    """
    Класс для представления данных о самолете.
    Реализует принципы инкапсуляции и сравнения.
    """
    icao24: str
    callsign: Optional[str]
    origin_country: str
    time_position: Optional[int]
    last_contact: int
    longitude: Optional[float]
    latitude: Optional[float]
    baro_altitude: Optional[float]
    on_ground: bool
    velocity: Optional[float]
    true_track: Optional[float]
    vertical_rate: Optional[float]

    # Дополнительные атрибуты для удобства
    _id: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Инициализация дополнительных полей и базовая валидация"""
        self._id = f"{self.origin_country}_{self.icao24}"
        self._validate_data()

    def _validate_data(self) -> None:
        """Валидация входных данных"""
        if not isinstance(self.icao24, str) or len(self.icao24) == 0:
            raise ValueError("ICAO24 code cannot be empty")

        # Валидация числовых значений, если они не None
        if self.baro_altitude is not None and not isinstance(self.baro_altitude, (int, float)):
            raise ValueError("Barometric altitude must be a number")

        if self.velocity is not None and not isinstance(self.velocity, (int, float)):
            raise ValueError("Velocity must be a number")

    @property
    def altitude(self) -> float:
        """Геттер для высоты (защита от None)"""
        return self.baro_altitude if self.baro_altitude is not None else 0.0

    @property
    def speed(self) -> float:
        """Геттер для скорости (защита от None)"""
        return self.velocity if self.velocity is not None else 0.0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.icao24 == other.icao24

    def __lt__(self, other: object) -> bool:
        """Сравнение по высоте для сортировки"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude < other.altitude

    def __gt__(self, other: object) -> bool:
        """Сравнение по высоте (исправлено: было по скорости, теперь единообразно)"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.altitude > other.altitude

    def __repr__(self) -> str:
        return (f"Aeroplane(callsign='{self.callsign}', country='{self.origin_country}', "
                f"alt={self.altitude}, speed={self.speed})")

    @staticmethod
    def cast_to_object_list(raw_data: Dict[str, Any]) -> List['Aeroplane']:
        """
        Преобразует сырой ответ от API OpenSky в список объектов Aeroplane.
        """
        if not raw_data or 'states' not in raw_data:
            return []

        aeroplanes: List[Aeroplane] = []
        states = raw_data.get('states')

        if not isinstance(states, list):
            return []

        for state in states:
            try:
                # Проверка, что state это список и имеет нужную длину
                if not isinstance(state, list) or len(state) < 12:
                    continue

                plane = Aeroplane(
                    icao24=str(state[0]),
                    callsign=state[1],
                    origin_country=str(state[2]),
                    time_position=state[3],
                    last_contact=state[4],
                    longitude=state[5],
                    latitude=state[6],
                    baro_altitude=state[7],
                    on_ground=bool(state[8]),
                    velocity=state[9],
                    true_track=state[10],
                    vertical_rate=state[11]
                )
                aeroplanes.append(plane)
            except (IndexError, ValueError, TypeError, KeyError):
                # Пропускаем битые данные, чтобы программа не падала
                continue
        return aeroplanes