from setuptools import setup, find_packages

setup(
        name = "Pycco",
        version = "0.5.0",
        description = """A Python port of Docco: the original quick-and-dirty,
        hundred-line-long, literate-programming-style documentation generator.
        """,
        author = "Nick Fitzgerald",
        author_email = "fitzgen@gmail.com",
        maintainer = "Alex Popescu",
        maintainer_email = "alex@mypopescu.com",
        url = "http://github.com/al3xandru/pycco",
        packages = find_packages(),
        entry_points = {
            'console_scripts': [
                'pycco = pycco.main:main',
                ]
            },
        install_requires = ['markdown', 'pygments', 'pystache', 'smartypants'],
        extras_require = {'monitoring': 'watchdog'},
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Documentation',
            'Topic :: Text Processing',
            'Topic :: Text Processing :: Markup',
            'Topic :: Text Processing :: Markup :: HTML'
        ],
        )
