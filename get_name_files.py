import os

def get_all_files(directory_path):
    try:
        # Проверяем существование директории
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Директория '{directory_path}' не существует")

        # Проверяем, что это действительно директория
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"'{directory_path}' не является директорией")

        # Получаем все элементы в директории
        all_items = os.listdir(directory_path)

        # Фильтруем только файлы (исключаем директории)
        files = [item for item in all_items if os.path.isfile(os.path.join(directory_path, item))]
        file = []

        for i in files:
            if '.DS_Store' != i:
                file.append(i)
        return file

    except Exception as e:
        print(f"Ошибка: {e}")
        return []
