import json
import logging
import re
from collections import Counter
from datetime import datetime

import pandas as pd

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("logs/utils.log", "w", encoding="utf-8")
file_formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)


def open_json(directory):
    try:
        logger.info(f"Успешно открыт json файл {directory}")
        with open(directory, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"json файл не был найден {directory}")
        return "файл не найден"
    except json.JSONDecodeError:
        logger.error(f"не удалось открыть json файл {directory}, json.JSONDecodeError")
        return []


def open_xlsx(directory):
    reader_xlsx = pd.read_excel(directory)
    logger.info(f"xlsx файл {directory} успешно открыт ")
    return reader_xlsx.to_dict(orient="records")


def get_card_number(operations_list):
    """Функция для получения списка уникальных карт"""
    cards = []
    for operation in operations_list:
        if operation["Номер карты"]:
            cards.append(operation["Номер карты"])
    cards = list(Counter(cards))
    cards = [card for card in cards if str(card).lower() != "nan"]
    logger.info('из списка: "operations_list" успешно получен список уникальных карт')
    return cards


def search_func(operations_list, category, keyword=""):
    """Универсальная функция для фильтрации данных по значениям: category/keyword"""
    searched_info = []
    pattern = re.compile(
        re.escape(keyword.lower())
    )  # Экранирование специального символа

    for operation in operations_list:
        # Проверяем наличие категории и соответствие ключевому слову
        if category in operation:
            value = operation[category]
            if isinstance(value, str) and re.search(pattern, value.lower()):
                searched_info.append(operation)
    logger.info(
        f'из списка: "operations_list" успешно получен отфильтрованный список '
        f"операций по категории - {category} и ключу - {keyword}"
    )
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
    logger.info(
        'из списка: "operations_list" успешно получен список уникальных категорий'
    )
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
    logger.info(f"Получен список операций по заданной дате {data}")
    return filtered_operations
