from setuptools import setup, find_packages

setup(
        name = "Pycco",
        version = "git-11022010-1005",
        description = """A Python port of Docco: the original quick-and-dirty, 
        hundred-line-long, literate-programming-style documentation generator.
        """,
        author = "Nick Fitzgerald",
        author_email = "fitzgen@gmail.com",
        url = "http://fitzgen.github.com/pycco",
        packages = find_packages(),
        entry_points = {
            'console_scripts': [
                'pycco = pycco.main:main',
                ]
            },
        install_requires = ['markdown', 'pygments', 'pystache'],
        )
