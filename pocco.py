# **Pocco** is a Python port of [Docco](http://jashkenas.github.com/docco/ ):
# the original quick-and-dirty, hundred-line-long, literate-programming-style
# documentation generator. It produces HTML that displays your comments
# alongside your code. Comments are passed through
# [Markdown](http://daringfireball.net/projects/markdown/syntax), and code is
# passed through [Pygments](http://pygments.org/) syntax highlighting.  This
# page is the result of running Pocco against its own source file.
#
# If you install Pocco, you can run it from the command-line:
#
#     pocco src/*.py
#
# ...will generate linked HTML documentation for the named source files, saving
# it into a `docs` folder.
#
# To install Pocco, simply
#
#     sudo setup.py install
#

#### Main Documentation Generation Functions

# Generate the documentation for a source file by reading it in, splitting it
# up into comment/code sections, highlighting them for the appropriate language,
# and merging them into an HTML template.
def generate_documentation(source):
    fh = open(source, "r")
    sections = parse(source, fh.read())
    highlight(source,
              sections)
    generate_html(source, sections)

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

    def save(docs, code):
        sections.append({
            "docs_text": docs,
            "code_text": code
        })

    for line in lines:
        if re.match(language["comment_matcher"], line):
            if has_code:
                save(docs_text, code_text)
                has_code = docs_text = code_text = ''
            docs_text += re.sub(language["comment_matcher"], "", line) + "\n"
        else:
            has_code = True
            code_text += line + '\n'
    save(docs_text, code_text)
    return sections

# Highlights a single chunk of code, using **Pygments** over stdio, and runs the
# text of its corresponding comment through **Markdown**.
#
# We process the entire file in a single call to Pygments by inserting little
# marker comments between each section and then splitting the result string
# wherever our markers occur.
def highlight(source, sections):
    language = get_language(source)
    pygments = Popen(["pygmentize", "-l", language["name"], "-f", "html"],
                     stderr=PIPE,
                     stdin=PIPE,
                     stdout=PIPE)

    pygments.stdin.write(language["divider_text"].join(section["code_text"] for section in sections))
    output = ""
    while pygments.returncode is None:
        stdout, stderr = pygments.communicate()
        if stderr:
            print stderr
        if stdout:
            output += stdout

    output = output.replace(highlight_start, "").replace(highlight_end, "")
    fragments = re.split(language["divider_html"], output)
    for i, section in enumerate(sections):
        section["code_html"] = highlight_start + fragments[i] + highlight_end
        section["docs_html"] = markdown(section["docs_text"])
        section["num"] = i

# Once all of the code is finished highlighting, we can generate the HTML file
# and write out the documentation. Pass the completed sections into the template
# found in `resources/pocco.jst`
def generate_html(source, sections):
    title = path.basename(source)
    dest = destination(source)
    html = pocco_template({
        "title":       title,
        "sections":    sections,
        "sources":     sources,
        "path":        path,
        "destination": destination
    })
    print "pocco = %s -> %s" % (source, dest)
    fh = open(dest, "w")
    fh.write(html)
    fh.close()

#### Helpers & Setup

# Import our external dependencies.
import pystache
import re
import sys
from markdown import markdown
from os import path
from subprocess import Popen, PIPE

# A list of the languages that Pocco supports, mapping the file extension to
# the name of the Pygments lexer and the symbol that indicates a comment. To
# add another language to Pocco's repertoire, add it here.
languages = {
    ".coffee": { "name": "coffee-script", "symbol": "#" },
    ".js":     { "name": "javascript",    "symbol": "//" },
    ".rb":     { "name": "ruby",          "symbol": "#" },
    ".py":     { "name": "python",        "symbol": "#" }
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
    l["divider_html"] = re.compile(r'\n*<span class="c">' + l["symbol"] + 'DIVIDER</span>\n*')

# Get the current language we're documenting, based on the extension.
def get_language(source):
    return languages[ source[source.rindex("."):] ]

# Compute the destination HTML path for an input source file path. If the source
# is `lib/example.coffee`, the HTML will be at `docs/example.html`
def destination(filepath):
    name = filepath.replace(filepath[ filepath.rindex("."): ], "")
    return "docs/" + path.basename(name) + ".html"

# Ensure that the destination directory exists.
def ensure_directory():
    Popen(["mkdir", "-p", "docs"]).wait()

def template(source):
    return lambda context: pystache.render(source, context)

# Create the template that we will use to generate the Pocco HTML page.
pocco_template = template(open(path.dirname(__file__) + "/resources/pocco.html").read())

# The CSS styles we"d like to apply to the documentation.
pocco_styles = open(path.dirname(__file__) + "/resources/pocco.css").read()

# The start of each Pygments highlight block.
highlight_start = "<div class=\"highlight\"><pre>"

# The end of each Pygments highlight block.
highlight_end = "</pre></div>"

# Run the script.
# For each source file passed in as an argument, generate the documentation.
if __name__ == "__main__":
    sources = list(sys.argv)
    sources.sort()
    if sources:
        ensure_directory()
        css = open("docs/pocco.css", "w")
        css.write(pocco_styles)
        css.close()

        def next_file():
            generate_documentation(sources.pop(0))
            if sources:
                next_file()
        next_file()
