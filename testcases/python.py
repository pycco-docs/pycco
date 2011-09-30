import datetime

# Comment 1
class Class(object):
    """Docstring 1"""
    def get(self):
        """Docstring 2"""
        # Comment 2 - pycco puts the function into the documntation not the code
        datum = datetime.date.today()
