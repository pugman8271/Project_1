import json
import unittest
from unittest.mock import patch
from datetime import datetime
from unittest.mock import Mock
import pandas as pd
import pytest
import currencyapicom
from src.views import (
    user_greeting,
    card_number,
    card_total_expenses_cashback,
    top_5_expenses,
    currency_rate,
    currency_stock_price,
    account_expenses,
    account_deposits,
)


# тесты user_greeting
@patch("src.views.datetime")
def test_user_greeting(mock_datetime):
    # Создаем фиктивный объект времени
    mock_datetime.now.return_value = datetime(2023, 1, 1, 14, 0, 0)
    assert user_greeting() == "Добрый день"


# тесты card_number
@patch("src.views.get_card_number")
def test_card_number(mock_list):
    mock_list.return_value = ["*5555", "*6552", "*3884"]
    assert card_number(mock_list.return_value) == ["5555", "6552", "3884"]


# тесты card_total_expenses_cashback
@pytest.mark.parametrize(
    "card_list, expected",
    [
        (
            ["*7197"],
            [{"last_digits": "*7197", "total_spent": -3023.5, "cashback": 0.0}],
        ),
        (["*4556"], [{"last_digits": "*4556", "total_spent": -362.0, "cashback": 0}]),
        (
            ["*4556", "*7197"],
            [
                {"last_digits": "*4556", "total_spent": -362.0, "cashback": 0},
                {"last_digits": "*7197", "total_spent": -3023.5, "cashback": 0.0},
            ],
        ),
    ],
)
def test_card_total_expenses_cashback(card_list, expected, operations_list_test):
    result = card_total_expenses_cashback(card_list, operations_list_test)
    assert result == expected


# тесты top_5_expenses
@pytest.mark.parametrize("expected", [
    [
        {
            'amount': -3000.0,
            'category': 'Переводы',
            'date': '01.01.2018',
            'description': 'Линзомат ТЦ Юность',
        },
        {
            'amount': -815.68,
            'category': 'Супермаркеты',
            'date': '01.01.2021',
            'description': 'Дикси',
        },
        {
            'amount': -362.0,
            'category': 'Красота',
            'date': '04.01.2020',
            'description': 'OOO Balid',
        },
        {
            'amount': -357.96,
            'category': 'Супермаркеты',
            'date': '01.02.2021',
            'description': 'Магнит',
        },
        {
            "amount": -325.0,
            "category": "Фастфуд",
            "date": "03.02.2018",
            "description": "OOO Frittella",
        },
    ]
])
def test_card_top_5_expenses(expected, operations_list_test):
    result = top_5_expenses(operations_list_test)
    assert result == expected

# тесты currency_rate
@patch("src.views.currencyapicom.Client")
def test_currency_rate(mock_get):

    mock_client = mock_get.return_value
    mock_client.latest.return_value = {
        "data": {
            "RUB": {
                "value": 80.0
            }
        }
    }
    user_setting = {
        "user_currencies": ["USD", "RUB"]
    }

    expected_result = [{"currency": "USD", "rate": 80.0}]
    assert currency_rate(user_setting) == expected_result


# тесты currency_stock_price
@patch('requests.get')
def test_currency_stock_price(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ticker": "test_stock",
        "name": "Test",
        "price": 10.00,
        "exchange": "NASDAQ",
        "updated": 1706302801,
        "currency": "USD"
    }
    mock_get.return_value = mock_response
    user_setting = {"user_stocks": ["test_stock"]}
    expected_result = [{"stock": "Test", "price": 10.00}]
    assert currency_stock_price(user_setting) == expected_result

# тесты account_expenses
@pytest.mark.parametrize("expected" ,[{'main': [{'amount': '-4877', 'category': 'Без информации'}, {'amount': '-1509', 'category': 'Супермаркеты'}, {'amount': '0', 'category': 'Остальное'}], 'total_amount': -6386}])
def test_account_expenses(expected, operations_list_test):
    result = account_expenses(operations_list_test, ['Супермаркеты'])
    assert result == expected


# тесты account_deposits
@pytest.mark.parametrize("expected" ,[{'main': [], 'total_amount': 0}])
def test_account_deposits(expected, operations_list_test):
    result = account_deposits(operations_list_test, ['Переводы'])
    assert result == expected
