from get_name_files import get_all_files
from rendering import rendering
from save import save, save_csv
from calculate import calculate_region_totals


def main():

    files = get_all_files('files/')
    print('-' * 50)
    print(f"Найдено файлов: {len(files)}")

    result_df = rendering(files)
    excel_path = save(result_df)

    calculate = calculate_region_totals(result_df)
    csv_path = save_csv(calculate)

    print('-' * 50)
    print("Успешно! Созданы файлы:")
    print(f"Excel: {excel_path}")
    print(f"CSV: {csv_path}")

    print(f"Всего записей: {len(result_df)}")
    print('-' * 50)

if __name__ == "__main__":
    main()