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
    useful_tags = ['abstract', 'body', 'title', 'fig']
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
    brat_so_alignment = open('Brat/{0}.soa'.format(filename), 'w')
    
    for sentence in xml.iter('sentence'):
        startoffset = -1
        endoffset = -1
        sentence_text = []
        for i, token in enumerate(sentence.iter('token')):
            if i == 0: startoffset = int(token.find('CharacterOffsetBegin').text)
            endoffset = int(token.find('CharacterOffsetEnd').text)
            sentence_text.append(token.find('word').text)
        # Store only sentences that are in the abstract or body
        tags = [tag for tag, start, end in scopes if startoffset>=start and endoffset<=end]
        if ('abstract' in tags or 'body' in tags) and not 'fig' in tags:
            # Remove all parts of section titles from the sentence. Stanford NLP tends to mix these into sentences.
            # Assumes, as seems to be the case in CoreNLP, that titles are only attached to the start of sentences.
            for tag, start, end in scopes:
                if tag=="title" and startoffset<=start and endoffset>=end:
                    startoffset = end
            # Find the sentence from the pure text and store it. 
            sentence_text = text[startoffset:endoffset].strip()
            if sentence_text:
                brat_txt.write(sentence_text+"\n")
                brat_so_alignment.write(str(startoffset)+" "+str(endoffset)+"\n")
    brat_txt.close()

if __name__ == "__main__":
    optparser = OptionParser(description="Script to convert parsed text to Brat format.")
    optparser.add_option("-f", "--filename", default=None, dest="filename", help="The filename of the file to be converted.")
    (options, args) = optparser.parse_args()
    
    global filename; filename= options.filename
    assert filename, "You must specify which file to convert!"
    
    convert_plos_to_brat()