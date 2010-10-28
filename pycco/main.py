#!/usr/bin/env python

# **Pycco** is a Python port of [Docco](http://jashkenas.github.com/docco/ ):
# the original quick-and-dirty, hundred-line-long, literate-programming-style
# documentation generator. It produces HTML that displays your comments
# alongside your code. Comments are passed through
# [Markdown](http://daringfireball.net/projects/markdown/syntax), and code is
# passed through [Pygments](http://pygments.org/) syntax highlighting.  This
# page is the result of running Pycco against its own source file.
#
# If you install Pycco, you can run it from the command-line:
#
#     pycco src/*.py
#
# ...will generate linked HTML documentation for the named source files, saving
# it into a `docs` folder.
#
# To install Pycco, simply
#
#     sudo setup.py install
#

#### Main Documentation Generation Functions

# Generate the documentation for a source file by reading it in, splitting it
# up into comment/code sections, highlighting them for the appropriate language,
# and merging them into an HTML template.
def generate_documentation(source, options):
    fh = open(source, "r")
    sections = parse(source, fh.read())
    highlight(source,
              sections)
    generate_html(source, sections, options=options)

# Given a string of source code, parse out each comment and the code that
# follows it, and create an individual **section** for it.
# Sections take the form:
#
#     { "docs_text": ...,
#       "docs_html": ...,
#       "code_text": ...,
#       "code_html": ...,
#       "num":       ...
#     }
#
def parse(source, code):
    lines = code.split("\n")
    sections = []
    language = get_language(source)
    has_code = docs_text = code_text = ""

    if lines[0].startswith("#!"):
        lines.pop(0)

    if language["name"] == "python":
        for linenum, line in enumerate(lines[:2]):
            if re.search(r'coding[:=]\s*([-\w.]+)', lines[linenum]):
                lines.pop(linenum)
                break


    def save(docs, code):
        sections.append({
            "docs_text": docs,
            "code_text": code
        })

    multi_line = False
    multi_line_delimeters = ['"""', "'''"]
    for line in lines:

        if any([delim in line.strip() for delim in multi_line_delimeters]):
            if not multi_line:
                multi_line = True

            else:
                multi_line = False

            line = re.sub('"""','',line)
            line = re.sub("'''",'',line)
            docs_text += line.strip() + '\n'
            
            save(docs_text, code_text)
            code_text = has_code = docs_text = ''

        elif multi_line:
            docs_text += line.strip() + '\n'

        elif re.match(language["comment_matcher"], line):
            if has_code:
                save(docs_text, code_text)
                has_code = docs_text = code_text = ''
            docs_text += re.sub(language["comment_matcher"], "", line) + "\n"

        else:
            if docs_text:
                save(docs_text, code_text)
                code_text = has_code = docs_text = ''

            has_code = True
            code_text += line + '\n'


    save(docs_text, code_text)
    return sections

# === Preprocessing the comments ===
#
# Add cross-references before having the text processed by markdown.
# It's possible to reference another file, like this : [[pycco.py]] or a specific section of
# another file, like this: [[pycco.py#Highlighting]]. Of course, sections have to be manually declared before,
# A section name is written on a single line, and surrounded by equals signs, === like this ===
def preprocess(comment, section_nr):
	def sanitize_section_name(name):
		return name.strip().split(" ")[0]

	def replace_crossref(match):
		# Check if the match contains an anchor
		if '#' in match.group(1):
			name, anchor = match.group(1).split('#')
			return "[%s](%s#%s)" % (name, path.basename(destination(name)), anchor)

		else:
			return "[%s](%s)" % (match.group(1), path.basename(destination(match.group(1))))

	def replace_section_name(match):
		return '<a name="%s">*%s*</a>' % (sanitize_section_name(match.group(1)), match.group(1))

	comment = re.sub('===(.+)===\\n', replace_section_name, comment)
	comment = re.sub('\[\[(.+)\]\]', replace_crossref, comment)

	return comment

# === Highlighting the source code ===
#
# Highlights a single chunk of code using the **Pygments** module, and runs the
# text of its corresponding comment through **Markdown**.
#
# We process the entire file in a single call to Pygments by inserting little
# marker comments between each section and then splitting the result string
# wherever our markers occur.
def highlight(source, sections):
    language = get_language(source)

    output = pygments.highlight(language["divider_text"].join(section["code_text"] for section in sections),
                                language["lexer"],
                                formatters.get_formatter_by_name("html"))

    output = output.replace(highlight_start, "").replace(highlight_end, "")
    fragments = re.split(language["divider_html"], output)
    for i, section in enumerate(sections):
        section["code_html"] = highlight_start + shift(fragments, "") + highlight_end
        try:
            docs_text = unicode(section["docs_text"])
        except UnicodeError:
            docs_text = unicode(section["docs_text"].decode('utf-8'))
        section["docs_html"] = markdown(preprocess(docs_text, i))
        section["num"] = i

