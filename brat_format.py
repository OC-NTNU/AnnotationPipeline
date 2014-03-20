# -*- coding: utf-8 -*-
"""
Script to convert paper to Brat text format (i.e. no mark-up, each sentence on
its own line).

Currently defined for the PLoS format.
"""
from optparse import OptionParser
import xml.etree.ElementTree as ET

def convert_plos_to_brat():
    # Store the scopes of allthe interesting mark-up tags
    useful_tags = ['abstract', 'body']
    scopes = []
    with open("NXML/{0}.so".format(filename), 'r') as file:
        for line in file:
            line = line.strip().split()
            if line[1] in useful_tags:
                scopes.append( (line[1], int(line[2]), int(line[3])) )
    
    # Get the pure text format
    text = open("NXML/{0}.txt".format(filename), 'r').read()
    
    # Extract the boundaries for all sentences from the NLP document
    xml = ET.parse('NLP/{0}.xml'.format(filename))
    brat_txt = open('Brat/{0}.txt'.format(filename), 'w')
    for sentence in xml.iter('sentence'):
        startoffset = -1
        endoffset = -1
        for i, token in enumerate(sentence.iter('token')):
            if i == 0: startoffset = int(token.find('CharacterOffsetBegin').text)
            endoffset = int(token.find('CharacterOffsetEnd').text)
        # Store only sentences that are in the abstract or body
        tags = [scope[0] for scope in scopes if startoffset>=scope[1] and endoffset<=scope[2]]
        if 'abstract' in tags or 'body' in tags:
            brat_txt.write(text[startoffset:endoffset]+"\n")
    brat_txt.close()

if __name__ == "__main__":
    optparser = OptionParser(description="Script to convert parsed text to Brat format.")
    optparser.add_option("-f", "--filename", default=None, dest="filename", help="The filename of the file to be converted.")
    (options, args) = optparser.parse_args()
    
    global filename; filename= options.filename
    assert filename, "You must specify which file to convert!"
    
    convert_plos_to_brat()