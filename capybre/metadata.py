"""
Using Calibre's `ebook-meta``_ tool, extracts metadata and cover images from
ebook files

..ebook-meta: https://manual.calibre-ebook.com/generated/en/ebook-meta.html
"""

import os
import re
import datetime
from typing import List

from .helpers import random_filename, check_output, call
from .ebook_format import EbookFormat


class Metadata():
    """
    Somewhat opinionated standardization of the metadata format.
    The title field is guaranteed to exist, but everything else may just be
    an empty string

    Args:
        title (str): Title
        author (str): Author
        author_sort (str): String by which the author should be sorted
        tags (List[str]): List of tags, inluding possible rating, series,
            and publisher tags
        isbn (str): ISBN
        description (str): Paragraph length text
        publication_date (date): Publication date of this edition
    """
    title: str
    author: str
    author_sort: str
    tags: List[str]
    isbn: str
    description: str
    publication_date: datetime.date
    ebook_format: EbookFormat

    def __init__(
        self,
        title='',
        author='',
        author_sort='',
        tags=[],
        isbn='',
        description='',
        publication_date=None,
        ebook_format=EbookFormat.UNKNOWN
    ):
        self.title = title
        self.author = author
        self.author_sort = author_sort
        self.tags = tags
        self.isbn = isbn
        self.description = description
        self.publication_date = publication_date
        self.ebook_format = ebook_format


TITLE = 'Title'
AUTHOR = 'Author(s)'
PUBLISHER = 'Publisher'
TAGS = 'Tags'
LANGUAGE = 'Languages'
IDENTIFIERS = 'Identifiers'
DESCRIPTION = 'Comments'
SERIES = 'Series'
RATING = 'Rating'
ISBN = 'ISBN'
PUBLISHED = 'Published'

CALIBRE_AUTHOR_RE = re.compile("(.+)\\[(.+)\\]")
CALIBRE_ISBN_RE = re.compile('isbn:(.+)')


def extract_metadata(input_file) -> Metadata:
    """Extracts metadata from an ebook into the standardized :class:`Metadata` format

    Args:
        input_file (str): path to the input file
    Returns:
        :class:`Metadata` object
    """
    metadata = clean_metadata_map(extract_metadata_map(input_file))
    metadata.ebook_format = EbookFormat.from_filename(input_file)
    return metadata


def extract_metadata_map(input_file: str):
    """Extracts metadata from an ebook via an ``ebook-meta`` call, returning a dict

    Args:
        input_file (str): path to the input file
    Returns:
        Dict mapping between metadata keys and values as directly output from
            the ebook-meta call
    """
    raw_metadata = check_output(['ebook-meta', input_file])
    return extract_raw_metadata_map(raw_metadata)


def extract_raw_metadata_map(raw_metadata: List[str]):
    """Given output of ebook-meta program, extract metadata map
    Args:
        raw_metadata (List[str]): String representation of the lines produced
            by Calibre (also produced by a call to ``fetch-ebook-metadata``)
    Returns:
        Dict mapping between metadata keys and values as directly output from
            the ebook-meta call
    """
    metadata_lines = []
    for line in raw_metadata:
        # VERY brittle, but it looks like this is the only way to read the
        # output in case there is a newline in the value
        # (as seems to happen often in the description)
        if len(line.strip()) > 20 and line[20] == ':':
            key, _, value = line.partition(':')
            metadata_lines.append((key.strip(), value))
        elif len(metadata_lines) > 0:
            # append to the end of the previous line
            (key, value) = metadata_lines[-1]
            metadata_lines[-1] = (key, value + ' ' + line)

    return {key.strip(): value.strip() for key, value in metadata_lines}


def clean_metadata_map(metadata_map):
    """Cleans and standardizes the metadata map returned by :func:`extract_raw_metadata_map`

    Args:
        metadata_map (dict): Dict result of :func:`extract_raw_metadata_map`
    Returns:
        :class:`Metadata` object
    """
    title = get_title(metadata_map)
    author, author_sort = get_author_and_sort(metadata_map)
    tags = get_tags(metadata_map)
    isbn = get_isbn(metadata_map)
    description = get_description(metadata_map)
    publication_date = get_date(metadata_map)

    return Metadata(
        title=title,
        author=author,
        author_sort=author_sort,
        tags=tags,
        isbn=isbn,
        description=description,
        publication_date=publication_date
    )


def extract_cover(
    input_file: str,
    output_file: str = 'cover.jpg',
    suppress_output=True
):
    """Extracts the cover image from the given ebook, and saves it in the output file

    Args:
        input_file (str): path to the input file
        output_file (str, optional): path to the output cover image file,
            defaults to 'cover.jpg'
        suppress_output (bool, optional): Suppresses stdout from ebook-convert
            call (typically dozens of lines). Defaults to ``True``


    """
    call(['ebook-meta', input_file, '--get-cover', output_file], suppress_output)


class extracted_cover_fileobj:
    """Extracts the cover image and temporarily presents it as a fileobj context

    For use like ::

        with extracted_cover_fileobj('original.epub') as f:
            # f is file pointer to file object
            upload(f)

    Args:
        input_file (str): path to the input file
        output_file (str, optional): path to the output cover image file,
            defaults to 'cover.jpg'
        suppress_output (bool, optional): Suppresses stdout from ebook-convert call
            (typically dozens of lines). Defaults to ``True``


    """

    def __init__(self, input_file, suppress_output=True):
        self.input_file: str = input_file
        self.fp = None
        self.output_file = None
        self.suppress_output = suppress_output

    def __enter__(self):
        # make random new file
        self.output_file = random_filename('jpg')
        extract_cover(self.input_file, self.output_file, self.suppress_output)
        self.fp = open(self.output_file, 'rb')
        return self.fp

    def __exit__(self, type, value, traceback):
        if self.fp:
            self.fp.close()
        if self.output_file:
            os.remove(self.output_file)


"""
    Helper functions to extract metadata bits from the raw metadata map
"""


def get_title(mmap):
    return mmap[TITLE] if TITLE in mmap else ''


def get_author_and_sort(mmap):
    author = ''
    author_sort = ''
    if AUTHOR in mmap:
        author = mmap[AUTHOR]
        match = CALIBRE_AUTHOR_RE.match(author)
        if match:
            author = match[1].strip()
            author_sort = match[2].strip()
        else:
            first, _, last = author.partition(' ')
            if last:
                author_sort = '{}, {}'.format(last.strip(), first.strip())
            else:
                author_sort = first.strip()
    return author, author_sort


def get_tags(mmap):
    tags = []
    if TAGS in mmap:
        tags += mmap[TAGS].split(',')
    if LANGUAGE in mmap:
        tags.append('Language: '+mmap[LANGUAGE])
    if PUBLISHER in mmap:
        tags.append('Publisher: '+mmap[PUBLISHER])
    if RATING in mmap:
        tags.append('Rating: ' + mmap[RATING])
    if SERIES in mmap:
        tags.append('Series: ' + mmap[SERIES])

    return [t.strip() for t in tags]


def get_isbn(mmap):
    if ISBN in mmap:
        return mmap[ISBN]
    if IDENTIFIERS in mmap:
        identifiers = mmap[IDENTIFIERS].split(',')
        for id in identifiers:
            match = CALIBRE_ISBN_RE.match(id)
            if match:
                return match[1]
    return ''


def get_description(mmap):
    if DESCRIPTION in mmap:
        return mmap[DESCRIPTION]
    return ''


def get_date(mmap):
    if PUBLISHED in mmap:
        try:
            date, _, _ = mmap[PUBLISHED].partition('T')
            return datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except(Exception):
            return None
    return None
