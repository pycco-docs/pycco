import os
import re
from markdown import markdown
from pygments import lexers, formatters
import pycco_resources
import inspect

from .parsing import parse, get_language

import pygments
import pystache

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


def highlight(source, sections, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    language = get_language(source)
    
    divider_text = "\n" + language["symbol"] + "DIVIDER\n"
    divider_html = re.compile(r'\n*<span class="c[1]?">'+ language["symbol"] + 'DIVIDER</span>\n*')

    output = pygments.highlight(divider_text.join(section["code"] for section in sections),
                                lexers.get_lexer_by_name(language["name"]),
                                formatters.get_formatter_by_name("html"))

    output = output.replace(highlight_start, "").replace(highlight_end, "")
    fragments = re.split(divider_html, output)
    for i, tp in enumerate(zip(sections, fragments)):
        section, fragment = tp
        section["code_html"] = highlight_start + fragment + highlight_end
        try:
            docs_text = unicode(section["doc"])
        except UnicodeError:
            docs_text = unicode(section["doc"].decode('utf-8'))

        section["docs_html"] = markdown(inspect.cleandoc(docs_text))
        section["num"] = i

# Ensure that the destination directory exists.
def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError:
        print "pycco => Dir already exists"

# Compute the destination HTML path for an input source file path. If the source
# is `lib/example.py`, the HTML will be at `docs/example.html`
def destination(filepath, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword ")
    name = filepath
    if not preserve_paths:
        name = os.path.basename(name)
    return os.path.join(outdir, "%s.html" % name)


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
    title = os.path.basename(source)
    dest = destination(source, preserve_paths=preserve_paths, outdir=outdir)

    for sect in sections:
        if "code_html" in sect:
            sect["code_html"] = re.sub(r"\{\{", r"__DOUBLE_OPEN_STACHE__", sect["code_html"])

    rendered = pycco_template({
        "title"       : title,
        "stylesheet"  : os.path.relpath(os.path.join(os.path.dirname(dest), "pycco.css"),
                                     os.path.split(dest)[0]),
        "sections"    : sections,
        "source"      : source,
        "path"        : os.path,
        "destination" : destination
    })

    return re.sub(r"__DOUBLE_OPEN_STACHE__", "{{", rendered).encode("utf-8")
    
def generate_documentation(source, outdir=None, preserve_paths=True):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    fh = open(source, "r")
    sections = parse(source, fh.read())
    highlight(source, sections, preserve_paths=preserve_paths, outdir=outdir)
    return generate_html(source, sections, preserve_paths=preserve_paths, outdir=outdir)
    
# For each source file passed in as an argument, generate the documentation.
def process(sources, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    ensure_directory(outdir)
    css = open(os.path.join(outdir, "pycco.css"), "w")
    css.write(pycco_styles)
    css.close()
    
    for source in sources:
        dest = destination(source, preserve_paths=preserve_paths, outdir=outdir)
        ensure_directory(os.path.dirname(dest))
        with open(destination(source, preserve_paths=preserve_paths, outdir=outdir), "w") as f:
            f.write(generate_documentation(source, outdir=outdir))
            print "pycco = %s -> %s" % (source, dest)
