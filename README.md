# kindle-okular-clippings
Show your Kindle clippings  as inline notes in KDE okular viewer.


## How does it work?
Okular saves reviews in an xml file into your ~/.kde/share/apps/okular/docdata.
kindleparse creates this xml file using "My Clippings.txt" data


## Testing
To test:

    # pip install -r requirements.txt
    # export PYTHONPATH+=:$PWD
    # nosetests -v -w test


## Running
Just:

   - download your "My Clippings.txt" from the Kindle
   - run the script
   - open your file with okular

That is

    #python kindleparse.py -c test/clippings.txt test/sample.pdf
    #okular test/sample.pdf


## TODO
Help is appreciate to:
  
    - convert clippings in html format;
    - reduce the opacity of the inline note canvas.
    - show clippings as highlighted text: this requires some acquaintance with the PDF format;
