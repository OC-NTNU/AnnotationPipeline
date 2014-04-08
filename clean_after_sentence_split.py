# -*- coding: utf-8 -*-
"""
Script to readjust SOA offsets after fixing sentence splitting.

Can cause a problem where sentences are split without any character in between,
such as "Using the formula:where X is ...", this can happen when formulas are 
removed. The question is whether TEES can handle
"""
import re, os
from optparse import OptionParser

def clean_and_readjust(txt_dir="TXT", ann_dir="Brat"):
    filenames = set([filename[:filename.index('.')] for filename in os.listdir(ann_dir)])
    
    for filename in filenames:
        remove_double_newlines(os.path.join(ann_dir, filename+".txt"))
        readjust(os.path.join(ann_dir, filename), os.path.join(txt_dir, filename+".txt"))
        
        
def remove_double_newlines(filename):
    with open(filename, 'r') as file:
        text = re.sub('\n\n', '\n', file.read())
    
    with open(filename, 'w') as file:
        file.write(text) 

def readjust(sfilename=None, txtfilename=None):
    original_text = open(txtfilename, 'r').read()
    sentences = [sentence.strip() for sentence in open(sfilename+".txt", 'r')]
    soas = []    
    
    # Uses the following heuristic: Most sentences are found only once in the original material,
    # so it uses the found indices. For sentences that occur more than once, use the first occurence
    # that is stricly after the last sentence.
    last_end = -1
    for sentence in sentences:
        finds = [(f.start(), f.end()) for f in re.finditer(re.escape(sentence), original_text)]
        for find in finds:
            if find[0] >= last_end: #PROBLEMS? SEE ABOVE
                soas.append(find)
                last_end = find[1]
                break
        else:
            assert False, "Sentence '{0}' does not occur in the original paper. Something wrong has occured!".format(sentence)
    
    with open(sfilename+".soa", 'w') as soafile:
        for soa in soas:
            soafile.write(str(soa[0]) + " " + str(soa[1]) + "\n")
                
if __name__ == "__main__":
    optparser = OptionParser("Script to clean up and readjust alignments after manual sentence splitting.")
    optparser.add_option("-a", "--ann", default=None, dest="annotation_directory", help="Directory where the annotation files are stored.")
    optparser.add_option("-t", "--txt", default=None, dest="txt_directory", help="Directory where the original text files are stored.")
    (options, args) = optparser.parse_args()
    
    assert options.txt_directory, "You must specify a text directory!"
    assert options.annotation_directory, "You must specify an annotation directory!"

    clean_and_readjust(txt_dir=options.txt_directory, ann_dir=options.annotation_directory)
