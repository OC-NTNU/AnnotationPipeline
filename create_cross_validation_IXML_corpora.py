# -*- coding: utf-8 -*-
"""
Creates 5 different sets of test and training corpora, that can be used for 
5-fold cross-validation. Uses the convertion code in convert to IXML.
"""
from optparse import OptionParser
from convert_to_interactionXML import do_convert
import parse_and_align
import os

def build_corpora(ann_dir, nlp_dir, is_given, ignore_sentences):
    parse_and_align.parse_and_align(filefolder=ann_dir, nlpfolder=nlp_dir)    
    
    if is_given:
        is_given = 'True'
    else:
        is_given = 'False'
    
    # Find all the papers    
    papers = list(set([filename[:filename.index('.')] for filename in os.listdir(ann_dir)]))
    assert len(papers) == 10, "The current script assumes a corpus of 10 papers. If you have more, maybe a 5-fold is not the best idea?"
    
    # Create partitions of the papers
    for start_index in xrange(0, len(papers), 2):
        print "Creating fold", start_index/2
        test_set = [papers[start_index], papers[start_index+1]]
        training_set = [paper for j, paper in enumerate(papers) if not j in [start_index, start_index+1]]
        devel_set = training_set[:len(training_set)//2]
        training_set = training_set[len(training_set)//2:]
        
        do_convert(test_set, ann_dir, nlp_dir, "test_"+str(start_index/2), given=is_given, ignore_sentences=False)
        do_convert(training_set, ann_dir, nlp_dir, "train_"+str(start_index/2), given=is_given, ignore_sentences)
        do_convert(devel_set, ann_dir, nlp_dir, "devel_"+str(start_index/2), given=is_given, ignore_sentences)

if __name__ == "__main__":
    optparser = OptionParser("Script for building IXML corpora for cross validation. Assumes 10 papers and 5 fold validation.")
    optparser.add_option("-a", "--ann", default=None, dest="annotation_directory", help="Directory where the annotation files are stored.")
    optparser.add_option("-p", "--prep", default=None, dest="analyses_directory", help="Directory where the linguistic preprocessing files are stored.")
    optparser.add_option("--ignoreSentences", default=False, dest="ignore_sentences", action="store_true", help="Pass this trigger if sentences without annotation should not be included in the train and devel IXML")
    optparser.add_option("--given", default=False, dest="given", action="store_true", help="Pass this trigger if GIVEN=TRUE should be specified in the IXML for every entity")
    (options, args) = optparser.parse_args()
    
    assert options.annotation_directory, "You must specify a directory from which to gather the annotation files."
    assert options.analyses_directory, "You must specify a directory from which to gather the files with the linguistic preprocessings."    
    
    build_corpora(options.annotation_directory, options.analyses_directory, options.given, options.ignore_sentences)