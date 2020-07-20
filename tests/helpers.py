import os

SAMPLE = 'PrideAndPrejudice.epub'

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def local_path(file):
    return os.path.join(THIS_DIR, file)


SAMPLE_FILE = local_path(SAMPLE)


def local_files():
    return os.listdir(local_path('.'))
