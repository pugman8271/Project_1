import json
import re
from collections import Counter
from datetime import datetime

import pandas as pd


def open_json(directory):
    try:
        with open(directory, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return "файл не найден"
    except json.JSONDecodeError:
        return []


def open_xlsx(directory):
    reader_xlsx = pd.read_excel(directory)
    return reader_xlsx.to_dict(orient="records")


def get_card_number(operations_list):
    """Функция для получения списка уникальных карт"""
    cards = []
    for operation in operations_list:
        if operation["Номер карты"]:
            cards.append(operation["Номер карты"])
    cards = list(Counter(cards))
    cards = [card for card in cards if str(card).lower() != "nan"]
    return cards


def search_func(operations_list, category, keyword=""):
    """Универсальная функция для фильтрации данных по значениям: category/keyword"""
    searched_info = []
    pattern = re.compile(re.escape(keyword.lower()))  # Экранирование специального символа

    for operation in operations_list:
        # Проверяем наличие категории и соответствие ключевому слову
        if category in operation:
            value = operation[category]
            if isinstance(value, str) and re.search(pattern, value.lower()):
                searched_info.append(operation)

    return searched_info


def get_category(operations_list):
    """Функция для получения списка категорий"""
    category_list = []
    for operation in operations_list:
        if operation["Категория"]:
            category_list.append(operation["Категория"])
    category_list = list(Counter(category_list))
    category_list = [
        category_list
        for category_list in category_list
        if str(category_list).lower() != "nan"
    ]
    return category_list


def filter_by_data(operations_list, data):
    """Функция фильтрации списка операций по заданному промежутку времени
    принимает на вход дату, выдает список с начала месяца, по заданную дату"""
    end_date = datetime.strptime(data, "%Y-%m-%d")
    start_date = datetime.strptime(f"{end_date.year}-{end_date.month}-01", "%Y-%m-%d")

    filtered_operations = [
        op
        for op in operations_list
        if start_date
        <= datetime.strptime(str(op["Дата операции"]), "%d.%m.%Y %H:%M:%S")
        <= end_date
    ]
    return filtered_operations
