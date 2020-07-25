import os
from unittest import TestCase
from datetime import date
from capybre import (
    extract_metadata,
    extract_metadata_map,
    extract_cover,
    extracted_cover_fileobj,
    EbookFormat,
)

from . import helpers


class MetadataTest(TestCase):

    def test_metadata(self):
        metadata = extract_metadata(helpers.SAMPLE_FILE)
        expected_dict = {
            'author': 'Jane Austen',
            'author_sort': 'Austen, Jane',
            'description': None,
            'ebook_format': EbookFormat.EPUB,
            'identifiers': {'uri': 'http://www.gutenberg.org/1342'},
            'isbn': None,
            'language': 'eng',
            'last_edited': None,
            'publication_date': date(1998, 6, 1),
            'publisher': None,
            'rating': None,
            'series': None,
            'tags': [
                'England -- Fiction',
                'Young women -- Fiction',
                'Love stories',
                'Sisters -- Fiction',
                'Domestic fiction',
                'Courtship -- Fiction',
                'Social classes -- Fiction'
            ],
            'title': 'Pride and Prejudice'
        }
        for key, value in metadata.__dict__.items():
            self.assertEqual(
                value,
                expected_dict[key],
                'Metadata item {} doesn\t match'.format(key)
            )

    def test_metadata_map(self):
        metadata_map = extract_metadata_map(helpers.SAMPLE_FILE)
        expectation = {
            'Title':       'Pride and Prejudice',
            'Author(s)':   'Jane Austen [Austen, Jane]',
            'Tags':        'England -- Fiction, Young women -- Fiction, ' +
                           'Love stories, Sisters -- Fiction, Domestic fiction, ' +
                           'Courtship -- Fiction, Social classes -- Fiction',
            'Languages':   'eng',
            'Published':   '1998-06-01T00:00:00+00:00',
            'Rights':      'Public domain in the USA.',
            'Identifiers': 'uri:http://www.gutenberg.org/1342'
        }

        for key, value in metadata_map.items():
            if key == 'Published':
                # publication time depends on timezone
                self.assertTrue(value.startswith('1998-06-01'))
            else:
                self.assertEqual(value, expectation[key])

    def test_cover_extraction(self):
        file = helpers.local_path('cover.jpg')
        extract_cover(helpers.SAMPLE_FILE, file)
        self.assertTrue(os.path.isfile(file))
        os.remove(file)

    def test_cover_temporary_extraction(self):
        initial_dir = helpers.local_files()
        f_file = None
        with extracted_cover_fileobj(helpers.SAMPLE_FILE) as f:
            f_file = f
            self.assertTrue(not f.closed)
            self.assertEqual(f.mode, 'rb')
            self.assertTrue(True)
        self.assertTrue(f_file.closed)
        self.assertEqual(helpers.local_files(), initial_dir)
