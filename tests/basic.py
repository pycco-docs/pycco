#!/usr/bin/env python
# encoding: utf-8

# basic.py
#
# Created by Sebastian Hillig on 2011-03-21.
# Copyright (c) 2011 SAP AG. All rights reserved.

import sys
import os


def main():
    """
    A docstring for the main method
        
        Containing some indented text
    
    More text
    """
    print "While the above was obviously a docstring"
    print """This one is not"""
    print """
    As is isn't this one
    """
    for i in range(10000):
        # do some stuff,
        # for a few lines,
        # meaningless though,
        # as these lines are collapsed into a multiline like comment
        print i
        if i > 10:
            print i**i


if __name__ == '__main__':
    # Call main!
    main()

