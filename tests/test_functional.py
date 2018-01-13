import glob
from os import path, linesep, unlink, mkdir
import re
import tempfile
import shutil
import codecs

from sphinx.application import Sphinx
from unittest import skipIf
from six import PY2

_here = path.dirname(__file__)
_fixturedir = path.join(_here, 'fixture')
_fakecmd = path.join(_here, 'fakecmd.py')
_fakeepstopdf = path.join(_here, 'fakeepstopdf.py')


def setup():
    global _tempdir, _srcdir, _outdir
    _tempdir = tempfile.mkdtemp()
    _srcdir = path.join(_tempdir, 'src')
    _outdir = path.join(_tempdir, 'out')
    mkdir(_srcdir)


def teardown():
    shutil.rmtree(_tempdir)


def readfile(fname):
    with codecs.open(path.join(_outdir, fname), 'r', encoding='utf-8') as f:
        raw = f.read()
        print(raw)
        filtered = [l for l in raw.splitlines() if not l.startswith('%%')]
        print(filtered)
        return linesep.join(filtered)


def runsphinx(text, builder, confoverrides):
    with codecs.open(path.join(_srcdir, 'index.rst'), 'wb', encoding='utf-8') as f:
        f.write(text)
    app = Sphinx(_srcdir, _fixturedir, _outdir, _outdir, builder,
                 confoverrides)
    app.build()


def with_runsphinx(builder, **kwargs):
    confoverrides = {'plantuml': _fakecmd}
    confoverrides.update(kwargs)

    def wrapfunc(func):
        def test():
            src = '\n'.join(l[4:] for l in func.__doc__.splitlines()[2:])
            mkdir(_outdir)
            try:
                runsphinx(src, builder, confoverrides)
                func()
            finally:
                unlink(path.join(_srcdir, 'index.rst'))
                shutil.rmtree(_outdir)
        test.__name__ = func.__name__
        return test
    return wrapfunc


@with_runsphinx('html', plantuml_output_format='svg')
def test_buildhtml_simple_with_svg():
    """Generate simple HTML

    .. uml::

       Hello
    """
    pngfiles = glob.glob(path.join(_outdir, '_images', 'plantuml-*.png'))
    assert len(pngfiles) == 1
    svgfiles = glob.glob(path.join(_outdir, '_images', 'plantuml-*.svg'))
    assert len(svgfiles) == 1

    assert '<img src="_images/plantuml' in readfile('index.html')
    assert '<object data="_images/plantuml' in readfile('index.html')

    pngcontent = readfile(pngfiles[0]).splitlines()
    assert '-pipe' in pngcontent[0]
    assert 'Hello' in pngcontent[1][2:]
    svgcontent = readfile(svgfiles[0]).splitlines()
    assert '-tsvg' in svgcontent[0]
    assert 'Hello' in svgcontent[1][2:]


@with_runsphinx('html')
def test_buildhtml_samediagram():
    """Same diagram should be same file

    .. uml::

       Hello

    .. uml::

       Hello
    """
    files = glob.glob(path.join(_outdir, '_images', 'plantuml-*.png'))
    assert len(files) == 1
    imgtags = [l for l in readfile('index.html').splitlines()
               if '<img src="_images/plantuml' in l]
    assert len(imgtags) == 2


@with_runsphinx('html')
def test_buildhtml_alt():
    """Generate HTML with alt specified

    .. uml::
       :alt: Foo <Bar>

       Hello
    """
    assert 'alt="Foo &lt;Bar&gt;"' in readfile('index.html')


@with_runsphinx('html')
def test_buildhtml_caption():
    """Generate HTML with caption specified

    .. uml::
       :caption: Caption with **bold** and *italic*

       Hello
    """
    assert ('Caption with <strong>bold</strong> and <em>italic</em>'
            in readfile('index.html'))


@with_runsphinx('html')
def test_buildhtml_nonascii():
    u"""Generate simple HTML of non-ascii diagram

    .. uml::

       \u3042
    """
    files = glob.glob(path.join(_outdir, '_images', 'plantuml-*.png'))
    content = readfile(files[0]).splitlines()
    assert '-charset utf-8' in content[0]
    assert u'\u3042' == content[1][2:]


@with_runsphinx('latex')
def test_buildlatex_simple():
    """Generate simple LaTeX

    .. uml::

       Hello
    """
    files = glob.glob(path.join(_outdir, 'plantuml-*.png'))
    assert len(files) == 1
    assert re.search(r'\\(sphinx)?includegraphics\{+plantuml-',
                     readfile('plantuml_fixture.tex'))

    content = readfile(files[0]).splitlines()
    assert '-pipe' in content[0]
    assert 'Hello' == content[1][2:]


@with_runsphinx('latex', plantuml_latex_output_format='eps')
def test_buildlatex_simple_with_eps():
    """Generate simple LaTeX with EPS

    .. uml::

       Hello
    """
    files = glob.glob(path.join(_outdir, 'plantuml-*.eps'))
    assert len(files) == 1
    assert re.search(r'\\(sphinx)?includegraphics\{+plantuml-',
                     readfile('plantuml_fixture.tex'))

    content = readfile(files[0]).splitlines()
    assert '-teps' in content[0]
    assert 'Hello' == content[1][2:]


@with_runsphinx('latex', plantuml_latex_output_format='pdf')
def test_buildlatex_simple_with_pdf():
    """Generate simple LaTeX with PDF

    .. uml::

       Hello
    """
    epsfiles = glob.glob(path.join(_outdir, 'plantuml-*.eps'))
    pdffiles = glob.glob(path.join(_outdir, 'plantuml-*.pdf'))
    assert len(epsfiles) == 1
    assert len(pdffiles) == 1
    assert re.search(r'\\(sphinx)?includegraphics\{+plantuml-',
                     readfile('plantuml_fixture.tex'))

    epscontent = readfile(epsfiles[0]).splitlines()
    assert '-teps' in epscontent[0]
    assert 'Hello' == epscontent[1][2:]


@with_runsphinx('latex')
def test_buildlatex_with_caption():
    """Generate LaTeX with caption

    .. uml::
       :caption: Hello UML

       Hello
    """
    out = readfile('plantuml_fixture.tex')
    assert re.search(r'\\caption\{\s*Hello UML\s*\}', out)
    assert re.search(r'\\begin\{figure\}\[htbp\]', out)
    assert not re.search(r'\\begin\{flushNone', out)  # issue #136


@with_runsphinx('latex')
def test_buildlatex_with_align():
    """Generate LaTeX with caption

    .. uml::
       :align: right

       Hello
    """
    out = readfile('plantuml_fixture.tex')
    assert (re.search(r'\\begin\{figure\}\[htbp\]\\begin\{flushright\}', out)
            or re.search(r'\\begin\{wrapfigure\}\{r\}', out))


@skipIf(not PY2, "rst2pdf is not Python3 ready")
@with_runsphinx('pdf')
def test_buildpdf_simple():
    """Generate simple PDF

    .. uml::

       Hello
    """
    epsfiles = glob.glob(path.join(_outdir, 'plantuml-*.eps'))
    pdffiles = glob.glob(path.join(_outdir, 'plantuml-*.pdf'))
    assert len(epsfiles) == 1
    assert len(pdffiles) == 1

    epscontent = readfile(epsfiles[0]).splitlines()
    assert '-teps' in epscontent[0]
    assert 'Hello' == epscontent[1][2:]
