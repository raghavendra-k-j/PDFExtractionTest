import os

def extract_name_ext(file_path: str) -> tuple[str | None, str | None]:
    if not file_path or not isinstance(file_path, str):
        return None, None

    file_name, file_extension = os.path.splitext(file_path)

    if not file_name or not file_extension:
        return None, None

    return file_name, file_extension.lower().lstrip('.')
