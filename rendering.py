from itertools import count
import pandas as pd
import os
import re


class ExcelConfig:
    """Конфигурация для обработки Excel файлов с различными названиями столбцов"""

    ALLOWED_HEADERS = [
        {
            "name": "Дата проводки",
            "aliases": ["Дата проводки", "Дата", "Date"],
            "type": "date"
        },
        {
            "name": "Наименование завода",
            "aliases": ["Наименование завода", "Завод", "Plant"],
        },
        {
            "name": "Подрядчик",
            "aliases": ["Подрядчик", "Контрагент", "Contractor"],
        },
        {
            "name": "Наименование подрядчика",
            "aliases": ["Наименование подрядчика", "Название контрагента", "Contractor Name"],
        },
        {
            "name": "Материал",
            "aliases": ["Материал", "Номенклатура", "Material", "Item"],
        },
        {
            "name": "Наименование материала",
            "aliases": ["Наименование материала", "Наименование номенклатуры",
                        "Material Name", "Item Description"],
        },
        {
            "name": "Количество",
            "aliases": ["Количество", "Отгружено с учётом корректировок",
                        "Quantity", "Кол-во"],
        },
        {
            "name": "Базисная ЕИ",
            "aliases": ["Базисная ЕИ", "Единица измерения", "Unit", "UOM"],
            "default": "КГ"
        },
        {
            "name": "Транспортная накладная",
            "aliases": ["Транспортная накладная", "Накладная GK", "Накладная",
                        "Transport Invoice", "Invoice"],
            "regex": ["Накладная", "GK", "Транспортная"]
        },
    ]


def find_matching_column(df_columns, config_item):
    """
    Находит подходящий столбец в DataFrame по конфигурации
    """
    df_columns = [str(col).strip() for col in df_columns]

    # Сначала ищем точное совпадение с алиасами
    for alias in config_item["aliases"]:
        if alias in df_columns:
            return alias

    # Если есть regex паттерны, ищем по ним
    if "regex" in config_item:
        for pattern in config_item["regex"]:
            for col in df_columns:
                if re.search(pattern, col, re.IGNORECASE):
                    return col

    # Если ничего не найдено, возвращаем None
    return None


def clean_region_name(file_name):
    """
    Очищает название региона от цифр, расширений файла и ненужных символов
    """
    # Убираем расширения файлов
    clean_name = file_name.replace('.xlsx', '').replace('.XLSX', '').replace('.xls', '').replace('.XLS', '')

    # Убираем цифры, точки, дефисы и прочие ненужные символы
    translator = str.maketrans('', '', '.0123456789-–—')
    region = clean_name.translate(translator)

    # Убираем пробелы в начале и конце, а также одиночные дефисы
    region = region.strip()

    # Убираем оставшиеся дефисы и прочие символы по краям
    region = re.sub(r'^[-–—\s]+|[-–—\s]+$', '', region)

    # Убираем множественные пробелы
    region = re.sub(r'\s+', ' ', region)

    return region.strip()


def standardize_dataframe(df, file_name):
    """
    Стандартизирует DataFrame согласно конфигурации
    """
    standardized_data = {}
    df_columns = df.columns.tolist()

    for config_item in ExcelConfig.ALLOWED_HEADERS:
        target_column = find_matching_column(df_columns, config_item)

        if target_column:
            # Копируем данные из найденного столбца
            standardized_data[config_item["name"]] = df[target_column]
        else:
            # Если столбец не найден, создаем пустой или со значением по умолчанию
            if "default" in config_item:
                standardized_data[config_item["name"]] = config_item["default"]
            else:
                standardized_data[config_item["name"]] = None

    # Создаем стандартизированный DataFrame
    result_df = pd.DataFrame(standardized_data)

    # Добавляем регион (очищенное имя файла)
    region = clean_region_name(file_name)
    result_df['Регион'] = region

    # Добавляем ID завода
    result_df['ID завода'] = result_df['Наименование завода'].astype(str).str[:6]

    # Обработка даты
    if 'Дата проводки' in result_df.columns:
        result_df['Дата проводки'] = result_df['Дата проводки'].astype(str).str.split(' ').str[0]

    return result_df


def rendering(files):
    all_dfs = []
    print('-' * 50)
    print("Начинаем обработку файлов...")

    for file in files:
        try:
            file_path = f'files/{file}'

            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                continue

            # Пробуем читать с разными движками
            df_raw = None
            for engine in ['openpyxl', 'xlrd', 'odf']:
                try:
                    df = pd.read_excel(file_path, engine=engine)
                    print('-' * 50)
                    print(f"✓ Успешно прочитан {file} с движком {engine}")
                    df_raw = df
                    break
                except Exception as e:
                    print(f"✗ Не удалось прочитать {file} с движком {engine}: {e}")
                    continue

            if df_raw is not None:
                # Стандартизируем DataFrame
                standardized_df = standardize_dataframe(df_raw, file)
                all_dfs.append(standardized_df)

                # Показываем как был обработан регион
                region_sample = standardized_df['Регион'].iloc[0] if len(standardized_df) > 0 else "N/A"
                print(f"✓ Файл {file} -> Регион: '{region_sample}'")

        except Exception as e:
            print(f"❌ Критическая ошибка с файлом {file}: {e}")
            continue

    if not all_dfs:
        print("Нет данных для обработки")
        return None

    print('-' * 50)

    # Объединяем все DataFrame
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Выбираем нужные колонки в правильном порядке (без source_file)
    final_columns = [
        'Дата проводки', 'ID завода', 'Наименование завода',
        'Подрядчик', 'Наименование подрядчика', 'Материал',
        'Наименование материала', 'Количество', 'Базисная ЕИ',
        'Транспортная накладная', 'Регион'
    ]

    # Оставляем только существующие колонки
    existing_columns = [col for col in final_columns if col in combined_df.columns]
    result_df = combined_df[existing_columns]

    print(f"Всего обработано файлов: {len(all_dfs)}")
    print(f"Всего строк: {len(result_df)}")
    print("Уникальные регионы:", result_df['Регион'].unique().tolist())

    return result_df


# Дополнительная функция для отладки - показывает какие столбцы найдены в файле
def analyze_file_columns(file_path):
    """Анализирует столбцы в файле для отладки"""
    try:
        df = pd.read_excel(file_path, nrows=1)
        print(f"Столбцы в файле {file_path}:")
        for i, col in enumerate(df.columns):
            print(f"  {i + 1}. {col}")
        return df.columns.tolist()
    except Exception as e:
        print(f"Ошибка при анализе файла {file_path}: {e}")
        return []


# Тестовая функция для проверки очистки имен регионов
def test_region_cleaning():
    """Тестирует очистку названий регионов"""
    test_names = [
        "ЕКБ -.xlsx",
        "МСК ЮГ -.xls",
        "НН -.XLSX",
        "МСК Восток -.xlsx",
        "МСК Север -.xlsx",
        "Саратов -.xlsx",
        "Краснодар123.xlsx",
        "СПб-456.xls"
    ]

    print("Тест очистки названий регионов:")
    print("-" * 40)
    for name in test_names:
        cleaned = clean_region_name(name)
        print(f"'{name}' -> '{cleaned}'")