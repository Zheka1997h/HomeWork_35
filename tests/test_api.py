import io
import os
import unittest
import unittest.mock as mock
from typing import Any, Dict

import requests

from src.api_handlers import AeroplanesAPI
from src.main import main
from src.models import Aeroplane
from src.storage import JSONSaver


class TestAeroplaneModel(unittest.TestCase):
    """Тесты для класса Aeroplane"""

    def setUp(self) -> None:
        """Создание тестовых объектов самолетов"""
        self.plane1 = Aeroplane(
            icao24="abc123",
            callsign="TEST1",
            origin_country="United States",
            time_position=1,
            last_contact=1,
            longitude=1.0,
            latitude=1.0,
            baro_altitude=10000.0,
            on_ground=False,
            velocity=200.0,
            true_track=90.0,
            vertical_rate=0.0,
        )
        self.plane2 = Aeroplane(
            icao24="def456",
            callsign="TEST2",
            origin_country="Russia",
            time_position=1,
            last_contact=1,
            longitude=2.0,
            latitude=2.0,
            baro_altitude=5000.0,
            on_ground=False,
            velocity=300.0,
            true_track=180.0,
            vertical_rate=0.0,
        )

    def test_attributes_exist(self) -> None:
        """Проверка наличия атрибутов"""
        self.assertEqual(self.plane1.icao24, "abc123")
        self.assertEqual(self.plane1.callsign, "TEST1")
        self.assertEqual(self.plane1.origin_country, "United States")
        self.assertEqual(self.plane1.baro_altitude, 10000.0)
        self.assertEqual(self.plane1.velocity, 200.0)

    def test_properties_altitude_and_speed(self) -> None:
        """Проверка свойств altitude и speed"""
        self.assertEqual(self.plane1.altitude, 10000.0)
        self.assertEqual(self.plane1.speed, 200.0)
        self.assertEqual(self.plane2.altitude, 5000.0)
        self.assertEqual(self.plane2.speed, 300.0)

    def test_comparison_height(self) -> None:
        """Проверка сравнения по высоте"""
        self.assertGreater(self.plane1.altitude, self.plane2.altitude)
        self.assertLess(self.plane2.altitude, self.plane1.altitude)
        self.assertNotEqual(self.plane1.altitude, self.plane2.altitude)

    def test_comparison_speed(self) -> None:
        """Проверка сравнения по скорости"""
        self.assertGreater(self.plane2.speed, self.plane1.speed)
        self.assertLess(self.plane1.speed, self.plane2.speed)

    def test_validation_empty_icao(self) -> None:
        """Проверка валидации: пустой ICAO24"""
        with self.assertRaises(ValueError) as context:
            Aeroplane("", "Test", "US", 1, 1, 1, 1, 1, False, 1, 1, 1)  # type: ignore[arg-type]
        self.assertIn("ICAO24 code cannot be empty", str(context.exception))

    def test_validation_invalid_altitude(self) -> None:
        """Проверка валидации: некорректная высота"""
        with self.assertRaises(ValueError) as context:
            Aeroplane("test123", "Test", "US", 1, 1, 1, 1, "invalid", False, 1, 1, 1)  # type: ignore[arg-type]
        self.assertIn("Barometric altitude must be a number", str(context.exception))

    def test_validation_invalid_velocity(self) -> None:
        """Проверка валидации: некорректная скорость"""
        with self.assertRaises(ValueError) as context:
            Aeroplane("test123", "Test", "US", 1, 1, 1, 1, 100, False, "invalid", 1, 1)  # type: ignore[arg-type]
        self.assertIn("Velocity must be a number", str(context.exception))

    def test_none_values_handling(self) -> None:
        """Проверка обработки None значений"""
        plane = Aeroplane(
            icao24="test",
            callsign=None,
            origin_country="US",
            time_position=None,
            last_contact=1,
            longitude=None,
            latitude=None,
            baro_altitude=None,
            on_ground=False,
            velocity=None,
            true_track=None,
            vertical_rate=None,
        )
        self.assertEqual(plane.altitude, 0.0)
        self.assertEqual(plane.speed, 0.0)

    def test_cast_to_object_list(self) -> None:
        """Проверка преобразования сырых данных"""
        raw_data: Dict[str, Any] = {
            "states": [
                ["abc", "CALL", "US", 1, 1, 1.0, 1.0, 100.0, False, 50.0, 90.0, 0.0],
                ["def", "CALL2", "RU", 2, 2, 2.0, 2.0, 200.0, False, 100.0, 180.0, 0.0],
            ]
        }
        objects = Aeroplane.cast_to_object_list(raw_data)
        self.assertEqual(len(objects), 2)
        self.assertIsInstance(objects[0], Aeroplane)
        self.assertEqual(objects[0].icao24, "abc")

    def test_cast_to_object_list_empty(self) -> None:
        """Проверка пустых данных"""
        self.assertEqual(Aeroplane.cast_to_object_list({}), [])

    def test_cast_to_object_list_no_states(self) -> None:
        """Проверка данных без ключа states"""
        self.assertEqual(Aeroplane.cast_to_object_list({"other": []}), [])

    def test_cast_to_object_list_invalid_state(self) -> None:
        """Проверка обработки битых данных внутри states"""
        raw_data: Dict[str, Any] = {
            "states": ["invalid_string", [], ["short"]]  # Не список  # Пустой список  # Слишком короткий список
        }
        objects = Aeroplane.cast_to_object_list(raw_data)
        self.assertEqual(len(objects), 0)

    def test_repr(self) -> None:
        """Проверка строкового представления"""
        repr_str = repr(self.plane1)
        self.assertIn("TEST1", repr_str)
        self.assertIn("10000.0", repr_str)


