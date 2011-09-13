# -*- coding: utf-8 -*-

import os.path
from setuptools import setup, find_packages

def read_file_contents(pathname):
    """
    Reads the contents of a given file relative to the directory
    containing this file and returns it.

    :param filename:
        The file to open and read contents from.
    """
    return open(os.path.join(os.path.dirname(__file__), pathname), 'rb').read()

setup(
    name="Pycco",
    version="0.2.0",
    description="""A Python port of Docco: the original quick-and-dirty,
        hundred-line-long, literate-programming-style documentation generator.
        """,
    long_description=read_file_contents('README'),
    author="Nick Fitzgerald",
    author_email="fitzgen@gmail.com",
    license="MIT License",
    url="http://fitzgen.github.com/pycco",
    keywords=' '.join(['python',
                       'literate',
                       'programming',
                       'documentation',
                       'generator',
                       ]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Documentation',
        'Topic :: Utilities',
        ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pycco = pycco:main',
            ]
        },
    install_requires=[
        'markdown',
        'pygments',
        'pystache',
        'smartypants',
        'cssmin',
        ],
    )
