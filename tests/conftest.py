import pandas as pd
import pytest


@pytest.fixture
def operations_list():
    return [
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
    ]
