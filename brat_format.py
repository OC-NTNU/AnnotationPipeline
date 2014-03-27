# -*- coding: utf-8 -*-
"""
Script to convert paper to Brat text format (i.e. no mark-up, each sentence on
its own line).

Currently defined for PLoS format -> Brat format only.
"""
from optparse import OptionParser
import xml.etree.ElementTree as ET
import os

def convert_plos_to_brat(filename, txtfolder="TXT", sofolder="SO", bratfolder="Brat", corenlpfolder="CoreNLP"):
    """
        Converts a single file to Brat format, assuming it has already been preprocessed by NXML2TXT and Stanford CoreNLP.
    """
    if not os.path.isdir(bratfolder): os.mkdir(bratfolder)
    
    # Store the scopes of allthe interesting mark-up tags
    useful_tags = ['abstract', 'body', 'title', 'fig', 'supplementary-material', 'table-wrap']
    scopes = []
    with open(os.path.join(sofolder, filename+'.so'), 'r') as file:
        for line in file:
            line = line.strip().split()
            if line[1] in useful_tags:
                scopes.append( (line[1], int(line[2]), int(line[3])) )
    
    # Get the pure text format
    text = open(os.path.join(txtfolder, filename+".txt"), 'r').read()

    # Extract the boundaries for all sentences from the NLP document
    xml = ET.parse(os.path.join(corenlpfolder, filename+".xml"))

    # Create the required files, including an empty dummy .ann file    
    brat_txt = open(os.path.join(bratfolder, filename+'.txt'), 'w')
    brat_so_alignment = open(os.path.join(bratfolder, filename+'.soa'), 'w')
    open(os.path.join(bratfolder, filename+'.ann'), 'w')
    
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
        if ('abstract' in tags or 'body' in tags) and not 'fig' in tags and not 'supplementary-material' in tags and not 'table-wrap' in tags:
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
    brat_so_alignment.close()

if __name__ == "__main__":
    optparser = OptionParser(description="Script to convert parsed text to Brat format.")
    optparser.add_option("-f", "--filename", default=None, dest="filename", help="The filename of the file to be converted.")
    optparser.add_option("-t", "--txtfolder", default="TXT", dest="txtfolder", help="Name of the folder that contains the .txt files output by NXML2TXT.")
    optparser.add_option("-s", "--sofolder", default="SO", dest="sofolder", help="Name of the folder that contains the .so files output by NXML2TXT.")
    optparser.add_option("-c", "--corenlpfolder", default="CoreNLP", dest="corenlpfolder", help="Name of the folder that contains the .xml files output by Stanford CoreNLP.")
    optparser.add_option("-b", "--bratfolder", default="Brat", dest="bratfolder", help="Output folder.")
    (options, args) = optparser.parse_args()
    
    filename = options.filename
    assert filename, "You must specify which file to convert!"
    
    convert_plos_to_brat(filename, txtfolder=options.txtfolder, sofolder=options.sofolder, bratfolder=options.bratfolder, corenlpfolder=options.corenlpfolder)
