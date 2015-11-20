try:
    pycco_unichr = unichr
except NameError:
    pycco_unichr = chr

import itertools
try:
    pycco_zip_longest = itertools.zip_longest
except AttributeError:
    import itertools
    pycco_zip_longest = itertools.izip_longest
