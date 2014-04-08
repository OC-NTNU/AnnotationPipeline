# -*- coding: utf-8 -*-
"""
Script to readjust SOA offsets after fixing sentence splitting.
"""
import re
            
def readjust(sfilename="Brat/101371journalpone0052932", txtfilename="TXT/101371journalpone0052932.txt"):
    original_text = open(txtfilename, 'r').read()
    sentences = [sentence.strip() for sentence in open(sfilename+".txt", 'r')]
    soas = []    
    
    # Uses the following heuristic: Most sentences are found only once in the original material,
    # so it uses the found indices. For sentences that occur more than once, use the first occurence
    # that is stricly after the last sentence.
    last_end = -1
    for sentence in sentences:
        print sentence
        finds = [(f.start(), f.end()) for f in re.finditer(re.escape(sentence), original_text)]
        for find in finds:
            print find
            if find[0] > last_end:
                soas.append(find)
                last_end = find[1]
                break
        else:
            assert False, "Sentence '{0}' does not occur in the original paper. Something wrong has occured!".format(sentence)
    
    with open(sfilename+".soa", 'w') as soafile:
        for soa in soas:
            soafile.write(str(soa[0]) + " " + str(soa[1]) + "\n")
                
if __name__ == "__main__":
    readjust()