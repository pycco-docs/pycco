import re

def iscomment(line):
    """ Is this line a comment?

    >>> iscomment("if True:")
    False
    >>> iscomment("    # Checks if true")
    True
    """
    return not not re.match('^\s*#', line)


def indent_level(lines):
    """ What is the indentation level of this block?

    >>> lines = ['    hello', '    world', '        !', '']
    >>> indent_level(lines)
    4
    """
    clean = [line for line in lines if line.strip()]
    if not clean:
        return 0
    else:
        return min([len(re.match('^\s*', line).group()) for line in clean])


def unindent_lines(indent, lines):
    """ Unindent lines to base level

    >>> lines = ['    hello', '    world', '        !']
    >>> unindent_lines(4, lines)
    ['hello', 'world', '    !']
    """
    if not lines:
        return lines
    return [line[indent:] for line in lines]

def reindent_lines(lines):
    if not lines:
        return lines
    return unindent_lines(indent_level(lines), lines)


def indent_code_lines(lines):
    """

    >>> lines = ['Hello', '>>> x', '5', '6', '', 'World', '>>> y']
    >>> indent_code_lines(lines)
    ['Hello', '', '    >>> x', '    5', '    6', '', 'World', '', '    >>> y']
    """
    iscode = False
    out = []
    for line in lines:
        if re.match('^\s*>>>', line):
            if not iscode:
                out.append('')
                iscode = True
        elif not line.strip():
            iscode = False
        if iscode:
            out.append('    ' + line)
        else:
            out.append(line)
    return out


def remove_directives(line):
    """

    >>> line = "if True:  # doctest: +SKIP"
    >>> remove_directives(line)
    'if True:'
    """
    match = re.search('\s*#\s*doctest\s*:.*', line)
    if not match:
        return line
    return line[:-len(match.group())]


def process_docs(text):
    lines = text.split('\n')
    lines2 = reindent_lines(lines)
    lines3 = indent_code_lines(lines2)
    lines4 = list(map(remove_directives, lines3))
    return '\n'.join(lines4)

