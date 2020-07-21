# Capybre
![Tests](https://github.com/digitaltembo/capybre/workflows/Tests/badge.svg) [![Documentation Status](https://readthedocs.org/projects/capybre/badge/?version=latest)](https://capybre.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/capybre.svg)](https://badge.fury.io/py/capybre)


Thin python wrapper over (some of) the Calibre CLI. Can be used for ebook conversion, metadata-extraction, and metadata-lookup:

## Simple Usages
```
# convert between formats; creates 'PrideAndPrejudice.mobi'

from capybre import convert

convert('PrideAndPrejudice.epub', as_ext='mobi')


# extract metadata 
from capybre import extract_metada

metadata = extract_metadata('PrideAndPrejudice.epub')

# prints "Pride and Prejudice"
print(metadata.title)


# extract cover from metadata; saves as cover.jpg
from capybre import extract_cover

extract_cover('PrideAndPrejudice.epub', output_file='cover.jpg')


# fetch metadata from internet sources
from capybre import fetch_metadata

metadata = fetch_metadata(title='Pride and Prejudice')

# prints Jane Austen
print(metadata.author)


# download cover from internet sources; saves as cover.jpg
from capybre import fetch_cover

fetch_cover(title='Pride and Prejudice')
```

## Getting Started

First, you need to download Calibre's command line tools.

You can follow instructions [on Calibre's site](https://calibre-ebook.com/download>) to download, or download through package managers: 
```  
# on Ubuntu
sudo apt-get install calibre

# on MacOS
brew install calibre
```

On MacOS, the command line tools may not be added to your path. To access them, add ``/Applications/calibre.app/Contents/MacOS/`` to your PATH variable, for instance in ``~/.bashrc`` adding 
```
export PATH=$PATH:/Applications/calibre.app/Contents/MacOS/
```

Then, just install Capybre with pip!
```
pip install capybre
```

See the full documentation at [https://capybre.readthedocs.io/](https://capybre.readthedocs.io/)
