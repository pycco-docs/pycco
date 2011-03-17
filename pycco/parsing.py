import re
import inspect

class LexerContext(object):
    def __init__(self, language):
        self.multi_comment = False
        self.sections = []
        self.doc = ""
        self.code = ""
        self.language = language
    
    def add_code(self, code):
        self.code += code.rstrip() + "\n"
    
    def add_doc(self, doc):
        self.doc += doc.rstrip() + "\n"        
    
    def save_current_state(self):
        """
        Creates a new section from the current state, when there is something
        to save
        """
        if self.doc or self.code:
            self.save_section(self.doc.strip(), self.code)
    
    def save_section(self, doc_text, code_text):
        self.sections.append({"code": code_text, "doc": doc_text})
        self.doc = ""
        self.code = ""


from .languages import languages, template_general_matchers, template_symbol_matchers, template_multi_matchers

def get_language(source):
    return languages[source[source.rindex("."):]]

def get_matchers_for_language(source):
    """
    Construct matchers for a specific language in the following order:
    
    1. Custom language callbacks go in first
    2. Generic callbacks for multiline operators
    3. Generic callback for single line operator
    4. Generic catch all
    """
    language = get_language(source)
    matchers = []
    symbols = dict((key, re.escape(language[key])) for key in ['multistart', 'multiend', 'symbol'] if key in language)    
    if 'callbacks' in language:
        for exp, function in language['callbacks']:
            matchers.append((exp.format(**symbols), function))
    if 'multistart' in language and 'multiend' in language:
        for exp, function in template_multi_matchers:
            matchers.append((exp.format(**symbols), function))
    if 'symbol' in language:
        for exp, function in template_symbol_matchers:
            matchers.append((exp.format(**symbols), function))
    matchers.extend(template_general_matchers)
    return matchers
    

def parse(source, lines):
    """
    Parse the source file line by line using matcher regex to find comments.
    
    Furthermore,
    """
    language = get_language(source)
    ctx = LexerContext(language)
    matchers = get_matchers_for_language(source)
    for line in lines.split('\n'):
        ctx.current_line = line
        for expression, func in matchers:
            result = re.match(expression, line)
            if result:
                if func(ctx, *result.groups()) is None:
                    break
        if not result:
            print line, "not matched"
    ctx.save_current_state()
    return ctx.sections
