# -*- coding: utf-8 -*-
"""
Script to transform double newlines to single newlines. To be used after manual
fixing of sentence splitting errors.
"""
import re
from optparse import OptionParser

def remove_double_newlines(filename, outfile):
    with open(filename, 'r') as file:
        text = re.sub('\n\n', '\n', file.read())
    
    if not outfile: outfile = filename
    
    with open(outfile, 'w') as file:
        file.write(text)
    

if __name__=="__main__":
    optparser = OptionParser(description="Script to reduce double newlines to single newline characters.")

    optparser.add_option("-f", "--file", default=None, dest="filename", help="Name of the file to convert.")
    optparser.add_option("-o", "--output", default=None, dest="outfile", help="Name of file to output the convertion, if different from input file.")
    (options, args) = optparser.parse_args()

    assert options.filename, "You need to specify a file to convert!"    
    
    remove_double_newlines(options.filename, options.outfile)
