import pandas as pd


def calculate_region_totals(result_df):

    if result_df is None or result_df.empty:
        print("Нет данных для расчета")
        return pd.DataFrame()

    # Группируем по региону и суммируем количество
    region_totals = result_df.groupby('Регион')['Количество'].sum().reset_index()
    region_totals.columns = ['Регион', 'Общий вес']

    # Округляем до 3 знаков после запятой
    region_totals['Общий вес'] = region_totals['Общий вес'].round(3)

    # Сортируем по убыванию веса
    region_totals = region_totals.sort_values('Общий вес', ascending=False)

    return region_totals