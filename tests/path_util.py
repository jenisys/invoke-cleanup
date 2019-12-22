import os
import stat

MODE_READABLE_MASK = (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
MODE_WRITABLE_MASK = (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
MODE_EXECUTABLE_MASK = (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def path_has_mask(path, mask, mode=None):
    path = str(path)
    if mode is None:
        mode = os.stat(path).st_mode
    mode = stat.S_IMODE(mode)
    return bool(mode & mask)

def path_is_writable(path, mode=None):
    return path_has_mask(path, MODE_WRITABLE_MASK, mode=mode)


def path_is_readable(path, mode=None):
    # path = str(path)
    # if mode is None:
    #     mode = os.stat(path).st_mode
    # mode = stat.S_IMODE(mode)
    # return bool(mode & MODE_READABLE_MASK)
    return path_has_mask(path, MODE_READABLE_MASK, mode=mode)


def path_is_executable(path, mode=None):
    return path_has_mask(path, MODE_EXECUTABLE_MASK, mode=mode)


def path_is_readonly(path, mode=None):
    return path_is_readable(path, mode) and not path_is_writable(path, mode)


def make_path_readonly(path, mode_mask=None):
    path = str(path)
    if mode_mask is None:
        mode_mask = MODE_READABLE_MASK
    mode = stat.S_IMODE(os.stat(path).st_mode)
    mode |= MODE_READABLE_MASK
    mode &= ~MODE_WRITABLE_MASK
    mode = ((mode & mode_mask) | stat.S_IRUSR)
    os.chmod(path, mode)
    assert path_is_readonly(path)


def make_path_readwrite(path):
    path = str(path)
    readwrite_mask = (stat.S_IRUSR | stat.S_IWUSR)
    mode = stat.S_IMODE(os.stat(path).st_mode)
    mode |= readwrite_mask
    os.chmod(path, mode)
    assert path_is_readable(path)
    assert path_is_writable(path)
