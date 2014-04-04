import unittest

from pycco.main import (parse, highlight, generate_documentation, get_language, register_comment_styles, generate_html)

import basetest


class MultilineComments(basetest.BaseTest):
    @unittest.skip("not perfect, but the output is not that bad")
    def test_python_start_on_same_line(self):
        in_source = u'''
class BlockParser:
    """ Parse Markdown blocks into an ElementTree object.

    A wrapper class that stitches the various BlockProcessors together,
    looping through them and creating an ElementTree object.
    """

    def parseDocument(self, lines):
        """
        Parse a markdown document into an ElementTree.

        Given a list of lines, an ElementTree object (not just a parent Element)
        is created and the root element is passed to the parser as the parent.
        The ElementTree object is returned.

        This should only be called on an entire document, not pieces.
        """
        self.root = util.etree.Element(self.markdown.doc_tag)
        self.parseChunk(self.root, '\n'.join(lines))
'''.lstrip()
        expected_output = u'''Parse Markdown blocks into an ElementTree object.

A wrapper class that stitches the various BlockProcessors together,
looping through them and creating an ElementTree object.
'''

        lang = get_language('test.py', in_source, 'python')
        sections = parse('test.py', in_source, lang)
        self.assertIsEqual(4, len(sections), str(sections))
        self.assertIsEqual(expected_output, sections[0]['docs_text'],
                           self.to_html(sections, lang))

    def test_python_class_level(self):
        in_source = u'''
class BlockParser:
    """
    Parse Markdown blocks into an ElementTree object.

    A wrapper class that stitches the various BlockProcessors together,
    looping through them and creating an ElementTree object.
    """
'''.lstrip()
        expected_output = u'''
Parse Markdown blocks into an ElementTree object.

A wrapper class that stitches the various BlockProcessors together,
looping through them and creating an ElementTree object.

'''

        lang = get_language('test.py', in_source, 'python')
        result = parse('test.py', in_source, lang)
        self.assertIsEqual(2, len(result), str(result))
        self.assertIsEqual(expected_output, result[0]['docs_text'], " ")

    def test_pydoc(self):
        in_source = u'''
def parseDocument(self, lines):
    """
    Parse a markdown document into an ElementTree.

    Given a list of lines, an ElementTree object (not just a parent Element)
    is created and the root element is passed to the parser as the parent.
    The ElementTree object is returned.

    This should only be called on an entire document, not pieces.
    """
    self.root = util.etree.Element(self.markdown.doc_tag)
    self.parseChunk(self.root, '\n'.join(lines))
'''.lstrip()
        expected_out = u'''
Parse a markdown document into an ElementTree.

Given a list of lines, an ElementTree object (not just a parent Element)
is created and the root element is passed to the parser as the parent.
The ElementTree object is returned.

This should only be called on an entire document, not pieces.

'''
        lang = get_language('test.py', in_source, 'python')
        result = parse('test.py', in_source, lang)

        self.assertIsEqual(2, len(result), str(result))
        self.assertIsEqual(expected_out, result[0]['docs_text'], " ")

    def test_python_sameline(self):
        in_source = u'''
def get_language(source, code, language=None):
    """Get the current language we're documenting, based on the extension."""

    if language is not None:
        return
'''.lstrip()
        expected_out = u'''Get the current language we're documenting, based on the extension.\n'''

        lang = get_language('test.py', in_source, 'python')
        result = parse('test.py', in_source, lang)

        self.assertIsEqual(2, len(result), str(result))
        self.assertIsEqual(expected_out, result[0]['docs_text'], " ")

    def test_parse_python_classdef(self):
        in_source = u'''
class BlockParser: pass
    """Just a simple class"""
'''.lstrip()
        expected_output = {
            'text': u"Just a simple class\n",
            'html': u"<p>Just a simple class</p>"
        }
        lang = get_language('test.py', in_source, 'python')
        sections = parse("test.py", in_source, lang)
        self.assertIsEqual(len(sections), 2, str(sections))
        self.assertEqual(sections[0]['docs_text'], expected_output['text'])

        highlight('test.py', sections, lang, outdir="/tmp")
        self.assertEqual(sections[0]['docs_html'], expected_output['html'])

    @unittest.skip("No support for multi-line continuation symbols")
    def test_java(self):
        in_source = u'''
/**
 * Provides {@link Authenticator} instances for use when connecting
 * to Cassandra nodes.
 *
 * See {@link PlainTextAuthProvider} for an implementation which uses SASL
 * PLAIN mechanism to authenticate using username/password strings
 */
public interface AuthProvider {

    /**
     * The {@code Authenticator} to use when connecting to {@code host}
     *
     * @param host the Cassandra host to connect to.
     * @return The authentication implementation to use.
     */
    public Authenticator newAuthenticator(InetSocketAddress host) throws AuthenticationException;
}
'''.lstrip()
        expected_out = u'''
The {@code Authenticator} to use when connecting to {@code host}

@param host the Cassandra host to connect to.  
@return The authentication implementation to use.  
 '''

        lang = get_language('test.java', in_source, 'java')
        result = parse('test.java', in_source, lang)

        self.assertIsEqual(2, len(result), str(result))
        self.assertIsEqual(expected_out, result[1]['docs_text'], str(result))

    def test_sql(self):
        in_source = u'''
/*
As you'd expect, when creating a table you
must specify its fields and the primary key.
*/
CREATE TABLE employee
( id number(5),
name char(20),
);'''.lstrip()
        expected_out = u'''
As you'd expect, when creating a table you
must specify its fields and the primary key.

'''
        lang = get_language('test.sql', in_source, 'sql')
        sections = parse('test.sql', in_source, lang)

        self.assertIsEqual(1, len(sections), str(sections))
        self.assertIsEqual(expected_out, sections[0]['docs_text'], " ")
