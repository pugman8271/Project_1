import json
import unittest
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import (
    filter_by_data,
    get_card_number,
    get_category,
    open_json,
    open_xlsx,
    search_func,
)


# тесты open_json
@patch("json.load")
def test_open_json_correct(mock_test):
    mock_test.return_value = "test_pass"
    assert open_json("tests/user_settings_test.json") == "test_pass"


@patch("json.load", side_effect=FileNotFoundError)
def test_open_json_error_dir(mock_test):
    assert open_json("src/user_settings_test.json") == "файл не найден"


@patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "", 0))
def test_open_json_error_ecode(mock_test):
    assert open_json("tests/operations_test.xlsx") == []


# тесты open_xlsx
@patch("src.utils.pd.read_excel")
def test_open_xlsx_correct(mock_test):
    mock_df = pd.DataFrame({"column1": [1, 2], "column2": ["a", "b"]})
    mock_test.return_value = mock_df
    expected_result = mock_df.to_dict(orient="records")
    assert open_xlsx("tests/operations_test.xlsx") == expected_result


# тесты get_card_number
@pytest.mark.parametrize(
    "operations_list, expected",
    [
        ([{"Номер карты": "1234"}, {"Номер карты": "5678"}], ["1234", "5678"]),
        ([{"Номер карты": "1234"}, {"Номер карты": "1234"}], ["1234"]),
        ([{"Номер карты": "nan"}, {"Номер карты": "1234"}], ["1234"]),
        ([{"Номер карты": None}, {"Номер карты": ""}], []),
    ],
)
def test_get_card_number(operations_list, expected):
    assert get_card_number(operations_list) == expected


# тесты get_category
@pytest.mark.parametrize(
    "operations_list, expected",
    [
        ([{"Категория": "Продукты"}, {"Категория": "ЖКХ"}], ["Продукты", "ЖКХ"]),
        (
            [{"Категория": "Интернет магазин"}, {"Категория": "Интернет магазин"}],
            ["Интернет магазин"],
        ),
        ([{"Категория": "nan"}, {"Категория": "Транспорт"}], ["Транспорт"]),
        ([{"Категория": None}, {"Категория": ""}], []),
    ],
)
def test_get_category(operations_list, expected):
    assert get_category(operations_list) == expected


# тесты search_func
@pytest.mark.parametrize(
    "category, keyword, expected",
    [
        (
            "category1",
            "apple",
            [
                {
                    "category1": "apple",
                    "category2": "banana",
                    "Дата операции": "01.01.2021 18:08:23",
                }
            ],
        ),
        (
            "category2",
            "grape",
            [
                {
                    "category1": "orange",
                    "category2": "grape",
                    "Дата операции": "01.02.2021 12:09:06",
                }
            ],
        ),
        (
            "category1",
            "banana",
            [
                {
                    "category1": "banana",
                    "category2": "apple",
                    "Дата операции": "01.02.2021 18:43:51",
                }
            ],
        ),
        (
            "category2",
            "",
            [
                {
                    "category1": "apple",
                    "category2": "banana",
                    "Дата операции": "01.01.2021 18:08:23",
                },
                {
                    "category1": "orange",
                    "category2": "grape",
                    "Дата операции": "01.02.2021 12:09:06",
                },
                {
                    "category1": "banana",
                    "category2": "apple",
                    "Дата операции": "01.02.2021 18:43:51",
                },
            ],
        ),
    ],
)
def test_search_func(operations_list, category, keyword, expected):
    assert search_func(operations_list, category, keyword) == expected


# тесты filter_by_data


@pytest.mark.parametrize(
    "data, expected",
    [
        ("2020-02-02", []),
        (
            "2021-02-02",
            [
                {
                    "category1": "orange",
                    "category2": "grape",
                    "Дата операции": "01.02.2021 12:09:06",
                },
                {
                    "category1": "banana",
                    "category2": "apple",
                    "Дата операции": "01.02.2021 18:43:51",
                },
            ],
        ),
        ("2019-05-02", []),
        ("2018-08-02", []),
    ],
)
def test_filter_by_data(operations_list, data, expected):
    assert filter_by_data(operations_list, data) == expected
