"""
Using Calibre's `ebook-meta``_ tool, extracts metadata and cover images from
ebook files

..ebook-meta: https://manual.calibre-ebook.com/generated/en/ebook-meta.html
"""

import os
import re
import datetime
from typing import List, Dict, Optional

from .helpers import random_filename, check_output, call
from .ebook_format import EbookFormat


class Metadata():
    """
    Standardization of the metadata output from `ebook-meta` with mild changes
    to parse and clean the data.

    The title field is guaranteed to exist, and ebook_format defaults ito
    EbookFormat.UNKNOWN if not specified, but everything else may be Nonr

    Args:
        author (str): Author (Looks like this may be an &-seperated list of
            authors for multi-author works)
        author_sort (str): String by which the author should be sorted
        description (str): Paragraph length text
        ebookFormat (EbookFormat): Enum of ebook formats used by Calibre
        identifiers (Dict[str,str]): Dict of identifiers, like {'isbn':'xxx'}
        isbn (str): ISBN
        language (str): Language used, seemingly in 3-letter language codes
        lastEdited (date): Timestamp on the file
        publication_date (date): Publication date of this edition
        publisher (str): Publisher's name
        rating (int): Rating, out of 5?
        series (str): Series that this belongs to
            (possibly including a number indicating rank in the series)
        tags (List[str]): List of tags describing the book
        title (str): Title
    """

    author:           Optional[str]
    author_sort:      Optional[str]
    description:      Optional[str]
    ebook_format:     EbookFormat
    identifiers:      Optional[Dict[str, str]]
    isbn:             Optional[str]
    language:         Optional[str]
    lastEdited:       Optional[datetime.date]
    publication_date: Optional[datetime.date]
    publisher:        Optional[str]
    rating:           Optional[int]
    series:           Optional[str]
    tags:             Optional[List[str]]
    title:            str

    def __init__(
        self,
        author=None,
        author_sort=None,
        description=None,
        ebook_format=EbookFormat.UNKNOWN,
        identifiers=None,
        isbn=None,
        publication_date=None,
        publisher=None,
        rating=None,
        series=None,
        tags=None,
        title=None
    ):
        self.author = author
        self.author_sort = author_sort
        self.description = description
        self.ebook_format = ebook_format
        self.identifiers = identifiers
        self.isbn = isbn
        self.publication_date = publication_date
        self.publisher = publisher
        self.rating = rating
        self.series = series
        self.tags = tags
        self.title = title


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
LAST_EDITED = 'Timestamp'

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
    author, author_sort = get_author_and_sort(metadata_map)
    description = get_string(metadata_map, DESCRIPTION)
    identifiers, isbn = get_identifiers(metadata_map)
    last_edited = get_date(metadata_map, LAST_EDITED)
    publication_date = get_date(metadata_map, PUBLISHED)
    publisher = get_string(metadata_map, PUBLISHED)
    rating = get_rating(metadata_map)
    series = get_string(metadata_map, SERIES)
    tags = get_tags(metadata_map)
    title = get_string(metadata_map, TITLE)

    return Metadata(
        author=author,
        author_sort=author_sort,
        description=description,
        identifiers=identifiers,
        isbn=isbn,
        publication_date=publication_date,
        publisher=publisher,
        rating=rating,
        series=series,
        tags=tags,
        title=title,
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


def get_author_and_sort(mmap):
    author = None
    author_sort = None
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
    if TAGS in mmap:
        return [t.strip() for t in mmap[TAGS].split(',')]
    return None


def get_identifiers(mmap):
    identifiers = None
    isbn = None
    if ISBN in mmap:
        isbn = mmap[ISBN]
    if IDENTIFIERS in mmap:
        identifiers = {
            key.strip(): value.strip()
            for key, _, value in [
                i.partition(':') for i in mmap[IDENTIFIERS].split(',')
            ]
        }
        if isbn is None:
            isbn = identifiers.get('isbn')
    return isbn, identifiers


def get_string(mmap, key):
    if key in mmap:
        return mmap[key]
    return None


def get_date(mmap, key):
    if key in mmap:
        try:
            date, _, _ = mmap[key].partition('T')
            return datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except(Exception):
            return None
    return None

def get_rating(mmap):
    if RATING in mmap:
        try:
            return int(mmap[RATING])
        except(Exception):
            return None
    return None
