# -*- coding: utf-8 -*-
"""
Script for downloading papers from PLoS, either the paper with a given DOI, or
all papers that are returned when making an all-fields query with a keyword.
"""
from optparse import OptionParser
import httplib2
import re
import os

def get_fetch_url(id):
    return 'http://www.plosone.org/article/fetchObject.action?uri=info:doi/{0}&representation=XML'.format(id)
def get_api_url(query):
    return 'http://api.plos.org/search?q="{0}"&api_key=rc-hmLyPpmyMdfHcDhQv'.format('+'.join(query.split()).strip('+'))

def doi_to_filename(doi):
    return re.sub("[^0-9A-Za-z+]", "", doi)

def download_doi(doi, outfolder="PLOS"):
    """
        Download paper with given DOI from PLoS.
        
        @param doi: The DOI of the paper to download.
        @param outfolder: The folder to download the paper into.
    """
    filename = outfolder + "/" + doi_to_filename(doi)+".xml"
    if os.path.exists(filename):
        print "A paper DOI " + str(doi) + " has been downloaded earlier. Not downloading it..."
    else:
        h = httplib2.Http()
        (resp_header, xml) = h.request(get_fetch_url(doi), "GET")
        with open(filename, 'w') as file:
            file.write(xml)

def download_query(query, outfolder="PLOS"):
    """
        Download all papers returned with a keyword search from from PLoS.
        
        @param query: The keyword(s) to search PLoS for.
        @param outfolder: The folder to download the papers into.
    """
    url = get_api_url(query)

    h = httplib2.Http()
    (resp_headers, content) = h.request(url, "GET")

    # This should extract all the IDs in the returned XML.
    for i, match in enumerate(re.finditer(r'<str name="id">(.*?)</str>', content)):
        id = match.group(1)
        (resp_header, xml) = h.request(get_fetch_url(id), "GET")
        with open(outfolder + "/" + str(i) + ".xml", 'w') as file:
            file.write(xml)
        
if __name__=="__main__":
    optparser = OptionParser(description="Script to download full-text papers from PLoS.")
    optparser.add_option("--doi", default=None, dest="doi", help="Download paper from PLoS with the given ID.")
    optparser.add_option("--keyword", default=None, dest="keyword", help="Download all papers returned when querying PLoS with given keyword.")
    optparser.add_option("--outfolder", default="PLOS", dest="outfolder", help="Output folder for the downloaded papers.")
    (options, args) = optparser.parse_args()
    
    if options.doi == None and options.keyword == None:
        print "Please specify either a DOI or a keyword to download."
    elif options.doi != None and options.keyword != None:
        print "Please either specify a DOI to a keyword, not both."
    elif options.doi == None and options.keyword != None:
        download_query(options.keyword, outfolder=options.outfolder)
    elif options.doi != None and options.keyword == None:
        download_doi(options.doi, outfolder=options.outfolder)