class TestJSONSaver(unittest.TestCase):
    """Тесты для класса JSONSaver"""

    def setUp(self) -> None:
        """Подготовка тестового файла"""
        self.test_file = "test_data.json"
        self.saver = JSONSaver(filename=self.test_file)
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self) -> None:
        """Очистка после тестов"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_get(self) -> None:
        """Проверка добавления и чтения"""
        plane = Aeroplane("test1", "TST", "TestLand", 1, 1, 1, 1, 100, False, 10, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(plane)
        loaded = self.saver.get_all()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].icao24, "test1")

    def test_add_multiple(self) -> None:
        """Проверка добавления нескольких записей"""
        p1 = Aeroplane("id1", "C1", "US", 1, 1, 1, 1, 100, False, 10, 1, 1)  # type: ignore[arg-type]
        p2 = Aeroplane("id2", "C2", "US", 1, 1, 1, 1, 200, False, 20, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(p1)
        self.saver.add_aeroplane(p2)
        self.assertEqual(len(self.saver.get_all()), 2)

    def test_add_duplicate(self) -> None:
        """Проверка защиты от дубликатов"""
        p = Aeroplane("id1", "C1", "US", 1, 1, 1, 1, 100, False, 10, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(p)
        self.saver.add_aeroplane(p)
        self.assertEqual(len(self.saver.get_all()), 1)

    def test_delete(self) -> None:
        """Проверка удаления"""
        p = Aeroplane("del1", "DEL", "US", 1, 1, 1, 1, 100, False, 10, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(p)
        self.assertTrue(self.saver.delete_aeroplane("del1"))
        self.assertEqual(len(self.saver.get_all()), 0)

    def test_delete_nonexistent(self) -> None:
        """Проверка удаления несуществующего ID"""
        self.assertFalse(self.saver.delete_aeroplane("nonexistent"))

    def test_find_by_criteria_country(self) -> None:
        """Поиск по стране"""
        p_ru = Aeroplane("ru1", "RU", "Russia", 1, 1, 1, 1, 5000, False, 10, 1, 1)  # type: ignore[arg-type]
        p_us = Aeroplane("us1", "US", "United States", 1, 1, 1, 1, 10000, False, 10, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(p_ru)
        self.saver.add_aeroplane(p_us)

        found = self.saver.find_by_criteria(country="Russia")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].origin_country, "Russia")

    def test_find_by_criteria_altitude(self) -> None:
        """Поиск по минимальной высоте"""
        p_low = Aeroplane("low", "L", "US", 1, 1, 1, 1, 1000, False, 10, 1, 1)  # type: ignore[arg-type]
        p_high = Aeroplane("high", "H", "US", 1, 1, 1, 1, 10000, False, 10, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(p_low)
        self.saver.add_aeroplane(p_high)

        found = self.saver.find_by_criteria(min_alt=5000)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].icao24, "high")

    def test_find_by_criteria_no_results(self) -> None:
        """Поиск без результатов"""
        p = Aeroplane("t1", "T", "US", 1, 1, 1, 1, 100, False, 10, 1, 1)  # type: ignore[arg-type]
        self.saver.add_aeroplane(p)
        found = self.saver.find_by_criteria(country="Nowhere")
        self.assertEqual(len(found), 0)

    def test_load_corrupted_json(self) -> None:
        """Проверка загрузки поврежденного JSON"""
        with open(self.test_file, "w") as f:
            f.write("{ invalid json }")
        # Метод get_all должен вернуть пустой список, а не упасть
        loaded = self.saver.get_all()
        self.assertEqual(len(loaded), 0)

    def test_load_json_not_list(self) -> None:
        """Проверка загрузки JSON, который не является списком"""
        with open(self.test_file, "w") as f:
            f.write('{"key": "value"}')
        loaded = self.saver.get_all()
        self.assertEqual(len(loaded), 0)


class TestAeroplanesAPI(unittest.TestCase):
    """Тесты для API хендлера"""

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_coordinates_success(self, mock_get: mock.Mock) -> None:
        """Проверка получения координат страны"""
        mock_response = mock.Mock()
        mock_response.json.return_value = [{"boundingbox": ["50.0", "60.0", "30.0", "40.0"]}]
        mock_response.raise_for_status = mock.Mock()
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_coordinates("Spain")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["south"], 50.0)
            self.assertEqual(result["north"], 60.0)
            self.assertEqual(result["west"], 30.0)
            self.assertEqual(result["east"], 40.0)

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_coordinates_not_found(self, mock_get: mock.Mock) -> None:
        """Проверка обработки, когда страна не найдена"""
        mock_response = mock.Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = mock.Mock()
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_coordinates("NonExistentCountry")

        self.assertIsNone(result)

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_coordinates_exception(self, mock_get: mock.Mock) -> None:
        """Проверка обработки исключения при запросе координат"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection Error")

        api = AeroplanesAPI()
        result = api.get_coordinates("ErrorCountry")

        self.assertIsNone(result)

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_aircraft_data_success(self, mock_get: mock.Mock) -> None:
        """Проверка получения данных о самолетах"""
        mock_response = mock.Mock()
        mock_response.json.return_value = {"states": []}
        mock_response.raise_for_status = mock.Mock()
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_aircraft_data([50.0, 30.0, 60.0, 40.0])

        self.assertIsNotNone(result)
        if result:
            self.assertIn("states", result)

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_aircraft_data_rate_limit(self, mock_get: mock.Mock) -> None:
        """Проверка обработки 429 Too Many Requests"""
        mock_response = mock.Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_aircraft_data([50.0, 30.0, 60.0, 40.0])

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["states"], [])

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_aircraft_data_exception(self, mock_get: mock.Mock) -> None:
        """Проверка обработки исключения при запросе самолетов"""
        mock_get.side_effect = requests.exceptions.RequestException("Timeout")

        api = AeroplanesAPI()
        result = api.get_aircraft_data([50.0, 30.0, 60.0, 40.0])

        self.assertIsNone(result)

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_aeroplanes_integration(self, mock_get: mock.Mock) -> None:
        """Интеграционный тест получения самолетов"""
        mock_response_coords = mock.Mock()
        mock_response_coords.json.return_value = [{"boundingbox": ["1", "2", "3", "4"]}]
        mock_response_coords.raise_for_status = mock.Mock()

        mock_response_planes = mock.Mock()
        mock_response_planes.json.return_value = {
            "states": [["abc", "CALL", "US", 1, 1, 1.0, 1.0, 100.0, False, 50.0, 90.0, 0.0]]
        }
        mock_response_planes.raise_for_status = mock.Mock()

        mock_get.side_effect = [mock_response_coords, mock_response_planes]

        api = AeroplanesAPI()
        result = api.get_aeroplanes("Spain")

        self.assertIsNotNone(result)
        if result:
            self.assertIn("states", result)

    @mock.patch("src.api_handlers.requests.Session.get")
    def test_get_aeroplanes_no_coords(self, mock_get: mock.Mock) -> None:
        """Тест, когда координаты не найдены"""
        mock_response = mock.Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = mock.Mock()
        mock_get.return_value = mock_response

        api = AeroplanesAPI()
        result = api.get_aeroplanes("Unknown")

        self.assertIsNone(result)


