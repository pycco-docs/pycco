#!/usr/bin/env python 

import optparse
import os
from .output import process

# Hook spot for the console script.
def main():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--paths', action='store_true',
                      help='Preserve path structure of original files')

    parser.add_option('-d', '--directory', action='store', type='string',
                      dest='outdir', default='docs',
                      help='The output directory that the rendered files should go to.')

    opts, sources = parser.parse_args()
    process(sources, outdir=opts.outdir, preserve_paths=opts.paths)

# Run the script.
if __name__ == "__main__":
    main()
