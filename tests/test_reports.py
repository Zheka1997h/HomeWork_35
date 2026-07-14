import pandas as pd

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


def test_reports_generate(tmp_path):
    df = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2021-12-01", "2021-12-05", "2021-12-11"]),  # 05 - воскресенье
            "Сумма платежа": [-100, -200, -300],
            "Категория": ["Еда", "Еда", "Еда"],
        }
    )
    file = str(tmp_path / "test.csv")

    res_cat = spending_by_category(df, "Еда", date="2021-12-20", filename=file)
    assert "total_spent" in res_cat.columns

    res_week = spending_by_weekday(df, date="2021-12-20", filename=file)
    assert "avg_spent" in res_week.columns

    res_work = spending_by_workday(df, date="2021-12-20", filename=file)
    assert "Тип дня" in res_work.columns
