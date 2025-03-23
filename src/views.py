import datetime
import os
from datetime import datetime
import currencyapicom
import requests
from black.trans import defaultdict
from dotenv import load_dotenv
from src import utils
from src.utils import get_card_number, search_func

load_dotenv("src/.env")

API_KEY_apilayer_1 = os.getenv("API_KEY_apilayer_1")
API_KEY_apilayer_2 = os.getenv("API_KEY_apilayer_2")


setting_info = utils.open_json("../user_settings.json")


def user_greeting():
    """Функция приветсвия пользоавтеля в зависимости от текущего времени функции"""
    time_user = datetime.now().hour
    if 5 <= time_user < 12:
        greeting_user = "Доброе утро"
    elif 12 <= time_user < 16:
        greeting_user = "Добрый день"
    elif 16 <= time_user < 23:
        greeting_user = "Добрый вечер"
    else:
        greeting_user = "Доброй ночи"

    return greeting_user


def card_number(operations_list):
    """Функция для вывода списка уникальных номеров карт из файла с оперциями
    принимаеи на вход списко оперций"""
    cards = get_card_number(operations_list)
    cards_list = []
    for card in cards:
        cards_list.append(card[1:])
    return cards_list


def card_total_expenses_cashback(card_list, operations_list):
    """Функция для вывода информации по каждйо карте, принимает список оперций импортированный из
    файла и список уникальных номеров карт"""
    total_expenses_cashback = []
    for card in card_list:
        card_info = search_func(operations_list, "Номер карты", card)
        card_dict = {}
        card_dict["last_digits"] = card
        card_dict["total_spent"] = 0
        card_dict["cashback"] = 0
        for operation in card_info:
            if operation.get("Сумма операции") <= 0:
                card_dict["total_spent"] += round(
                    (float(operation.get("Сумма операции"))), 2
                )
            if operation.get("Бонусы (включая кэшбэк)") <= 0:
                card_dict["cashback"] += round(
                    (float(operation.get("Бонусы (включая кэшбэк)"))), 2
                )
        total_expenses_cashback.append(card_dict)

    return total_expenses_cashback


def top_5_expenses(operations_list):
    """Фунуция поиска топ-5 операций по сумме платежа"""
    sorted_operations = sorted(
        operations_list, key=lambda x: abs(x.get("Сумма платежа")), reverse=True
    )
    top_transactions = sorted_operations[:5]
    result = []
    for operation in top_transactions:
        filtered_info = {
            "date": operation.get("Дата платежа"),
            "amount": operation.get("Сумма операции"),
            "category": operation.get("Категория"),
            "description": operation.get("Описание"),
        }
        result.append(filtered_info)
    return result


def currency_rate(user_setting):
    try:
        client = currencyapicom.Client(API_KEY_apilayer_1)
        result_1 = client.latest(
            user_setting["user_currencies"][0], [user_setting["user_currencies"][1]]
        )
    except Exception:
        return "Что-то пошло не так"
    result_dict = {}
    rate = round((result_1["data"][user_setting["user_currencies"][1]]["value"]), 2)
    currency = user_setting["user_currencies"][0]
    result_dict["currency"] = currency
    result_dict["rate"] = rate
    return [result_dict]


def currency_stock_price(user_setting):
    stock_info = []
    stock_list = user_setting["user_stocks"]
    for stock in stock_list:
        symbol = stock
        api_url = "https://api.api-ninjas.com/v1/stockprice?ticker={}".format(symbol)
        response = requests.get(api_url, headers={"X-Api-Key": API_KEY_apilayer_2})
        if response.status_code == requests.codes.ok:
            text_to_dict = response.json()  # Изменено на response.json()
            stock_info.append(
                {"stock": text_to_dict["name"], "price": text_to_dict["price"]}
            )
        else:
            stock_info = f"Error:, {response.status_code}, {response.text}"
    return stock_info


def account_expenses(operations_list, category_list):
    expenses_dict = defaultdict(int)
    for operation in operations_list:
        found_category = False
        for category in category_list:
            if category == operation.get("Категория"):
                if operation.get("Сумма операции") < 0:
                    expenses_dict[category] += round(operation.get("Сумма операции"))
                found_category = True
                break
        if not found_category and operation.get("Сумма операции") < 0:
            expenses_dict["Без информации"] += round(operation.get("Сумма операции"))

    expenses_dict_sorted = sorted(expenses_dict.items(), key=lambda item: item[1])
    expenses_dict_sorted_top = dict(expenses_dict_sorted[:7])
    expenses_dict_sorted_top["Остальное"] = sum(dict(expenses_dict_sorted[7:]).values())
    total_expenses = sum(dict(expenses_dict_sorted).values())
    # Создаем новый лист, удовлетворяющий требованиям json ответа по ТЗ
    list_to_format = []
    for k, v in expenses_dict_sorted_top.items():
        new_dict = {}
        new_dict["category"] = f"{k}"
        new_dict["amount"] = f"{v}"
        list_to_format.append(new_dict)
    # Создаем новый словарь, удовлетворяющий требованиям json ответа по ТЗ
    dict_to_return = {}
    dict_to_return["total_amount"] = round(total_expenses)
    dict_to_return["main"] = list_to_format

    return dict_to_return


def account_deposits(operations_list, category_list):
    deposits_dict = defaultdict(int)
    for operation in operations_list:
        found_category = False
        for category in category_list:
            if category == operation.get("Категория"):
                if operation.get("Сумма операции") > 0:
                    deposits_dict[category] += round(operation.get("Сумма операции"))
                found_category = True
                break
        if not found_category and operation.get("Сумма операции") > 0:
            deposits_dict["Без информации"] += round(operation.get("Сумма операции"))

    deposits_dict_sorted = dict(sorted(deposits_dict.items(), key=lambda item: item[1]))
    total_deposits = sum(deposits_dict_sorted.values())

    # Создаем новый лист, удовлетворяющий требованиям json ответа по ТЗ
    list_to_format = []
    for k, v in deposits_dict_sorted.items():
        new_dict = {}
        new_dict["category"] = f"{k}"
        new_dict["amount"] = f"{v}"
        list_to_format.append(new_dict)
    # Создаем новый словарь, удовлетворяющий требованиям json ответа по ТЗ
    dict_to_return = {}
    dict_to_return["total_amount"] = round(total_deposits)
    dict_to_return["main"] = list_to_format

    return dict_to_return
