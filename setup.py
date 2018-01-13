# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = open('README.rst').read()

requires = ['Sphinx>=1.1', 'Pillow', 'six', 'docutils']
tests_require = ['pytest']

setup(
    name='sphinxcontrib-plantuml',
    version='0.9',
    url='https://github.com/sphinx-contrib/plantuml/',
    download_url='https://pypi.python.org/pypi/sphinxcontrib-plantuml',
    license='BSD',
    author='Yuya Nishihara',
    author_email='yuya@tcha.org',
    description='Sphinx "plantuml" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    tests_require=tests_require,
    include_package_data=True,
    install_requires=requires,
    extras_require=dict(
        pdf=['rst2pdf'],
        test=tests_require,
    ),
    namespace_packages=['sphinxcontrib'],
)
