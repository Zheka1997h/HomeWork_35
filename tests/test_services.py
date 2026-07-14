from src.services import get_top_cashback_categories, investment_bank, search_transfers_to_individuals, simple_search


def test_investment_bank():
    data = [{"Дата операции": "15.01.2021", "Сумма операции": -1712}]
    assert investment_bank("2021-01", data, 50) == 38.0


def test_simple_search():
    data = [{"Описание": "Магазин Пятёрочка", "Категория": "Еда"}]
    assert len(simple_search("пятёрочка", data)) == 1


def test_search_transfers():
    data = [{"Категория": "Переводы", "Описание": "Иван И."}, {"Категория": "Переводы", "Описание": "ООО Ромашка"}]
    assert len(search_transfers_to_individuals(data)) == 1


def test_top_cashback():
    data = [{"Дата операции": "15.01.2021", "Категория": "Еда", "Кэшбэк": 100}]
    res = get_top_cashback_categories(data, 2021, 1)
    assert res.get("Еда") == 100
