import unittest

from pygments import lexers

from pycco.main import (highlight, register_comment_styles, generate_html)

EXTRA_LANGUAGES = {
}


class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            lexers.get_lexer_by_name('cql')
            EXTRA_LANGUAGES['.cql'] = {'name': 'cql', 'symbol': '--', 'multistart': '/*', 'multiend': '*/' }
        except lexers.ClassNotFound:
            pass
        register_comment_styles(EXTRA_LANGUAGES)

    def assertIsEqual(self, expected, actual, msg=""):
        if msg:
            if isinstance(expected, basestring) and len(expected) > 20:
                prefix = "\n%r != \n%r"
            else:
                prefix = "%r != %r"
            prefix = prefix % (expected, actual)
            msg = prefix + '\n' + msg
        self.assertEqual(expected, actual, msg)

    def to_html(self, sections, lang, source='test.txt'):
        preserve_paths = True
        outdir = '/tmp'
        highlight(source, sections, lang, preserve_paths=preserve_paths, outdir=outdir)

        return generate_html(source, sections, preserve_paths=preserve_paths, outdir=outdir)
