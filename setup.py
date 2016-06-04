from setuptools import setup, find_packages

setup(
    name="Pycco",
    version="0.5.1",
    description="""A Python port of Docco: the original quick-and-dirty,
        hundred-line-long, literate-programming-style documentation generator.
        """,
    author="Zach Smith",
    author_email="subsetpark@gmail.com",
    url="https://pycco-docs.github.io/pycco/",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pycco = pycco.main:main',
        ]
    },
    install_requires=['markdown', 'pygments', 'pystache', 'smartypants'],
    extras_require={'monitoring': 'watchdog'},
)
