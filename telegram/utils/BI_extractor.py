import pandas as pd


def create_bot_data_structure(file_path):
    # Загрузка данных из Excel файла
    data = pd.read_excel(file_path)

    # Заполняем пропущенные значения в столбце 'ФГ' для корректной группировки
    data['ФГ'] = data['ФГ'].ffill()

    # Инициализация словаря для данных
    bot_data = {}

    # Группировка по функциональной группе и агрегация данных
    for _, group in data.groupby('ФГ'):
        fg_name = group['ФГ'].iloc[0]  # Название функциональной группы
        choices = group['Варианты выбора'].tolist()  # Список вариантов выбора
        responses = group['Ответ'].tolist()  # Список ответов
        links = group['Unnamed: 3'].tolist()  # Список ссылок
        if 'ФГ ' in fg_name:
            fg_name = fg_name.replace('ФГ ', '')
        # Формирование структуры данных для каждой функциональной группы
        bot_data[fg_name.lower()] = {
            'варианты_выбора': choices,
            'ответы': responses,
            'доп_данные': links
        }

    return bot_data
