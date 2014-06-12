# -*- coding: utf-8 -*-
"""
Script that compares the IXML output of TEES with the Gold Standard and produces
evaluation metrics.

@author: elias
"""
from optparse import OptionParser
import xml.etree.ElementTree as ET

entity_type = {"None" : 0,
               "Increase" : 1,
               "Decrease" : 2,
               "Change" : 3,
               "Cause" : 4,
               "Correlate" : 5,
               "Negative_Correlate" : 6,
               "Positive_Correlate" : 7,
               "And" : 8,
               "Or" : 9,
               "RefExp" : 10,
               "Feedback" : 11,
               "Variable" : 12, 
               "Thing" : 13 }

argument_type = {"None" : 0,
                 "Theme" : 1,
                 "Agent" : 2,
                 "Co-theme" : 3,
                 "Part" : 4,
                 "RefExp" : 5}

def compare(ixml, gold, confusion_matrix_entities=None, confusion_matrix_argument=None):
    ixml = ET.parse(ixml)
    gxml = ET.parse(gold)
    
    if not confusion_matrix_entities:
        confusion_matrix_entities = [[0 for i in xrange(len(entity_type))] for j in xrange(len(entity_type))]
    if not confusion_matrix_argument:
        confusion_matrix_argument = [[0 for i in xrange(len(argument_type))] for j in xrange(len(argument_type))]
    
    # Find all documents in both xmls
    idocs = [doc for doc in ixml.findall('document')]
    gdocs = [doc for doc in gxml.findall('document')]
    
    assert len(idocs) == len(gdocs), "The two IXML files do not have the same amount of document files!"
    
    # Iterate over documents    
    for i in xrange(len(idocs)):
        # Find all sentences in each document
        isnt = [snt for snt in idocs[i].findall('sentence')]
        gsnt = [snt for snt in gdocs[i].findall('sentence')]
        
        assert len(isnt) == len(gsnt), "Document {0} has a different number of sentences in the two IXMLs!"
        
        # Iterate over sentences
        for j in xrange(len(isnt)):
            # Find all non-given triggers in the sentences
            itrgs = [trg for trg in isnt[j].findall('entity')] # if not trg.attrib.get('given') == "True"]
            gtrgs = [trg for trg in gsnt[j].findall('entity')] # if not trg.attrib.get('given') == "True"]

            # Try to match each trigger in IXML to a trigger in GXML
            event_id_map = {}
            matches = []
            non_matched_i = []
            non_matched_g = []
            matched_g = []
            
            for itrg in itrgs:
                i_start, i_end = map(int, itrg.attrib['charOffset'].split('-'))
                i_event_id = itrg.attrib['id']
                i_event_type = itrg.attrib['type']
                potmatch = []

                for gtrg in gtrgs:
                    g_start, g_end = map(int, gtrg.attrib['charOffset'].split('-'))
                    # Matching by either identical start or end offsets
