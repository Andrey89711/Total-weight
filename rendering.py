from itertools import count
import pandas as pd
import os


def rendering(files):
    all_dfs = []
    print('-' * 50)

    for file in files:
        try:
            file_path = f'files/{file}'

            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                continue

            # Пробуем читать с разными движками
            df_read = None
            for engine in ['openpyxl', 'xlrd', 'odf']:
                try:
                    df = pd.read_excel(file_path, engine=engine)
                    print(f"Успешно прочитан {file} с движком {engine}")
                    df_read = df
                    break
                except Exception as e:
                    print(f"Не удалось прочитать {file} с движком {engine}: {e}")
                    continue

            if df_read is not None:
                # Извлекаем регион из имени файла ДО добавления в общий список
                translator = str.maketrans('', '', '.0123456789')
                region = file.translate(translator)[:-5]  # убираем расширение .xlsx

                # Добавляем регион для ВСЕХ строк этого файла
                df_read['Регион'] = region
                df_read['source_file'] = file

                all_dfs.append(df_read)

        except Exception as e:
            print(f"Ошибка с файлом {file}: {e}")
            continue

    if not all_dfs:
        print("Нет данных для обработки")
        return None
    print('-' * 50)

    # Объединяем все DataFrame
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Простое преобразование даты - убираем время
    combined_df['Дата проводки'] = combined_df['Дата проводки'].astype(str).str.split(' ').str[0]

    # Добавляем ID завода (первые 6 символов)
    combined_df['ID завода'] = combined_df['Наименование завода'].astype(str).str[:6]

    # Выбираем нужные колонки (убираем временные)
    result_df = combined_df[[
        'Дата проводки', 'ID завода', 'Наименование завода',
        'Подрядчик', 'Наименование подрядчика', 'Материал',
        'Наименование материала', 'Количество', 'Базисная ЕИ',
        'Транспортная накладная', 'Регион'
    ]]

    print(f"Всего строк: {len(result_df)}")

    return result_df