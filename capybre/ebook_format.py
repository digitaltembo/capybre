from enum import Enum

import os

class EbookFormat(Enum):
    """
    EbookFormat is an enum representation of the supported output ebook
    formats: EPUB, LIT, LRF, FB2, MOBI, PDB, PDF, PMLZ, RB, TCR, TXT
    """
    UNKNOWN = 0
    EPUB = 1
    LIT = 2
    LRF = 3
    FB2 = 4
    MOBI = 5
    PDB = 6
    PDF = 7
    PMLZ = 8
    RB = 9
    TCR = 10
    TXT = 11

    def to_ext(self) -> str:
        """Gets the extension for the given EbookFormat Enum value"""
        if self in EBOOK_FORMAT_MAP:
            return EBOOK_FORMAT_MAP[self]
        return '???'

    @staticmethod
    def from_ext(name):
        """Gets the EbookFormat Enum value from the extension"""
        name = name.lower()
        if name in EBOOK_FORMAT_INVERSE_MAP:
            return EBOOK_FORMAT_INVERSE_MAP[name]
        return EbookFormat.UNKNOWN

    @staticmethod
    def from_filename(filename):
        _,ext = os.path.splitext(filename)
        return EbookFormat.from_ext(ext[1:])


EBOOK_FORMAT_MAP = {
    EbookFormat.EPUB: 'epub',
    EbookFormat.LIT:  'lit',
    EbookFormat.LRF:  'lrt',
    EbookFormat.FB2:  'fb2',
    EbookFormat.MOBI: 'mobi',
    EbookFormat.PDB:  'pdb',
    EbookFormat.PDF:  'pdf',
    EbookFormat.PMLZ: 'pmlz',
    EbookFormat.RB:   'rb',
    EbookFormat.TCR:  'tcr',
    EbookFormat.TXT:  'txt'
}

EBOOK_FORMAT_INVERSE_MAP = {
    value: key for key, value in EBOOK_FORMAT_MAP.items()
}
