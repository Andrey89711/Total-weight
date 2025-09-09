import os

def save(result_df):
    # Сохраняем результаты
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    excel_path = os.path.join(output_dir, 'результат.xlsx')
    result_df.to_excel(excel_path, index=False, engine='openpyxl')

    return excel_path

def save_csv(result_df):
    # Сохраняем результаты
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, 'результат.csv')
    result_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    return csv_path