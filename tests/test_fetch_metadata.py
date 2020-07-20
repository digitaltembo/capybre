import os
import socket
from unittest import TestCase

from capybre import fetch_metadata, fetch_cover, fetched_metadata_and_cover

from . import helpers


def has_internet():
    host = "8.8.8.8"
    port = 53
    timeout = 3
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
    return False


class FetchMetadataTest(TestCase):

    has_internet = True

    @classmethod
    def setUpClass(cls):
        cls.has_internet = has_internet()

    def test_fetch_by_title(self):
        if self.has_internet:
            # technically this works, although multiple books with the same name
            # seems to just return the first book it finds
            metadata = fetch_metadata(title='Pride and Prejdice')

            self.assertEqual(metadata.title, 'Pride and Prejudice')
            self.assertEqual(metadata.author, 'Jane Austen')
            self.assertEqual(metadata.author_sort, 'Austen, Jane')
            # that's probably good enough, although there are more fields defined

    def test_fetch_by_title_and_awthos(self):
        if self.has_internet:
            # probably should be the standard for lookup
            metadata = fetch_metadata(
                title='Pride and Prejdice',
                author='Jane Austen'
            )

            self.assertEqual(metadata.title, 'Pride and Prejudice')
            self.assertEqual(metadata.author, 'Jane Austen')
            self.assertEqual(metadata.author_sort, 'Austen, Jane')
            # that's probably good enough, although there are more fields defined

    def test_fetch_by_isbn(self):
        if self.has_internet:
            metadata = fetch_metadata(isbn='9780679783268')

            self.assertEqual(metadata.title, 'Pride and Prejudice')
            self.assertEqual(metadata.author, 'Jane Austen')
            self.assertEqual(metadata.author_sort, 'Austen, Jane')

    def test_fetch_cover_img(self):
        if self.has_internet:
            output_file = helpers.local_path('cover.jpg')
            fetch_cover(isbn='9780679783268', output_file=output_file)
            self.assertTrue(os.path.isfile(output_file))
            os.remove(output_file)

    def test_fetched_metadata_and_cover(self):
        if self.has_internet:
            initial_dir = helpers.local_files()
            c_file = None
            with fetched_metadata_and_cover(isbn='9780679783268') as (meta, cover):
                c_file = cover
                self.assertTrue(not cover.closed)
                self.assertTrue(cover.mode, 'rb')
                self.assertEqual(meta.title, 'Pride and Prejudice')
                self.assertEqual(meta.author, 'Jane Austen')
                self.assertEqual(meta.author_sort, 'Austen, Jane')

            self.assertTrue(c_file.closed)
            self.assertEqual(helpers.local_files(), initial_dir)