# === HTML Code generation ===
# Once all of the code is finished highlighting, we can generate the HTML file
# and write out the documentation. Pass the completed sections into the template
# found in `resources/pycco.html`
def generate_html(source, sections, options):
    title = path.basename(source)
    dest = destination(source, preserve_paths=options.paths)
    html = pycco_template({
        "title":       title,
        "stylesheet":  path.relpath('docs/pycco.css', path.split(dest)[0]),
        "sections":    sections,
        "source":     source,
        "path":        path,
        "destination": destination
    })
    print "pycco = %s -> %s" % (source, dest)
    try:
        os.makedirs(path.split(dest)[0])
    except OSError:
        pass
    fh = open(dest, "w")
    fh.write(html.encode(getpreferredencoding()))
    fh.close()

#### Helpers & Setup

# This module contains all of our static resources.
import pycco_resources

# Import our external dependencies.
import optparse
import os
import pygments
import pystache
import re
import sys
from markdown import markdown
from os import path
from pygments import lexers, formatters
from subprocess import Popen, PIPE
from locale import getpreferredencoding

# A list of the languages that Pycco supports, mapping the file extension to
# the name of the Pygments lexer and the symbol that indicates a comment. To
# add another language to Pycco's repertoire, add it here.
languages = {
#    ".coffee": { "name": "coffee-script", "symbol": "#" },
    ".js":     { "name": "javascript",    "symbol": "//" },
    ".rb":     { "name": "ruby",          "symbol": "#" },
    ".py":     { "name": "python",        "symbol": "#" },
    ".scm":    { "name": "scheme",        "symbol": ";;" },
    ".lua":    { "name": "lua",           "symbol": "--" },
}

# Build out the appropriate matchers and delimiters for each language.
for ext, l in languages.items():
    # Does the line begin with a comment?
    l["comment_matcher"] = re.compile(r"^\s*" + l["symbol"] + "\s?")

    # The dividing token we feed into Pygments, to delimit the boundaries between
    # sections.
    l["divider_text"] = "\n" + l["symbol"] + "DIVIDER\n"

    # The mirror of `divider_text` that we expect Pygments to return. We can split
    # on this to recover the original sections.
    l["divider_html"] = re.compile(r'\n*<span class="c[1]?">' + l["symbol"] + 'DIVIDER</span>\n*')

    # Get the Pygments Lexer for this language.
    l["lexer"] = lexers.get_lexer_by_name(l["name"])

# Get the current language we're documenting, based on the extension.
def get_language(source):
    try:
        return languages[ source[source.rindex("."):] ]
    except ValueError:
        source = open(source, "r")
        code = source.read()
        source.close()
        lang = lexers.guess_lexer(code).name.lower()
        for l in languages.values():
            if l["name"] == lang:
                return l
        else:
            raise ValueError("Can't figure out the language!")

# Compute the destination HTML path for an input source file path. If the source
# is `lib/example.py`, the HTML will be at `docs/example.html`
def destination(filepath, preserve_paths=False):
    try:
        name = filepath.replace(filepath[ filepath.rindex("."): ], "")
    except ValueError:
        name = filepath
    if not preserve_paths:
        name = path.basename(name)
    return "docs/%s.html" % name

# Shift items off the front of the `list` until it is empty, then return
# `default`.
def shift(list, default):
    try:
        return list.pop(0)
    except IndexError:
        return default

# Ensure that the destination directory exists.
def ensure_directory():
    if not os.path.isdir("docs"):
        os.mkdir("docs")

def template(source):
    return lambda context: pystache.render(source, context)

# Create the template that we will use to generate the Pycco HTML page.
pycco_template = template(pycco_resources.html)

# The CSS styles we"d like to apply to the documentation.
pycco_styles = pycco_resources.css

# The start of each Pygments highlight block.
highlight_start = "<div class=\"highlight\"><pre>"

# The end of each Pygments highlight block.
highlight_end = "</pre></div>"

# The bulk of the work is done here
# For each source file passed in as an argument, generate the documentation.
def process(sources, options=None):
    sources.sort()
    if sources:
        ensure_directory()
        css = open("docs/pycco.css", "w")
        css.write(pycco_styles)
        css.close()

        def next_file():
            generate_documentation(sources.pop(0), options)
            if sources:
                next_file()
        next_file()


# Hook spot for the console script
def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--paths', action='store_true',
                      help='Preserve path structure of original files')

    opts, sources = parser.parse_args()
    process(sources, opts)

# Run the script.
if __name__ == "__main__":
    main()
 
