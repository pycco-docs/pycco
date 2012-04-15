import sys
import os


def get_all_files(path, extension):
    def relative(path):
        relpath = os.path.relpath(path)
        if relpath == '.':
            return ''
        else:
            return relpath + "/"

    for path, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(extension):
                yield "%s%s" % (relative(path), filename)


class Source:
    def __init__(self, name, start):
        self.name       = name
        self.title      = os.path.basename(self.name)
        self.dirpath    = os.path.dirname(self.name) or '.'
        self.dirname    = os.path.relpath(self.dirpath, start)
        self.start      = start

    def save_path(self):
        return "docs/%s/%s" % (self.dirname, self.title)

    def relative_path(self, source):
        html = lambda x: "%s.html" % os.path.splitext(x)[0]
        rel  = os.path.relpath(source.dirpath, self.dirpath)
        return "%s/%s" % (rel, html(source.title))

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def relative_paths(self, sources):
        root_ = ''
        list_ = []
        dict_ = {}
        id_ = 1
        title    = lambda s: {'title': s.title, 'url': self.relative_path(s)}
        new_dict = lambda s: {'id': id_, 'dirname': s.dirname, 'display': 'none', 'titles': [title(s)]}

        for source in sources:
            if source.dirpath != root_:
                if dict_:
                    list_.append(dict_)
                root_  = source.dirpath
                dict_  = new_dict(source)
                id_   += 1
            else:
                dict_['titles'].append(title(source))

        list_.append(dict_)
        if len(list_) == 1:
            list_[0]['display'] = 'block'
        return list_
