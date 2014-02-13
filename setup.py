from setuptools import setup, find_packages

setup(
        name = "Pycco",
        version = "0.3.0",
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
        install_requires = ['markdown', 'pygments', 'pystache', 'smartypants'],
        extras_require = {'monitoring': 'watchdog'},
	data_files = [(os.path.join(sys.real_prefix, "share", "man", "man1"), 'pocco.1')]
        )
