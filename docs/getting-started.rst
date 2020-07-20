Getting Started
===============

First, you need to download Calibre's command line tools.

You can follow instructions `on Calibre's site <https://calibre-ebook.com/download>`_ to download, or download through package managers: ::
    
    # on Ubuntu
    sudo apt-get install calibre

    # on MacOS
    brew install calibre

On MacOS, the command line tools may not be added to your path. To access them, add ``/Applications/calibre.app/Contents/MacOS/`` to your PATH variable, for instance in ``~/.bashrc`` adding ::
    
    export PATH=$PATH:/Applications/calibre.app/Contents/MacOS/

Then, just install Capybre with pip! ::
    
    pip install capybre


