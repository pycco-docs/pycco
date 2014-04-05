# A list of the languages that Pycco supports, mapping the file extension to
# the name of the Pygments lexer and the symbol that indicates a comment. To
# add another language to Pycco's repertoire, add it here.
DEFAULT_COMMENT_STYLES = {
    ".sh": {"name": "bash", "symbol": "#"},

    '.c': {'name': 'c', 'symbol': '//',
           'multistart': '/*', 'multiend': '*/'},

    '.cpp': {'name': 'cpp', 'symbol': '//',
             'multistart': '/*', 'multiend': '*/'},

    '.cs': {'name': 'csharp', 'symbol': '//',
            'multistart': '/// <summary>', 'multiend': '/// </summary>', 'multicont': '///'}

    '.coffee': {'name': 'coffee-script', 'symbol': '#',
                'multistart': '###', 'multiend': '###'},

    '.erl': {'name': 'erlang', 'symbol': '%%'},

    '.hs': {'name': 'haskell', 'symbol': '--',
            'multistart': '{-', 'multiend': '-}'},

    '.java': { 'name': 'java', 'symbol': '//',
               'multistart': '/*', 'multiend': '*/', 'multicont': ' *'},

    '.js': {'name': 'javascript', 'symbol': '//',
            'multistart': '/*', 'multiend': '*/'},

    '.lua': {'name': 'lua', 'symbol': '--',
             'multistart': '--[[', 'multiend': '--]]'},

    '.php': {'name': 'php', 'symbol': '//',
             'multistart': '/*', 'multiend': '*/'},

    '.pl': {'name': 'perl', 'symbol': '#'},

    '.py': {'name': 'python', 'symbol': '#',
            'multistart': '"""', 'multiend': '"""'},

    '.rb': {'name': 'ruby', 'symbol': '#',
            'multistart': '=begin', 'multiend': '=end'},

    '.scm': {'name': 'scheme', 'symbol': ';;',
             'multistart': '#|', 'multiend': '|#'},

    '.sql': {'name': 'sql', 'symbol': '--',
             'multistart': '/*', 'multiend': '*/'},  # https://github.com/fitzgen/pycco/pull/70

    '.tcl': {'name': 'tcl', 'symbol': '#'}

}
