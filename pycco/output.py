import os
import re
from markdown import markdown
from pygments import lexers, formatters, highlight as pyg_highlight
import inspect

from .parsing import parse, get_language
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('pycco'))

def highlight(source, sections, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    language = get_language(source)
    
    divider_text = "\n" + language["symbol"] + "DIVIDER\n"
    divider_html = re.compile(r'\n*<span class="c[1]?">'+ language["symbol"] + 'DIVIDER</span>\n*')

    output = pyg_highlight(divider_text.join(section["code"] for section in sections),
                           lexers.get_lexer_by_name(language["lexer"]),
                           formatters.HtmlFormatter(nowrap=True))

    fragments = re.split(divider_html, output)
    for i, tp in enumerate(zip(sections, fragments)):
        section, fragment = tp
        section["code_html"] = "<div class='highlight'><pre>{0}</pre></div>".format(fragment)
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
        pass #dir already exists
        
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

def generate_html(source, sections, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument")
    title = os.path.basename(source)
    dest = destination(source, preserve_paths=preserve_paths, outdir=outdir)
    template = env.get_template('base.html')
    
    rendered = template.render(**{
        "title"       : title,
        "sections"    : sections,
        "source"      : source,
        "destination" : destination
    })

    return rendered
    
def generate_documentation(source, outdir=None, preserve_paths=True):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    code = open(source, "r").read()
    sections = parse(source, code)
    highlight(source, sections, preserve_paths=preserve_paths, outdir=outdir)
    return generate_html(source, sections, preserve_paths=preserve_paths, outdir=outdir)

from glob import glob
import shutil

def copy_static_css(outdir):
    for source in glob(os.path.join(os.path.dirname(__file__), "templates", "*.css")):
        print "pycco = %s -> %s" % (source, outdir)
        shutil.copy(source, outdir)

# For each source file passed in as an argument, generate the documentation.
def process(sources, preserve_paths=True, outdir=None):
    if not outdir:
        raise TypeError("Missing the required 'outdir' keyword argument.")
    ensure_directory(outdir)
    
    copy_static_css(outdir)
    for source in sources:
        dest = destination(source, preserve_paths=preserve_paths, outdir=outdir)
        ensure_directory(os.path.dirname(dest))
        with open(destination(source, preserve_paths=preserve_paths, outdir=outdir), "w") as f:
            f.write(generate_documentation(source, outdir=outdir))
            print "pycco = %s -> %s" % (source, dest)
