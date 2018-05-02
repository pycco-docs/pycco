from __future__ import absolute_import

import copy
import os
import os.path
import tempfile
import time

import pytest

import pycco.generate_index as generate_index
import pycco.main as p
from hypothesis import assume, example, given
from hypothesis.strategies import booleans, choices, lists, none, text
from pycco.languages import supported_languages

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch



PYTHON = supported_languages['.py']
PYCCO_SOURCE = 'pycco/main.py'
FOO_FUNCTION = """def foo():\n    return True"""


def get_language(choice):
    return choice(list(supported_languages.values()))


@given(lists(text()), text())
def test_shift(fragments, default):
    if fragments == []:
        assert p.shift(fragments, default) == default
    else:
        fragments2 = copy.copy(fragments)
        head = p.shift(fragments, default)
        assert [head] + fragments == fragments2


@given(text(), booleans(), text(min_size=1))
@example("/foo", True, "0")
def test_destination(filepath, preserve_paths, outdir):
    dest = p.destination(
        filepath, preserve_paths=preserve_paths, outdir=outdir)
    assert dest.startswith(outdir)
    assert dest.endswith(".html")


@given(choices(), text())
def test_parse(choice, source):
    lang = get_language(choice)
    parsed = p.parse(source, lang)
    for s in parsed:
        assert {"code_text", "docs_text"} == set(s.keys())


def test_skip_coding_directive():
    source = "# -*- coding: utf-8 -*-\n" + FOO_FUNCTION
    parsed = p.parse(source, PYTHON)
    for section in parsed:
        assert "coding" not in section['code_text']


def test_multi_line_leading_spaces():
    source = "# This is a\n# comment that\n# is indented\n"
    source += FOO_FUNCTION
    parsed = p.parse(source, PYTHON)
    # The resulting comment has leading spaces stripped out.
    assert parsed[0]["docs_text"] == "This is a\ncomment that\nis indented\n"


def test_comment_with_only_cross_ref():
    source = (
        '''# ==Link Target==\n\ndef test_link():\n    """[[testing.py#link-target]]"""\n    pass'''
    )
    sections = p.parse(source, PYTHON)
    p.highlight(sections, PYTHON, outdir=tempfile.gettempdir())
    assert sections[1][
        'docs_html'] == '<p><a href="testing.html#link-target">testing.py</a></p>'


@given(text(), text())
def test_get_language_specify_language(source, code):
    assert p.get_language(
        source, code, language_name="python") == supported_languages['.py']

    with pytest.raises(ValueError):
        p.get_language(source, code, language_name="non-existent")


@given(text() | none())
def test_get_language_bad_source(source):
    code = "#!/usr/bin/python\n"
    code += FOO_FUNCTION
    assert p.get_language(source, code) == PYTHON
    with pytest.raises(ValueError) as e:
        assert p.get_language(source, "badlang")

    msg = "Can't figure out the language!"
    try:
        assert e.value.message == msg
    except AttributeError:
        assert e.value.args[0] == msg


@given(text() | none())
def test_get_language_bad_code(code):
    source = "test.py"
    assert p.get_language(source, code) == PYTHON


@given(text(max_size=64))
def test_ensure_directory(dir_name):
    tempdir = os.path.join(tempfile.gettempdir(),
                           str(int(time.time())), dir_name)

    # Use sanitization from function, but only for housekeeping. We
    # pass in the unsanitized string to the function.
    safe_name = p.remove_control_chars(dir_name)

    if not os.path.isdir(safe_name) and os.access(safe_name, os.W_OK):
        p.ensure_directory(tempdir)
        assert os.path.isdir(safe_name)


def test_ensure_multiline_string_support():
    code = '''x = """
multi-line-string
"""

y = z  # comment

# *comment with formatting*

def x():
    """multi-line-string
    """'''

    docs_code_tuple_list = p.parse(code, PYTHON)

    assert docs_code_tuple_list[0]['docs_text'] == ''
    assert "#" not in docs_code_tuple_list[1]['docs_text']


def test_indented_block():

    code = '''"""To install Pycco, simply

    pip install pycco
"""
'''
    parsed = p.parse(code, PYTHON)
    highlighted = p.highlight(parsed, PYTHON, outdir=tempfile.gettempdir())
    pre_block = highlighted[0]['docs_html']
    assert '<pre>' in pre_block
    assert '</pre>' in pre_block


def test_generate_documentation():
    p.generate_documentation(PYCCO_SOURCE, outdir=tempfile.gettempdir())


@given(booleans(), booleans(), choices())
def test_process(preserve_paths, index, choice):
    lang_name = choice([l["name"] for l in supported_languages.values()])
    p.process([PYCCO_SOURCE], preserve_paths=preserve_paths,
              index=index,
              outdir=tempfile.gettempdir(),
              language=lang_name)


@patch('pygments.lexers.guess_lexer')
def test_process_skips_unknown_languages(mock_guess_lexer):
    class Name:
        name = 'this language does not exist'
    mock_guess_lexer.return_value = Name()

    with pytest.raises(ValueError):
        p.process(['LICENSE'], outdir=tempfile.gettempdir(), skip=False)

    p.process(['LICENSE'], outdir=tempfile.gettempdir(), skip=True)


one_or_more_chars = text(min_size=1, max_size=255)
paths = lists(one_or_more_chars, min_size=1, max_size=30)
@given(
    lists(paths, min_size=1, max_size=255),
    lists(one_or_more_chars, min_size=1, max_size=255)
)
def test_generate_index(path_lists, outdir_list):
    file_paths = [os.path.join(*path_list) for path_list in path_lists]
    outdir = os.path.join(*outdir_list)
    generate_index.generate_index(file_paths, outdir=outdir)


def test_flatten_sources(tmpdir):
    sources = [str(tmpdir)]
    expected_sources = []

    # Setup the base dir
    td = tmpdir.join("test.py")
    td.write("#!/bin/env python")
    expected_sources.append(str(td))

    # Make some more directories, each with a file present
    for d in ["foo", "bar", "buzz"]:
        dd = tmpdir.mkdir(d)
        dummy_file = dd.join("test.py")
        dummy_file.write("#!/bin/env python")
        expected_sources.append(str(dummy_file))

    # Get the flattened version of the base directory
    flattened = p._flatten_sources(sources)

    # Make sure that the lists are the same
    assert sorted(expected_sources) == sorted(flattened)
