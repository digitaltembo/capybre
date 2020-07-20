"""
Using Calibre's `fetch-ebook-metadata`_ tool,
looks up metadata based on title, author, and/or ISBN

..fetch-ebook-meta: https://manual.calibre-ebook.com/generated/en/fetch-ebook-metadata.html

"""
import os

from .helpers import random_filename, check_output
from .metadata import extract_raw_metadata_map, clean_metadata_map, Metadata


def fetch_metadata_map(title=None, author=None, isbn=None):
    """Extracts metadata about an ebook, returning a dict.
    At least one of title, author, or ISBN is required; it is suggested to
    either provide ISBN or both title and author. In the case of multiple books
    matching a particular set of identifiers, the first one found will be returned

    Args:
        title (str, optional): Title of the book
        author (str, optional): Author of the book
        isbn (str, optional): Book's ISBN code
    Returns:
        Dict mapping between metadata keys and values as directly output from
            the ebook-meta call
    """
    fetch_args = fetch_metadata_args(title, author, isbn)
    raw_metadata = check_output(fetch_args)
    return extract_raw_metadata_map(raw_metadata)


def fetch_metadata(title=None, author=None, isbn=None) -> Metadata:
    """Extracts metadata about an ebook, returning a :class:`Metadata` object.
    At least one of title, author, or ISBN is required; it is suggested to
    either provide ISBN or both title and author. In the case of multiple books
    matching a particular set of identifiers, the first one found will be returned

    Args:
        title (str, optional): Title of the book
        author (str, optional): Author of the book
        isbn (str, optional): Book's ISBN code
    Returns:
        :class:`Metadata` object
    """
    return clean_metadata_map(fetch_metadata_map(title, author, isbn))


def fetch_cover(title=None, author=None, isbn=None, output_file='cover.jpg'):
    """Downloads cover to specified file

    As it is impossible to download without also fetching metadata, also
    returns the metadata

    At least one of title, author, or ISBN is required; it is suggested to
    either provide ISBN or both title and author. In the case of multiple books
    matching a particular set of identifiers, the first one found will be returned

    Args:
        title (str, optional): Title of the book
        author (str, optional): Author of the book
        isbn (str, optional): Book's ISBN code
    Returns:
        :class:`Metadata` object
    """
    fetch_args = fetch_metadata_args(title, author, isbn) + ['-c', output_file]
    raw_metadata = check_output(fetch_args)
    return clean_metadata_map(extract_raw_metadata_map(raw_metadata))


class fetched_metadata_and_cover:
    """Fetches the cover image and metadata info inside a context.
    For use like::

        with fetched_metadata_and_cover(title='pride and prejudice') as metadata, cover:
            upload(cover, metadata)
    """

    def __init__(self, title=None, author=None, isbn=None):
        self.cover_filename = random_filename('jpg')
        self.title = title
        self.author = author
        self.isbn = isbn
        self.fp = None

    def __enter__(self):
        metadata = fetch_cover(
            self.title,
            self.author,
            self.isbn,
            self.cover_filename
        )
        self.fp = open(self.cover_filename, 'rb')

        return metadata, self.fp

    def __exit__(self, type, value, traceback):
        if self.fp:
            self.fp.close()
        if os.path.isfile(self.cover_filename):
            os.remove(self.cover_filename)


def fetch_metadata_args(title=None, author=None, isbn=None):
    args = ['fetch-ebook-metadata']
    if title:
        args += ['--title', title]
    if author:
        args += ['--author', author]
    if isbn:
        args += ['--isbn', isbn]
    if len(args) == 1:
        raise Exception('At least one of title, author and isbn must be specified')
    return args
