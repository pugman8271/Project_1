import json

from src import utils
from src.utils import filter_by_data, get_category, open_xlsx
from src.views import (
    account_deposits,
    account_expenses,
    card_number,
    card_total_expenses_cashback,
    currency_rate,
    currency_stock_price,
    top_5_expenses,
    user_greeting,
)

# Записываем в переменные необходимые данные:
# Читаем настройки пользователя
setting_info = utils.open_json("user_settings.json")
# Записываем пусть к файлу с банковскими операциями в переменную
directory = "data/operations.xlsx"
# Получаем список банковских операций
operations_list = open_xlsx(directory)
# Получаем список категорий
category_list = get_category(operations_list)
# Получаем список уникальных карт
card_list = card_number(operations_list)

# Словари, в которых хранятся курсы акций и валюты
currency_rates = currency_rate(setting_info)
stock_prices = currency_stock_price(setting_info)

# Фильтруем список операций по дате
data_user_input = input("Введите дату в формате: ГГГГ-ММ-ДД\n")
try:
    operations_list = filter_by_data(operations_list, data_user_input)
except ValueError:
    print("Дата введена некорректно\n" "Будет выведен список всех операций")


def main_page():
    """Функция для формирования json-ответа для главной страницы"""
    json_main_w = {}
    json_main_w["greeting"] = user_greeting()
    json_main_w["cards"] = card_total_expenses_cashback(card_list, operations_list)
    json_main_w["top_transactions"] = top_5_expenses(operations_list)
    json_main_w["currency_rates"] = currency_rates
    json_main_w["stock_prices"] = stock_prices
    with open("data/json_info_main.json", "w", encoding="utf-8") as file:
        json.dump(json_main_w, file, ensure_ascii=False)


def main_events():
    """Функция для формирования json-ответа для страницы "События" """
    json_events_w = {}
    json_events_w["expenses"] = account_expenses(operations_list, category_list)
    json_events_w["income"] = account_deposits(operations_list, category_list)
    json_events_w["currency_rates"] = currency_rates
    json_events_w["stock_prices"] = stock_prices
    with open("data/json_info_events.json", "w", encoding="utf-8") as file:
        json.dump(json_events_w, file, ensure_ascii=False)


#
main_page()
main_events()
