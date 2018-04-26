"""
A list of the languages that Pycco supports, mapping the file extension to
the name of the Pygments lexer and the symbol that indicates a comment. To
add another language to Pycco's repertoire, add it here.
"""

__all__ = ("supported_languages",)

HASH = "#"
SLASH_STAR = "/*"
STAR_SLASH = "*/"
SLASH_SLASH = "//"
DASH_DASH = "--"
TRIPLE_QUOTE = '"""'

def lang(name, comment_symbol, multistart=None, multiend=None):
    """
    Generate a language entry dictionary, given a name and comment symbol and
    optional start/end strings for multiline comments.
    """
    result = {
        "name": name,
        "comment_symbol": comment_symbol
    }
    if multistart is not None and multiend is not None:
        result.update(multistart=multistart, multiend=multiend)
    return result


c_lang = lang("c", SLASH_SLASH, SLASH_STAR, STAR_SLASH)

supported_languages = {
    ".coffee": lang("coffee-script", HASH, "###", "###"),

    ".pl": lang("perl", HASH),

    ".sql": lang("sql", DASH_DASH, SLASH_STAR, STAR_SLASH),

    ".sh": lang("bash", HASH),

    ".c": c_lang,

    ".h": c_lang,

    ".cl": c_lang,

    ".cpp": lang("cpp", SLASH_SLASH),

    ".js": lang("javascript", SLASH_SLASH, SLASH_STAR, STAR_SLASH),

    ".rb": lang("ruby", HASH, "=begin", "=end"),

    ".py": lang("python", HASH, TRIPLE_QUOTE, TRIPLE_QUOTE),

    ".pyx": lang("cython", HASH, TRIPLE_QUOTE, TRIPLE_QUOTE),

    ".scm": lang("scheme", ";;", "#|", "|#"),

    ".lua": lang("lua", DASH_DASH, "--[[", "--]]"),

    ".erl": lang("erlang", "%%"),

    ".tcl": lang("tcl", HASH),

    ".hs": lang("haskell", DASH_DASH, "{-", "-}"),
}
