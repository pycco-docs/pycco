```
888888b.
888   Y88b
888    888
888   d88P  888  888   .d8888b  .d8888b  .d88b.
8888888P"   888  888  d88P"    d88P"    d88""88b
888         888  888  888      888      888  888
888         Y88b 888  Y88b.    Y88b.    Y88..88P
888          "Y88888   "Y8888P  "Y8888P  "Y88P"
                 888
            Y8b d88P
             "Y88P"
```

Pycco is a Python port of Docco: the original quick-and-dirty, hundred-line-
long, literate-programming-style documentation generator. For more information,
see: <http://fitzgen.github.com/pycco/>

Others:

* CoffeeScript (Original) - http://jashkenas.github.com/docco/
* Ruby - http://rtomayko.github.com/rocco/
* Sh - http://rtomayko.github.com/shocco/

* * * * *

This is a fork of [fitzgen's Pycco](https://github.com/fitzgen/pycco) that
fixes and adds a couple of new features:

1.  a way to invoke Pycco programmatically

    ```python
    from pycco.main import (register_comment_styles, generate_html)

    register_comment_styles()
    html = generate_html(source_path)
    ```

2.  provide additional comment styles:

    ```python
    from pycco.main import register_comment_styles

    register_comment_style({
        '.cql': {'name': 'cql', 'symbol': '//', 'multistart': '/*', 'multiend': '*/'}
    })
    ```

3.  supports continuation multi-line comment symbol.

    In C, C++, Java, etc. each block comment line can start with an special character, e.g.:

    ```java
    /**
     * This is just a normal javadoc.
     */
    ```

    To support this case, when defining a comment style, you can add a `multicont` symbol.

4.  supports providing a custom template by passing to `generate_documentation()` or
    `generate_html()` a `custom_template` parameter.
