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


