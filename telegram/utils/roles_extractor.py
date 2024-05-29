import pandas as pd


def parse_roles_greetings(file_path: str) -> dict:
    """
    Парсит Excel файл с ролями и обращениями, возвращая словарь.

    Аргументы:
    file_path : str
        Путь к файлу Excel.

    Возвращает:
    dict
        Словарь, где ключи — роли, а значения — обращения.
    """
    # Загрузка данных из Excel файла
    data = pd.read_excel(file_path)

    # Создание словаря из столбцов "Роль" и "Обращение"
    role_to_greeting = dict(zip(data['Роль'], data['Обращение']))

    return role_to_greeting