#                    if g_start == i_start or i_end == g_end:
#                        potmatch.append(gtrg)
                    # Matching by scope overlap, as in PMS task
                    if (g_start >= i_start and g_start <= i_end) or (g_end >= i_start and g_end <= i_end):
                        potmatch.append(gtrg)
                
                # If there are multiple partial matches, take the match with 
                # the highest degree of overlap.
                if len(potmatch) > 1:
                    max_overlap = -1
                    best = None
                    for pm in potmatch:
                        pm_start, pm_end = map(int, pm.attrib['charOffset'].split('-'))
                        overlap = pm_end - pm_start
                        overlap -= max(0, i_start - pm_start)
                        overlap -= max(0, pm_end - i_end)
                        if overlap > max_overlap:
                            best = pm
                    if best == None:
                        print "DEATH"
                        print i_event_id, i_event_type, i_start, i_end
                        for pm in potmatch:
                            print ET.dump(pm)
                    potmatch = [best]
                
                if potmatch:
                    gtrg = potmatch.pop()
                    g_event_id = gtrg.attrib['id']
                    g_event_type = gtrg.attrib['type']
                    event_id_map[g_event_id] = i_event_id
                    matches.append( (g_event_type, i_event_type) )
                    matched_g.append(g_event_id)
                else: 
                    non_matched_i.append(i_event_type)
                    
            # Now score all the event matches
            for g_type, i_type in matches:
                confusion_matrix_entities[entity_type[g_type]][entity_type[i_type]] += 1
            
            # All non-matched events are counted as matched with None
            for i_type in non_matched_i:
                confusion_matrix_entities[entity_type["None"]][entity_type[i_type]] += 1
            non_matched_g = [trg.attrib['type'] for trg in gtrgs if not trg.attrib['id'] in matched_g]
            for g_type in non_matched_g:
                confusion_matrix_entities[entity_type[g_type]][entity_type["None"]] += 1
         
            # Index the given keys to help interaction matching
            given_e = [trg.attrib['id'] for trg in isnt[j].findall('entity') if trg.attrib.get('given') == "True"]            
            for e in given_e:
                event_id_map[e] = e
                
            # Find all interactions between triggers
            iitrs = [itr for itr in isnt[j].findall('interaction')]
            gitrs = [itr for itr in gsnt[j].findall('interaction')]
            
            for iitr in iitrs:
                iitr_e1 = iitr.attrib['e1']
                iitr_e2 = iitr.attrib['e2']
                iitr_type = iitr.attrib['type']
                if iitr_type in ["Part", "Part2", "Part3", "Part4"]:
                    iitr_type = "Part"
                
                for gitr in gitrs:
                    gitr_e1 = gitr.attrib['e1']
                    gitr_e2 = gitr.attrib['e2']
                    gitr_type = gitr.attrib['type']
                    if gitr_type in ["Part", "Part2", "Part3", "Part4"]:
                        gitr_type = "Part"
                    
                    try:
                        if event_id_map[gitr_e1] == iitr_e1 and event_id_map[gitr_e2] == iitr_e2:
                            confusion_matrix_argument[argument_type[gitr_type]][argument_type[iitr_type]] += 1
                            gitrs.remove(gitr)
                            break
                    except:
                        pass
                else:
                    # If an interaction is not matched in the gold standard, it 
                    # is matched to None
                    confusion_matrix_argument[argument_type["None"]][argument_type[iitr_type]] += 1
             
             # Then all the interactions in the gold standard that are not in the output
            for gitr in gitrs:
                 gitr_type = gitr.attrib['type'] 
                 if gitr_type in ["Part", "Part2", "Part3", "Part4"]:
                     gitr_type = "Part"
                 confusion_matrix_argument[argument_type[gitr_type]][argument_type["None"]] += 1
                    
    return confusion_matrix_entities, confusion_matrix_argument

def print_matrix(matrix, dicti):
    orig_keys = dicti.keys()
    short_keys = [key[:5] for key in orig_keys]
    
    print "\t"+"\t".join(short_keys)
    
    for i in xrange(len(matrix)):
        stri = ""
        for j in xrange(-1, len(matrix)):
            if j==-1:
                stri += short_keys[i] + "\t"
            else:
                stri += str(matrix[dicti[orig_keys[i]]][dicti[orig_keys[j]]]) + "\t"
        print stri

if __name__ == "__main__":

    optparser = OptionParser("Script for evaluating IXML output with gold standard.")
    optparser.add_option("-i", "--ixml", default=None, dest="ixml", help="Path to the IXML file to evaluate.")
    optparser.add_option("-g", "--gold", default=None, dest="gold", help="Path to the gold standard IXML file.")
    (options, args) = optparser.parse_args()
    
    assert options.ixml, "You must specify an IXML file to evaluate!"
    assert options.gold, "You must specify a gold standard IXML file!"    
    
    cme, cma = compare(options.ixml, options.gold)
    
    print_matrix(cme, entity_type)
    print
    print_matrix(cma, argument_type)
"""
	files = [("/data/software/nlp/TEES/tmp/er_fold0/classification-test/test-unmerging-pred.xml", "/data/software/nlp/TEES/tmp/IXML/test_0.xml"),
             ("/data/software/nlp/TEES/tmp/er_fold1/classification-test/test-unmerging-pred.xml", "/data/software/nlp/TEES/tmp/IXML/test_1.xml"),
             ("/data/software/nlp/TEES/tmp/er_fold2/classification-test/test-unmerging-pred.xml", "/data/software/nlp/TEES/tmp/IXML/test_2.xml"),
             ("/data/software/nlp/TEES/tmp/er_fold3/classification-test/test-unmerging-pred.xml", "/data/software/nlp/TEES/tmp/IXML/test_3.xml"),
             ("/data/software/nlp/TEES/tmp/er_fold4/classification-test/test-unmerging-pred.xml", "/data/software/nlp/TEES/tmp/IXML/test_4.xml"),
            ]
    
	confusion_e = None
	confusion_i = None
    
	for ii, gg in files:
		confusion_e, confusion_i = compare(ii, gg, confusion_matrix_entities=confusion_e, confusion_matrix_argument=confusion_i)
    
	print_matrix(confusion_e, entity_type)
	print 
	print_matrix(confusion_i, argument_type)
"""