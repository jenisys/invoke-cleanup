import os


def setup_workdir(directory_path, path_list):
    assert directory_path.exists() and directory_path.is_dir()
    for current_path in path_list:
        if current_path.endswith("/"):
            # -- CASE: directory
            current_directory = directory_path/current_path
            os.makedirs(str(current_directory))
            assert current_directory.exists()
            assert current_directory.is_dir()
        else:
            # -- CASE: file
            current_file = directory_path/current_path
            current_directory = current_file.parent
            if not current_directory.exists():
                os.makedirs(str(current_directory))
            current_file.write_text(u"")
            assert current_file.exists()
            assert current_file.is_file()
