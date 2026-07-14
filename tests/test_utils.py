import pandas as pd

from src.utils import df_to_list_of_dicts, read_excel_data


def test_read_excel_data_filters_and_cleans(tmp_path):
    file = tmp_path / "test.xlsx"
    pd.DataFrame(
        {
            "Дата операции": ["01.01.2021 10:00:00", "02.01.2021 11:00:00"],
            "Статус": ["OK", "FAILED"],
            "Номер карты": ["*1234", "*5678"],
            "Сумма операции": [-100, -200],
            "Сумма платежа": [-100, -200],
            "Кэшбэк": [10, 20],
            "Описание": ["Test", None],
            "Категория": ["Еда", None],
        }
    ).to_excel(file, index=False)

    df = read_excel_data(str(file))
    assert len(df) == 1
    assert df["Номер карты"].iloc[0] == "1234"
    assert df["Категория"].isna().sum() == 0


def test_df_to_list_of_dicts():
    df = pd.DataFrame({"Дата операции": pd.to_datetime(["01.01.2021"], format="%d.%m.%Y"), "Сумма": [-100]})
    res = df_to_list_of_dicts(df)
    assert res[0]["Дата операции"] == "01.01.2021"
