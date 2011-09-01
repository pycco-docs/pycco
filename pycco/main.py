#!/usr/bin/env python

# "**Pycco**" is a Python port of [Docco](http://jashkenas.github.com/docco/ ):
# the original quick-and-dirty, hundred-line-long, literate-programming-style
# documentation generator. It produces HTML that displays your comments
# alongside your code. Comments are passed through
# [Markdown](http://daringfireball.net/projects/markdown/syntax) and
# [SmartyPants](http://daringfireball.net/projects/smartypants), while code is
# passed through [Pygments](http://pygments.org/) for syntax highlighting.
# This page is the result of running Pycco against its own source file.
#
# If you install Pycco, you can run it from the command-line:
#
#     pycco src/*.py
#
# This will generate linked HTML documentation for the named source files,
# saving it into a `docs` folder by default.
#
# To install Pycco, simply
#
#     pip install pycco
#
# Or, to install the latest source
#
#     git clone git://github.com/fitzgen/pycco.git
#     cd pycco
#     python setup.py install

# === Main Documentation Generation Functions ===

# Generate the documentation for a source file by reading it in, splitting it up
# into comment/code sections, highlighting them for the appropriate language,
# and merging them into an HTML template.
def generate_documentation(source, outdir=None, preserve_paths=True):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    fh = open(source, "r")
    sections = parse(source, fh.read())
    highlight(source, sections, preserve_paths=preserve_paths, outdir=outdir)
    return generate_html(source, sections, preserve_paths=preserve_paths, outdir=outdir)

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
        if docs and code:
            sections.append({
                "docs_text": docs,
                "code_text": code
            })

    # Setup the variables to get ready to check for multiline comments
    preformatted = multi_line = False
    last_scope = 0
    multi_line_delimiters = [language.get("multistart"), language.get("multiend")]

    for line in lines:

        # Only go into multiline comments section when one of the delimiters is
        # found to be at the start of a line
        if all(multi_line_delimiters) and any([line.lstrip().startswith(delim) for delim in multi_line_delimiters]):
            if not multi_line:
                multi_line = True

            else:
                multi_line = False

            # Get rid of the delimiters so that they aren't in the final docs
            line = re.sub(re.escape(language["multistart"]),'',line)
            line = re.sub(re.escape(language["multiend"]),'',line)
            docs_text += line.strip() + '\n'

            if has_code and docs_text.strip():
                save(docs_text, code_text[:-1])
                code_text = code_text.split('\n')[-1]
                last_scope = 0
                has_code = docs_text = ''

        elif multi_line:
            line_striped = line.rstrip()
            current_scope = line_striped.count("    ")

            # This section will parse if the line is indented at least four
            # places, and if so know to have the final text treat it as a
            # preformatted text block.
            if line_striped.startswith("    ") and last_scope:
                if current_scope > last_scope and not preformatted:
                    preformatted = True
                    docs_text += "<pre>"

            else:
                if preformatted:
                    preformatted = False
                    docs_text += "</pre>"

            # Keep a tracker var to see if the scope increases, that way later
            # the code can decided if a section is indented more than 4 spaces
            # from the leading code.
            last_scope = current_scope if current_scope > last_scope else last_scope
            docs_text += line.strip() + '\n'

        elif re.match(language["comment_matcher"], line):
            if has_code:
                save(docs_text, code_text)
                has_code = docs_text = code_text = ''
            docs_text += re.sub(language["comment_matcher"], "", line) + "\n"

        else:
            if code_text and any([line.lstrip().startswith(x) for x in ['class ', 'def ']]):
                save(docs_text, code_text)
                code_text = has_code = docs_text = ''

            has_code = True
            code_text += line + '\n'


    save(docs_text, code_text)
    return sections

# === Preprocessing the comments ===

