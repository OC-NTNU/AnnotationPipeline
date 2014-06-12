# -*- coding: utf-8 -*-
"""
Script to do parsing and dependency extraction on interesting sentences, and 
the results are realigned to the original TXT file produced by NXML2TXT.
"""
import os
import xml.etree.ElementTree as ET
from subprocess import call

def parse_and_align(filefolder="Brat", nlpfolder="CoreNLP", coreNLPpath="/home/elias/master/sfcnlp"):
    parse(filefolder, nlpfolder, coreNLPpath)
    align(filefolder, nlpfolder)
    
def parse(filefolder, nlpfolder, coreNLPpath):
    # Create list of files to parse    
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")
    
    filenames = [filename for filename in os.listdir(filefolder) if '.txt' in filename]
    
    with open(os.path.join("tmp", "corenlpfilelist"), 'w') as file:
        for filename in filenames:
            if not os.path.exists(os.path.join(nlpfolder, filename[:-4]+".xml")):
                file.write(os.path.join(filefolder, filename) + "\n")

    # Run CoreNLP on list of files
    call(["java", "-cp", 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1.jar") + ":" + 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1-models.jar") + ":" + 
          os.path.join(coreNLPpath, "xom.jar") + ":" + 
          os.path.join(coreNLPpath, "joda-time.jar") + ":" + 
          os.path.join(coreNLPpath, "jollyday.jar") + ":" + 
          os.path.join(coreNLPpath, "ejml-0.23.jar"), 
          "-Xmx3g","edu.stanford.nlp.pipeline.StanfordCoreNLP",
          "-annotators", "tokenize,cleanxml,ssplit,pos,lemma,parse", "-ssplit.eolonly", "-newlineIsSentenceBreak"
          "-outputExtension", ".xml", "-replaceExtension", "-outputDirectory", nlpfolder, 
          "-filelist", os.path.join("tmp", "corenlpfilelist")])
          
def align(filefolder, nlpfolder):
    filenames = set([filename[:filename.index('.')] for filename in os.listdir(filefolder)])
    
    for filename in filenames:
        # Find the sentence offset boundaries
        sentence_starts = []
        for sentence in open(os.path.join(filefolder, filename+".soa"), 'r'):
            start, _ = sentence.strip().split()
            sentence_starts.append(int(start))
        
        # Find the sentences in the CoreNLP output
        cnlp_xml = ET.parse(os.path.join(nlpfolder, filename+".xml"))
        
        for i, sentence in enumerate(cnlp_xml.iter('sentence')):
            # Note the starting offset of the sentence
            sentence_start = int(sentence.find('tokens').find('token').find('CharacterOffsetBegin').text)
            # Now, update the offset of all words
            for token in sentence.find('tokens').iter('token'):
                change = - sentence_start + sentence_starts[i]
                token.find('CharacterOffsetBegin').text = str(int(token.find('CharacterOffsetBegin').text) + change)
                token.find('CharacterOffsetEnd').text = str(int(token.find('CharacterOffsetEnd').text) + change)

        # Then store the results
        cnlp_xml.write(os.path.join(nlpfolder, filename+".xml"))
        
if __name__=="__main__":
    print "Interface running the script from shell is not written yet."
