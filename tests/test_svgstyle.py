import os
import shutil
import tempfile

from sphinxcontrib import plantuml


def setup():
    global _tempdir
    _tempdir = tempfile.mkdtemp()


def teardown():
    shutil.rmtree(_tempdir)


def writefile(fname, data):
    with open(fname, 'w') as f:
        f.write(data)


def test_get_svg_style():
    fname = os.path.join(_tempdir, 'a.svg')
    writefile(
        fname,
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<svg xmlns="http://www.w3.org/2000/svg" height="147pt" '
        'style="width:115px;height:147px;" version="1.1" viewBox="0 0 115 147" '
        'width="115pt"><defs/>')
    assert 'width:115px;height:147px;' == plantuml._get_svg_style(fname)
