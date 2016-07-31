try:
    pycco_unichr = unichr
except NameError:
    pycco_unichr = chr


def compat_items(d):
    try:
        return d.iteritems()
    except AttributeError:
        return d.items()
