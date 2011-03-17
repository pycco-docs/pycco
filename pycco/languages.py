import re


def single_line_multi_comment(ctx, code_before, comment, code_after):
    ctx.save_current_state()
    ctx.add_doc(comment)
    if code_before.strip() or code_after.strip():
        ctx.add_code(' '.join([code_before, ctx.language["multistart"], comment, ctx.language["multiend"], code_after]))

def multi_comment_start(ctx, code_before, comment):
    if ctx.multi_comment:
        return True #yield control to another matching function
    ctx.add_code(code_before)
    ctx.save_current_state()
    ctx.multi_comment = True
    ctx.add_doc(comment)
    
def match_all(ctx, text):
    if ctx.multi_comment:
        ctx.add_doc(text)
    else:
        ctx.add_code(text)
    
def multi_comment_end(ctx, comment, code_after):
    ctx.add_doc(comment)
    ctx.add_code(code_after)
    ctx.multi_comment = False
    
def single_line_comment(ctx, code_before, comment):
    if code_before.strip():
        # First case: there is code in the same line
        ctx.save_current_state()
        ctx.save_section(comment, code_before)
    elif ctx.code:
        # Second case: there has been code before this comment, open a new section
        ctx.save_current_state()
        ctx.add_doc(comment)
    else:
        # Third case, accumulate comments
        ctx.add_doc(comment)

single_line_multi_re = r'(?P<code_before>.*){multistart}(?P<comment>.*){multiend}(?P<code_after>.*)'
multi_comment_start_re = r'(?P<code_before>.*){multistart}(?P<comment>.*)'
multi_comment_end_re = r'(?P<comment>.*){multiend}(?P<code_after>.*)'
single_line_comment_re = r'(?P<code_before>.*){symbol}(?P<comment>.*)'
catch_all_re = r'(?P<text>.*)'

template_multi_matchers = [
    (single_line_multi_re, single_line_multi_comment),
    (multi_comment_start_re, multi_comment_start),
    (multi_comment_end_re, multi_comment_end),
]
template_symbol_matchers = [
    (single_line_comment_re, single_line_comment),
]
template_general_matchers = [
    (catch_all_re, match_all)
]

def sql_include_callback(ctx, once, filename):
    ctx.save_current_state()
    once = "" if not once else once
    ctx.add_code("/* include"+once+" "+filename+" */")
    ctx.add_doc("Including [{0}]({0}.html)".format(filename))
    ctx.save_current_state()

languages = {

    ".sql": { "name": "sql", 
              "symbol": "--", 
              "multistart": "/*", 
              "multiend": "*/", 
              "callbacks": [(r'/\* include(?P<once>_once)? "(?P<filename>.*)" \*/', sql_include_callback)],
             },
              
    ".llang": { "name": "c", 
                "symbol": "//", 
                "multistart": "/*", 
                "multiend": "*/",  },
                
                
    ".py": { "name": "python", "symbol": "#",
             "multistart": '"""', "multiend": '"""'},

}