class TestMainInteraction(unittest.TestCase):
    """Тесты пользовательского интерфейса"""

    @mock.patch("builtins.input", side_effect=["1", "Spain", "0"])
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("src.main.AeroplanesAPI")
    @mock.patch("src.main.JSONSaver")
    def test_user_interaction_load_data(
        self, mock_saver_class: mock.Mock, mock_api_class: mock.Mock, mock_stdout: io.StringIO, mock_input: mock.Mock
    ) -> None:
        """Проверка загрузки данных"""
        mock_api_instance = mock.Mock()
        mock_api_instance.get_aeroplanes.return_value = {
            "states": [["abc", "CALL", "Russia", 1, 1, 1.0, 1.0, 1000.0, False, 50.0, 90.0, 0.0]]
        }
        mock_api_class.return_value = mock_api_instance

        mock_saver_instance = mock.Mock()
        mock_saver_class.return_value = mock_saver_instance

        try:
            main()
        except SystemExit:
            pass

        mock_api_instance.get_aeroplanes.assert_called()

    @mock.patch("builtins.input", side_effect=["1", "Spain", "2", "5", "0"])
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("src.main.AeroplanesAPI")
    @mock.patch("src.main.JSONSaver")
    def test_user_interaction_top_n(
        self, mock_saver_class: mock.Mock, mock_api_class: mock.Mock, mock_stdout: io.StringIO, mock_input: mock.Mock
    ) -> None:
        """Проверка вывода топ N"""
        mock_api_instance = mock.Mock()
        mock_api_instance.get_aeroplanes.return_value = {
            "states": [
                ["abc1", "CALL1", "Russia", 1, 1, 1.0, 1.0, 1000.0, False, 50.0, 90.0, 0.0],
                ["abc2", "CALL2", "Russia", 1, 1, 2.0, 2.0, 2000.0, False, 60.0, 90.0, 0.0],
                ["abc3", "CALL3", "Russia", 1, 1, 3.0, 3.0, 3000.0, False, 70.0, 90.0, 0.0],
            ]
        }
        mock_api_class.return_value = mock_api_instance

        mock_saver_instance = mock.Mock()
        mock_saver_class.return_value = mock_saver_instance

        try:
            main()
        except SystemExit:
            pass

        output = mock_stdout.getvalue()
        self.assertIn("Топ", output)
        self.assertIn("Загружено 3 самолетов", output)

    @mock.patch("builtins.input", side_effect=["2", "0"])
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("src.main.AeroplanesAPI")
    @mock.patch("src.main.JSONSaver")
    def test_user_interaction_top_n_zero(
        self, mock_saver_class: mock.Mock, mock_api_class: mock.Mock, mock_stdout: io.StringIO, mock_input: mock.Mock
    ) -> None:
        """Проверка ввода N=0 или меньше"""
        # Сначала пытаемся получить топ без данных (пункт 2), потом выходим
        mock_api_instance = mock.Mock()
        mock_api_class.return_value = mock_api_instance
        mock_saver_instance = mock.Mock()
        mock_saver_class.return_value = mock_saver_instance

        try:
            main()
        except SystemExit:
            pass

        output = mock_stdout.getvalue()
        # Должно быть сообщение о том, что данных нет или ошибка ввода
        self.assertIn("Сначала загрузите данные", output)

    @mock.patch("builtins.input", side_effect=["1", "Spain", "2", "-5", "2", "5", "0"])
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    @mock.patch("src.main.AeroplanesAPI")
    @mock.patch("src.main.JSONSaver")
    def test_user_interaction_top_n_negative_then_success(
        self, mock_saver_class: mock.Mock, mock_api_class: mock.Mock, mock_stdout: io.StringIO, mock_input: mock.Mock
    ) -> None:
        """Проверка ввода отрицательного N, затем успешного"""
        mock_api_instance = mock.Mock()
        mock_api_instance.get_aeroplanes.return_value = {
            "states": [
                ["abc1", "CALL1", "Russia", 1, 1, 1.0, 1.0, 1000.0, False, 50.0, 90.0, 0.0],
            ]
        }
        mock_api_class.return_value = mock_api_instance
        mock_saver_instance = mock.Mock()
        mock_saver_class.return_value = mock_saver_instance

        try:
            main()
        except SystemExit:
            pass

        output = mock_stdout.getvalue()
        self.assertIn("Ошибка: N должно быть больше 0", output)
        self.assertIn("Топ", output)


if __name__ == "__main__":
    unittest.main()