# Add cross-references before having the text processed by markdown.  It's
# possible to reference another file, like this : `[[main.py]]` which renders
# [[main.py]]. You can also reference a specific section of another file, like
# this: `[[main.py#highlighting-the-source-code]]` which renders as
# [[main.py#highlighting-the-source-code]]. Sections have to be manually
# declared; they are written on a single line, and surrounded by equals signs:
# `=== like this ===`
def preprocess(comment, section_nr, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    def sanitize_section_name(name):
        return "-".join(name.lower().strip().split(" "))

    def replace_crossref(match):
        # Check if the match contains an anchor
        if '#' in match.group(1):
            name, anchor = match.group(1).split('#')
            return " [%s](%s#%s)" % (name,
                                     path.basename(destination(name,
                                                               preserve_paths=preserve_paths,
                                                               outdir=outdir)),
                                     anchor)

        else:
            return " [%s](%s)" % (match.group(1),
                                  path.basename(destination(match.group(1),
                                                            preserve_paths=preserve_paths,
                                                            outdir=outdir)))

    def replace_section_name(match):
        return '%(lvl)s <span id="%(id)s" href="%(id)s">%(name)s</span>' % {
            "lvl"  : re.sub('=', '#', match.group(1)),
            "id"   : sanitize_section_name(match.group(2)),
            "name" : match.group(2)
        }

    comment = re.sub('^([=]+)([^=]+)[=]*\\n', replace_section_name, comment)
    comment = re.sub('[^`]\[\[(.+)\]\]', replace_crossref, comment)

    return comment

# === Highlighting the source code ===

# Highlights a single chunk of code using the **Pygments** module, and runs the
# text of its corresponding comment through **Markdown**.
#
# We process the entire file in a single call to Pygments by inserting little
# marker comments between each section and then splitting the result string
# wherever our markers occur.
def highlight(source, sections, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
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
        section["docs_html"] = markdown(preprocess(docs_text,
                                                   i,
                                                   preserve_paths=preserve_paths,
                                                   outdir=outdir))
        section["num"] = i

# === HTML Code generation ===

# Once all of the code is finished highlighting, we can generate the HTML file
# and write out the documentation. Pass the completed sections into the template
# found in `resources/pycco.html`.
#
# Pystache will attempt to recursively render context variables, so we must
# replace any occurences of `{{`, which is valid in some languages, with a
# "unique enough" identifier before rendering, and then post-process the
# rendered template and change the identifier back to `{{`.
def generate_html(source, sections, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument")
    title = path.basename(source)
    dest = destination(source, preserve_paths=preserve_paths, outdir=outdir)

    for sect in sections:
        sect["code_html"] = re.sub(r"\{\{", r"__DOUBLE_OPEN_STACHE__", sect["code_html"])

    rendered = pycco_template({
        "title"       : title,
        "stylesheet"  : path.relpath(path.join(path.dirname(dest), "pycco.css"),
                                     path.split(dest)[0]),
        "sections"    : sections,
        "source"      : source,
        "path"        : path,
        "destination" : destination
    })

    return re.sub(r"__DOUBLE_OPEN_STACHE__", "{{", rendered).encode("utf-8")

# === Helpers & Setup ===

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

# A list of the languages that Pycco supports, mapping the file extension to
# the name of the Pygments lexer and the symbol that indicates a comment. To
# add another language to Pycco's repertoire, add it here.
languages = {
    ".coffee": { "name": "coffee-script", "symbol": "#" },

    ".pl":  { "name": "perl", "symbol": "#" },

    ".sql": { "name": "sql", "symbol": "--" },

    ".c":   { "name": "c", "symbol": "//"},

    ".cpp": { "name": "cpp", "symbol": "//"},

    ".js": { "name": "javascript", "symbol": "//",
        "multistart": "/\*", "multiend": "\*/"},

    ".rb": { "name": "ruby", "symbol": "#",
        "multistart": "=begin", "multiend": "=end"},

    ".py": { "name": "python", "symbol": "#",
        "multistart": '"""', "multiend": '"""' },

    ".scm": { "name": "scheme", "symbol": ";;",
        "multistart": "#\|", "multiend": "\|#"},

    ".lua": { "name": "lua", "symbol": "--",
        "multistart": "--[[", "mutliend": "--]]"},

    ".erl": { "name": "erlang", "symbol": "%%" },
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
def destination(filepath, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    try:
        name = filepath.replace(filepath[ filepath.rindex("."): ], "")
    except ValueError:
        name = filepath
    if not preserve_paths:
        name = path.basename(name)
    return path.join(outdir, "%s.html" % name)

# Shift items off the front of the `list` until it is empty, then return
# `default`.
def shift(list, default):
    try:
        return list.pop(0)
    except IndexError:
        return default

# Ensure that the destination directory exists.
def ensure_directory(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)

def template(source):
    return lambda context: pystache.render(source, context)

# Create the template that we will use to generate the Pycco HTML page.
pycco_template = template(pycco_resources.html)

# The CSS styles we'd like to apply to the documentation.
pycco_styles = pycco_resources.css

# The start of each Pygments highlight block.
highlight_start = "<div class=\"highlight\"><pre>"

# The end of each Pygments highlight block.
highlight_end = "</pre></div>"

# For each source file passed in as an argument, generate the documentation.
def process(sources, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")

    sources.sort()
    if sources:
        ensure_directory(outdir)
        css = open(path.join(outdir, "pycco.css"), "w")
        css.write(pycco_styles)
        css.close()

        def next_file():
            s = sources.pop(0)
            dest = destination(s, preserve_paths=preserve_paths, outdir=outdir)

            try:
                os.makedirs(path.split(dest)[0])
            except OSError:
                pass

            with open(destination(s, preserve_paths=preserve_paths, outdir=outdir), "w") as f:
                f.write(generate_documentation(s, outdir=outdir))

            print "pycco = %s -> %s" % (s, dest)

            if sources:
                next_file()
        next_file()

__all__ = ("process", "generate_documentation")

# Hook spot for the console script.
def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--paths', action='store_true',
                      help='Preserve path structure of original files')

    parser.add_option('-d', '--directory', action='store', type='string',
                      dest='outdir', default='docs',
                      help='The output directory that the rendered files should go to.')

    opts, sources = parser.parse_args()
    process(sources, outdir=opts.outdir, preserve_paths=opts.paths)

# Run the script.
if __name__ == "__main__":
    main()
