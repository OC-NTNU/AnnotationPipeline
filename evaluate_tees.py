# -*- coding: utf-8 -*-
"""
Script that compares the IXML output of TEES with the Gold Standard and produces
evaluation metrics.

@author: elias
"""
from optparse import OptionParser
import xml.etree.ElementTree as ET

def compare(ixml, gold):
    ixml = ET.parse(ixml)
    gxml = ET.parse(gold)
    
    fp = 0
    tp = 0
    fn = 0
    
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
            itrgs = [trg for trg in isnt[j].findall('entity') if not trg.attrib.get('given') == "True"]
            gtrgs = [trg for trg in gsnt[j].findall('entity') if not trg.attrib.get('given') == "True"]

            # Try to match each trigger in IXML to a trigger in GXML
            event_id_map = {}
            type_map = []
            
            for itrg in itrgs:
                i_start, i_end = itrg.attrib['charOffset'].split('-')
                potmatch = []

                for gtrg in gtrgs:
                    g_start, g_end = gtrg.attrib['charOffset'].split('-')
                    if g_start == i_start or i_end == g_end:
                        potmatch.append(gtrg)
                
                assert len(potmatch) < 2, "Match on multiple locations, improve script!"
                
                if potmatch:
                    gtrg = potmatch.pop()
                    g_event_id = gtrg.attrib['id']
                    g_event_type = gtrg.attrib['type']
                    i_event_id = itrg.attrib['id']
                    i_event_type = itrg.attrib['type']
                    event_id_map[g_event_id] = i_event_id
                    type_map.append( (g_event_type, i_event_type) )
                    
            # Now score all the event matches
            for type1, type2 in type_map:
                if type1 == type2:
                    tp += 1
                else:
                    # Is this the proper score?
                    fp += 1
                    fn += 1
            
            # Give penalty for all non-aligned events
            fp += len(itrgs) - len(type_map) 
            fn += len(gtrgs) - len(type_map) 
                        
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
                
                for gitr in gitrs:
                    gitr_e1 = gitr.attrib['e1']
                    gitr_e2 = gitr.attrib['e2']
                    gitr_type = gitr.attrib['type']
                    
                    try:
                        if gitr_type == iitr_type and event_id_map[gitr_e1] == iitr_e1 and event_id_map[gitr_e2] == iitr_e2:
                            # Then its a match
                            tp += 1
                            gitrs.remove(gitr)
                            break
                        else:
                            fp += 1
                    except KeyError:
                        pass
                    
            fn += len(gitrs)
                    
    print tp, fp, fn
    p = float(tp)/float(tp+fp)
    r = float(tp)/float(tp+fn)
    print "Precision", p
    print "Recall", r
    print "F-score", float(2*p*r)/float(p+r)
    # Starting parsing at Wed May 21 18:49:02 2014


if __name__ == "__main__":
    optparser = OptionParser("Script for evaluating IXML output with gold standard.")
    optparser.add_option("-i", "--ixml", default=None, dest="ixml", help="Path to the IXML file to evaluate.")
    optparser.add_option("-g", "--gold", default=None, dest="gold", help="Path to the gold standard IXML file.")
    (options, args) = optparser.parse_args()
    
    assert options.ixml, "You must specify an IXML file to evaluate!"
    assert options.gold, "You must specify a gold standard IXML file!"    
    
    compare(options.ixml, options.gold)
