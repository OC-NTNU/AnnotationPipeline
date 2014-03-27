# -*- coding: utf-8 -*-
"""
Superscript that calls on the other scrips and programs to transform DOIs to 
Brat-formatted files.

"""
from optparse import OptionParser
from subprocess import call
import os
import fetch_plos_papers
import brat_format

def run(doi_file, nxmlpath, coreNLPpath):
    dois = [line.strip() for line in open(doi_file, 'r')]
    
    # Download all the DOIs
    if not os.path.isdir("PLOS"):
        os.mkdir("PLOS")
    for doi in dois:
        fetch_plos_papers.download_doi(doi, outfolder="PLOS")

    # Run NXML2TXT
    if not os.path.exists("TXT"):
        os.mkdir("TXT")
    if not os.path.exists("SO"):
        os.mkdir("SO")
    for filename in os.listdir("PLOS"):
        filename_root = filename[:filename.index('.')]
        call([nxmlpath, os.path.join("PLOS", filename), os.path.join("TXT", filename_root+".txt"), os.path.join("SO", filename_root+".so")])

    # Run Stanford CoreNLP
    if not os.path.exists("CoreNLP"):
        os.mkdir("CoreNLP")
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    filenames = [filename for filename in os.listdir("TXT")]
    with open(os.path.join("tmp", "corenlpfilelist"), 'w') as tmpfile:
        for filename in filenames:
            tmpfile.write(os.path.join("TXT", filename) + "\n")    
    
    call(["java", "-cp", 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1.jar") + ":" + 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1-models.jar") + ":" + 
          os.path.join(coreNLPpath, "xom.jar") + ":" + 
          os.path.join(coreNLPpath, "joda-time.jar") + ":" + 
          os.path.join(coreNLPpath, "jollyday.jar") + ":" + 
          os.path.join(coreNLPpath, "ejml-0.23.jar"), 
          "-Xmx3g","edu.stanford.nlp.pipeline.StanfordCoreNLP",
          "-annotators", "tokenize,cleanxml,ssplit,pos,lemma,ner,parse,dcoref", 
          "-outputExtension", ".xml", "-replaceExtension", "-outputDirectory", "CoreNLP", 
          "-filelist", os.path.join("tmp", "corenlpfilelist")])

    # Transform to Brat annotations
    for filename in filenames:
        filename_root = filename[:filename.index('.')]
        brat_format.convert_plos_to_brat(filename_root, txtfolder="TXT", sofolder="SO", bratfolder="Brat", corenlpfolder="CoreNLP")

if __name__=="__main__":
    optparser = OptionParser("Downloads papers with given DOIs from PLoS, and does all the preprocessing requried to annotate in Brat.")
    optparser.add_option("-i", "--doi", dest="doi_file", default=None, help="Input file - should contain all the DOIs to be downloaded on a separate line.")    
    optparser.add_option("-n", "--nxml2txt", dest="nxmlpath", default=os.path.join(os.getcwd(), "nxml2txt"), help="Path of the NXML2TXT executable.")
    optparser.add_option("-c", "--corenlp", dest="coreNLPpath", default=None, help="Path to the folder containing Stanford CoreNLP.")
    (options, args) = optparser.parse_args()
    
    assert options.doi_file, "You must specify an input file!"
    assert os.path.exists(options.doi_file), "The specified input file does not exist!"
    assert os.path.exists(options.nxmlpath), "The specificed NXML2TXT path does not refer to any file!"
    assert options.coreNLPpath, "You must specify the path for the CoreNLP folder!"
    assert os.path.isdir(options.coreNLPpath), "The given CoreNLP folderdoes not exist!"
    
    run(options.doi_file, options.nxmlpath, options.coreNLPpath)
