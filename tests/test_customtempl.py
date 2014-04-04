import unittest

from pycco.main import generate_html

class CustomTemplateTest(unittest.TestCase):
    def test_custom_template(self):
        custom_template = u"""<h1>Just the {{ title }}</h1>"""
        out = generate_html('empty.py', [], outdir='/dev/null', custom_template=custom_template)
        self.assertEqual(u"""<h1>Just the empty.py</h1>""", out)
