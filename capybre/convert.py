"""
Using Calibre's `ebook-convert'_ tool, converts files between supportedebook
formats. The format of the desired output can be specified either by
specifying the name of the output file, an ``EbookFormat`` enum value,
or the desired extenion.

..ebook-convert: https://manual.calibre-ebook.com/generated/en/ebook-convert.html
"""
import os

from .ebook_format import EbookFormat
from .helpers import call


def convert(
    input_file,
    output_file=None,
    as_format=EbookFormat.UNKNOWN,
    as_ext=None,
    suppress_output=True
) -> str:
    """Converts ebook at input_file to new format, returning the converted filepath

    Output format can be specified either through one of output_file,
    as_format, and as_ext. If the full output_file is not specified,
    the outputted file will have the same name as the input_file with
    a different extension

    Args:
        input_file (str): path to the input file
        output_file (str, optional): fully-specified path to the output file
        as_format (EbookFormat, optional): Enum representation of desired
            output format
        as_ext (str, optional): String representation of desired output format,
            e.g. ``mobi``
        suppress_output (bool, optional): Suppresses stdout from ebook-convert
            call (typically dozens of lines). Defaults to ``True``
    Returns:
        Path to the output file
    """

    if output_file is None:
        if as_ext:
            as_format = EbookFormat.from_ext(as_ext)
        if as_format == EbookFormat.UNKNOWN:
            raise Exception('Please specifiy a real extension')
        output_file = (input_file[:input_file.rfind('.')] +
                       '.' +
                       as_format.to_ext())

    call(['ebook-convert', input_file, output_file], suppress_output)

    return output_file


class converted_fileobj:
    """Context-object wrapper around convert

    Using the ``with X as Y:`` style, creates a temporary converted file
    object, opened in read-binary mode, and deletes it when finished.
    For use like ::

        with converted_fileobj('original.epub', target_extension='mobi') as f:
            # f is file pointer to file object
            upload(f)

    Args:
        input_file (str): path to the input file
        output_file (str, optional): fully-specified path to the output file
        as_format (EbookFormat, optional): Enum representation of desired
            output format
        as_ext (str, optional): String representation of desired output format,
            e.g. ``mobi``
        suppress_output (bool, optional): Suppresses stdout from ebook-convert
            call (typically dozens of lines). Defaults to ``True``

    """

    def __init__(
        self,
        input_file,
        as_format=None,
        as_ext=None,
        suppress_output=True
    ):
        self.input_file: str = input_file
        if as_format:
            self.as_format = as_format
        else:
            self.as_format = EbookFormat.from_ext(as_ext)
        self.suppress_output = suppress_output
        self.fp = None
        self.output_file = None

    def __enter__(self):
        self.output_file = convert(
            self.input_file,
            as_format=self.as_format,
            suppress_output=self.suppress_output
        )
        self.fp = open(self.output_file, 'rb')
        return self.fp

    def __exit__(self, type, value, traceback):
        if self.fp:
            self.fp.close()
        if self.output_file:
            os.remove(self.output_file)
