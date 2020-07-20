import os
from unittest import TestCase

from capybre import extract_metadata, extract_metadata_map, extract_cover, extracted_cover_fileobj

from . import helpers

class MetadataTest(TestCase):

    def test_metadata(self):
        metadata = extract_metadata(helpers.SAMPLE_FILE)

        self.assertEqual(metadata.title, 'Pride and Prejudice')
        self.assertEqual(metadata.author, 'Jane Austen')
        self.assertEqual(metadata.author_sort, 'Austen, Jane')
        print(metadata.tags)
        self.assertEqual(metadata.tags, [
            'England -- Fiction', 
            'Young women -- Fiction', 
            'Love stories', 
            'Sisters -- Fiction', 
            'Domestic fiction', 
            'Courtship -- Fiction', 
            'Social classes -- Fiction', 
            'Language: eng'
        ])
        # that's probably good enough, although there are more fields defined

    def test_metadata_map(self):
        metadata_map = extract_metadata_map(helpers.SAMPLE_FILE)
        self.assertEqual(metadata_map, {
            'Title': 'Pride and Prejudice', 
            'Author(s)': 'Jane Austen [Austen, Jane]', 
            'Tags': 'England -- Fiction, Young women -- Fiction, Love stories, Sisters -- Fiction, Domestic fiction, Courtship -- Fiction, Social classes -- Fiction', 
            'Languages': 'eng', 
            'Published': '1998-06-01T04:00:00+00:00', 
            'Rights': 'Public domain in the USA.', 
            'Identifiers': 'uri:http://www.gutenberg.org/1342'
        })

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




