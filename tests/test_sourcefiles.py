import codecs
import os
import unittest

from pycco.main import (register_comment_styles, get_language, parse, generate_html)


GEN_DEBUG_FILE = True  # set to False to avoid creating output *-debug.html files
SOURCE_DIR = 'examples'
SOURCES = ('cluster.py', 'Session.java', 'Cluster.cs', 'rocco.rb')


class CompleteSources(unittest.TestCase):
    def test_complete(self):
        for fname in SOURCES:
            try:
                self.compare_file(fname)
            except ValueError, verr:
                print 'ERROR: File type not supported:', fname, verr

    def compare_file(self, filename):
        register_comment_styles({
        })

        filepath = os.path.join(SOURCE_DIR, filename)

        in_source = codecs.open(filepath, 'rb+', 'utf8').read()
        lang = get_language(filepath, in_source)
        sections = parse(filepath, in_source, lang)
        for idx, s in enumerate(sections):
            s['num'] = idx
            s['code_html'] = r'%s' % (s['code_text'] or "''")
            s['docs_html'] = r'%s' % (s['docs_text'] or "''")

        out = generate_html(filepath, sections, outdir='/dev/null', custom_template=TEMPLATE)

        expected_out_file = os.path.join(SOURCE_DIR, filename + '.out')
        expected_out = codecs.open(expected_out_file, 'rb+', 'utf8').read()

        exp_lines = expected_out.splitlines()
        out_lines = out.splitlines()
        for idx, (el, al) in enumerate(zip(exp_lines, out_lines)):
            self.assertEqual(el, al,
                             "Output for %s differs at line %s\n'%r' != '%r'\nDebug file: %s" %
                             (filename, (idx + 1), el, al, debug_file(filepath, sections, out)))
        self.assertEqual(len(exp_lines), len(out_lines),
                         "Different number of lines (%s): expected %s != %s actual" %
                         (filename, len(exp_lines), len(out_lines)))

def debug_file(filepath, sections, out):
    if not GEN_DEBUG_FILE:
        return ''

    debug_fpath = filepath + '-debug.html'

    with open(debug_fpath, 'wb') as fout:
        fout.write(generate_html(filepath, sections, custom_template=HTML, outdir='/dev/null').encode('utf8'))
        fout.write("<div><pre>")
        fout.write("\n")
        fout.write(out.encode('utf8'))
        fout.write("\n")
        fout.write("</pre></div>")
        fout.write("</body></html>")
        fout.flush()

    return debug_fpath

TEMPLATE = u'''
{{#sections}}
Section {{ num }}: doc
{{ docs_html }}
Section {{ num }}: code
{{{ code_html }}}
{{/sections}}
'''

HTML = u'''
<!DOCTYPE html>
<html>
<head>
  <style type="text/css">
.codedoc {
    background: #ffffff;
}
.codedoc,
div.codesection {
    position: relative;
}
div.codesection {
    border-top: 1px #CCC dotted;
    padding-top: 1em;
}
.codebackground {
    position: absolute;
    left: 31%;
    top: 2em;
    right: 0;
    bottom: 0;
    background: #f5f5ff;
    border-left: 1px solid #e5e5ee;
    z-index: 0;
}
.codedoc .codebutton {
    float: right;
}
.codedoc .codebutton a {
    font-size: 0.8em;
    color: #073642;
}
.codedoc div.docs {
    float: left;
    max-width: 30%;
    min-width: 30%;
    min-height: 5px;
    padding: 0 1em 0 0;
    vertical-align: top;
    text-align: left;
}
    .codedoc div.docs p,
    .codedoc div.docs div,
    .codedoc div.docs pre {
        font-size: 14px;
        line-height: 1.3em;
    }
.codedoc .octowrap {
    position: relative;
  }
    .codedoc .octothorpe {
        color: #454545;
        position: absolute;
        top: 1em;
        left: -2em;
        padding: 0 1em;
        text-decoration: none;
        opacity: 0;
        -webkit-transition: opacity 0.2s linear;
    }
      .codedoc div.docs:hover .octothorpe {
        opacity: 1;
      }
.codedoc div.code {
  margin-left: 31%;
  padding: 1em 0;
  vertical-align: top;
}
.clearall {
    clear: both;
}
.codedoc div.docs pre,
.codedoc div.docs pre code {
    background-color: #ffffff;
    font-size: 12px;
    line-height: 1em;
}
.codedoc div.code pre,
.codedoc div.code pre code {
    background-color: #f5f5ff;
    font-size: 12px;
    line-height: 1.1em;
}
  </style>
</head>
<body>
<div class='codedoc'>
  <div class='codebackground'></div>
  <br class='clearall' />
  {{#sections}}
  <div class='codesection' id='section-{{ num }}'>
    <div class='docs'>
{{{ docs_html }}}
    </div>
    <div class='code'>
        <pre>
{{{ code_html }}}
        </pre>
    </div>
  </div>
  <br class='clearall' />
  {{/sections}}
</div>
'''
