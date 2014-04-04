import unittest

from pycco.main import (parse, highlight, get_language)

import basetest


class WeirdResults(basetest.BaseTest):
    @unittest.skip("Field comment is associated with the class def")
    def test_parse_java_multi_on_line(self):
        in_source = u'''
public class AuthProvider {

    /** An internal field. */
    private static final String T = "T";
}
'''.lstrip()
        expected_output = {
            'text': u"An internal field. ",
            'html': u"<p>An internal field</p>"
        }
        lang = get_language("test.java", in_source, "java")
        sections = parse("test.java", in_source, lang)

        self.assertIsEqual(len(sections), 2, str(sections) + '\n' + self.to_html(sections, lang))
        self.assertEqual(sections[1]['docs_text'], expected_output['text'])

        highlight('test.java', sections, lang, outdir="/tmp")
        self.assertEqual(sections[1]['docs_html'], expected_output['html'])

