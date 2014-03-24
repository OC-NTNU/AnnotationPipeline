# -*- coding: utf-8 -*-
"""
Superscript that calls on the other scrips and programs to transform DOIs to 
Brat-formatted files.

"""
from optparse import OptionParser
import os
import fetch_plos_papers

def run(doi_file):
    assert os.path.exists(doi_file), "The specified input file does not exist!"
    dois = [line.strip().split() for line in open(doi_file, 'r')]
    
    # Download all the DOIs
    for doi in dois:
        fetch_plos_papers.download_doi(doi, outfolder="PLOS")
    

if __name__=="__main__":
    optparser = OptionParser("Downloads papers with given DOIs from PLoS, and does all the preprocessing requried to annotate in Brat.")
    optparser.add_option("-i", "--doi", dest="doi_file", default=None, help="Input file - should contain all the DOIs to be downloaded on a separate line.")    
    (options, args) = optparser.parse_args()
    
    assert options.doi_file, "You must specify an input file!"
    
    run(options.doi_file)