from pycco.main import (parse, highlight, get_language)

import basetest


class SingleComment(basetest.BaseTest):
    def test_parse_python(self):
        in_source = u'''
# Create the template that we will use to generate the Pycco HTML page.
pycco_template = template(pycco_resources.html)

# The CSS styles we'd like to apply to the documentation.
# Currently there's no way to customize it.
pycco_styles = pycco_resources.css
'''.lstrip()
        expected_output = {
            'text': u"The CSS styles we'd like to apply to the documentation.\nCurrently there's no way to customize it.\n",
            'html': u"<p>The CSS styles we'd like to apply to the documentation.\nCurrently there's no way to customize it.</p>"
        }

        lang = get_language('test.py', in_source, 'python')
        result = parse("test.py", in_source, lang)
        self.assertIsEqual(len(result), 2)
        self.assertEqual(result[1]['docs_text'], expected_output['text'])

        highlight('test.py', result, lang)
        self.assertEqual(result[1]['docs_html'], expected_output['html'])

    def test_parse_java(self):
        in_source = u'''
// See {@link PlainTextAuthProvider} for an implementation which uses SASL
// PLAIN mechanism to authenticate using username/password strings
public interface AuthProvider {

    // The {@code Authenticator} to use when connecting to {@code host}
    public Authenticator newAuthenticator(InetSocketAddress host) throws AuthenticationException;
}
'''.lstrip()
        expected_output = {
            'text': u"See {@link PlainTextAuthProvider} for an implementation which uses SASL\nPLAIN mechanism to authenticate using username/password strings\n",
            'html': u"<p>See {@link PlainTextAuthProvider} for an implementation which uses SASL\nPLAIN mechanism to authenticate using username/password strings</p>"
        }

        lang = get_language("test.java", in_source, "java")
        result = parse("test.java", in_source, lang)
        self.assertEqual(len(result), 2,
                         "%s != %s\n%s" % (len(result), 2, result))
        self.assertEqual(result[0]['docs_text'], expected_output['text'])

        highlight('test.java', result, lang)
        self.assertEqual(result[0]['docs_html'], expected_output['html'])

