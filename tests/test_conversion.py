import os
from unittest import TestCase

from capybre import convert, converted_fileobj, EbookFormat

from . import helpers


class ConversionTest(TestCase):
    def test_convert(self):
        output_file = helpers.local_path('test.mobi')
        convert(helpers.SAMPLE_FILE, output_file=output_file)
        self.assertTrue(os.path.isfile(output_file))
        os.remove(output_file)

    def test_convert_format(self):
        output_file = helpers.local_path('PrideAndPrejudice.mobi')
        convert(helpers.SAMPLE_FILE, as_format=EbookFormat.MOBI)
        self.assertTrue(os.path.isfile(output_file))
        os.remove(output_file)

    def test_convert_extension(self):
        output_file = helpers.local_path('PrideAndPrejudice.mobi')
        convert(helpers.SAMPLE_FILE, as_ext='mobi')
        self.assertTrue(os.path.isfile(output_file))
        os.remove(output_file)

    def test_convert_context(self):
        initial_dir = helpers.local_files()
        f_file = None
        with converted_fileobj(helpers.SAMPLE_FILE, as_ext='mobi') as f:
            f_file = f
            self.assertTrue(not f.closed)
            self.assertEqual(f.mode, 'rb')
        self.assertTrue(f_file.closed)
        self.assertEqual(helpers.local_files(), initial_dir)
