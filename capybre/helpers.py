import os
import random
import string
import subprocess


def random_filename(extension, length=10):
    base = ''.join(random.choice(string.ascii_lowercase) for i in range(length))
    return '{}.{}'.format(base, extension)


def call(args, suppress_output=True):
    stdout = open(os.devnull, 'w') if suppress_output else None
    return subprocess.call(args, stdout=stdout)


def check_output(args):
    return subprocess.check_output(args).decode('UTF-8').split('\n')
