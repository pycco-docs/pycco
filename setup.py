from setuptools import setup

setup(name="Pycco",
      version="0.1.1",
      description="""A Python port of Docco: the original quick-and-dirty, hundred-line-long,
      literate-programming-style documentation generator.""",
      author="Nick Fitzgerald",
      author_email="fitzgen@gmail.com",
      url="http://fitzgen.github.com/pycco",
      packages=["pycco_resources"],
      scripts=["pycco"],
      install_requires = ['markdown', 'pygments', 'pystache'])
