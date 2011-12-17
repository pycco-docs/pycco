#!/usr/bin/env python
# encoding: utf-8

import sys
import os

def get_all_files( path, extension ):
    
    def relative( path ):
        relpath = os.path.relpath( path )
        if relpath == '.': 
            return ''
        else:
            return relpath + "/"
    
    for path, dirs, files in os.walk( path ):
        for filename in files:
            if filename.endswith( extension ):
                yield "%s%s" %( relative( path ), filename )



from os import path

class Source:    
    def __init__(self, name, start):
        self.name       = name
        self.title      = path.basename( self.name )
        self.dirpath    = path.dirname( self.name ) or '.'
        self.dirname    = path.relpath(self.dirpath, start)
    
    def save_path(self):
        return "docs/%s/%s" %( self.dirname, self.title )


class Sources:
    def __init__(self, sources, start):
        self.list = [ Source( name, start ) for name in sources ]
        self.get  = lambda x: self.list[ index ]

    def names(self):
        return [i.name for i in self.list]

    def __iter__(self):
        for i in self.list:
            yield i



