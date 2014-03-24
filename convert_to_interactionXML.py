# -*- coding: utf-8 -*-
"""
Script for converting Brat annotations combined with output from Stanford CoreNLP to InteractionXML format.

Assumes that there is a subfolder "Annotations" that contains:
    x.ann
    x.nlp
For every annotated paper with name x.
"""
from optparse import OptionParser
import xml.etree.ElementTree as ET
import os
import collections

def convert_to_ixml(ann_dir, nlp_dir):
    papers = set([filename[:filename.index('.')] for filename in os.listdir(ann_dir)])
    
    root = ET.Element('corpus')
    xml_tree = ET.ElementTree(element=root)
    root.attrib = {'source' : 'OceanCertainCorpus'}
    
    for paper in papers:
        # Create document level node in the XML
        document = ET.SubElement(root, 'document')
        document.attrib = {'id' : paper}
        
        sentences = [line.strip() for line in open(os.path.join(ann_dir, paper+".txt"), 'r')]
        offsets = [line.strip().split() for line in open(os.path.join(ann_dir, paper+".soa"), 'r')]
        nlp_xml = ET.parse(os.path.join(nlp_dir, paper+".xml"))
        relations = [tuple(line.strip().split()) for line in open(os.path.join(ann_dir, paper+".ann"), 'r') if "E" in line.strip().split()[0]]
        entities = [tuple(line.strip().split()) for line in open(os.path.join(ann_dir, paper+".ann"), 'r') if "T" in line.strip().split()[0]]
        assert len(relations)+len(entities) == len([line.strip().split() for line in open(os.path.join(ann_dir, paper+".ann"), 'r')]), "There are unrecognized annotations in the annotation file!" 
        # Build index from offset positions to sentence. 
        # (Uses only END position, because the start position can have been a removed headline, causing misalignment between CoreNLP and Brat formats)
        offsets_to_sentence = dict()
        for sentence in nlp_xml.iter('sentence'):
            for i, token in enumerate(sentence.iter('token')):
                end = token.find('CharacterOffsetEnd').text
            offsets_to_sentence[end] = sentence
            
        # Build index from sentence # to list of entities and relations in sentence
        sentence_nbr_to_entities = collections.defaultdict(set)
        sentence_nbr_to_relations = collections.defaultdict(set)
        sentence_start_offset = 0
        for i, sentence in enumerate(sentences):
            # Entities are included if they have endoffset before the endoffset of the current sentence
            for entity in entities:
                if int(entity[3]) <= sentence_start_offset+len(sentence) and int(entity[2]) >= sentence_start_offset:
                    # Make a new entity that uses sentence internal offset, rather than Brat offset
                    reindexed_entity = list(entity)
                    reindexed_entity[2] = int(reindexed_entity[2]) - sentence_start_offset
                    reindexed_entity[3] = int(reindexed_entity[3]) - sentence_start_offset                    
                    reindexed_entity = tuple(reindexed_entity)
                    sentence_nbr_to_entities[i].add(entity)
            sentence_start_offset += len(sentence)
            # Entities are included if all their arguments are in the sentence
            # NOTE: This will create a problem for co-ref, but TEES is unable to handle coref anyway
            for j in xrange(6): # This is a hack to make sure that every relation is included, even if its arguments are events, up to a nesting of 4. If we need more, a topological sort might be more efficient.
                argument_ids = set()
                for entity in sentence_nbr_to_entities[i]:
                    argument_ids.add(entity[0])
                for relation in sentence_nbr_to_relations[i]:
                    argument_ids.add(relation[0])
                for relation in relations:
                    _ids = [roleid[roleid.index(':')+1:] for roleid in relation[1:]]
                    if all([_id in argument_ids for _id in _ids]):
                        sentence_nbr_to_relations[i].add(relation)
            
            
        # Create sentence level nodes in the XML
        for i, sentence in enumerate(sentences):
            sentence_node = ET.SubElement(document, 'sentence')
            start, end = offsets[i]
            sentence_node.attrib = {'id' : paper+"."+str(i),
                                    'tail' : '',
                                    'text' : sentence,
                                    'charOffset' : start+"-"+end}
                                    
            # Use pre-built index to find matching sentence in CoreNLP output
            nlp_sentence_node = offsets_to_sentence[end]

            # Create the linguistic analysis nodes
            analysis_node = ET.SubElement(sentence_node, 'analyses')
            
            # Tokenization nodes
            tokenization_node = ET.SubElement(analysis_node, 'tokenization')
            tokenization_node.attrib = {'tokenizer' : 'CoreNLP'}
            
            # Now there is a problem; namely that maybe not the entire sentence
            # that CoreNLP has extracted has been used in Brat. Specifically,
            # some headlines might have been removed
            idn = 0 # Used to give unique IDs for all tokens
            # Index Original_ID -> new_ID, used to map the dependencies below to correct arguments
            oid_nid_idx = dict()
            for token in nlp_sentence_node.iter('token'):
                # Only store word that have not been removed by Brat script
                if not token.find('CharacterOffsetBegin').text < start:
                    unique_id = "t"+str(idn); idn += 1
                    oid_nid_idx[token.attrib['id']] = unique_id
                    token_node = ET.SubElement(tokenization_node, 'token')
                    token_node.attrib = {"POS" : token.find('POS').text,
                                       "CharacterOffset" : token.find('CharacterOffsetBegin').text+"-"+token.find('CharacterOffsetEnd').text,
                                       "id" : unique_id, 
                                        "text" :  token.find('word').text}
#                                        headScore lacks in the CoreNLP original data
            
            # Parsing information nodes
            parse_node = ET.SubElement(analysis_node, 'parse')
            parse_node.attrib = {"parser" : "CoreNLP",
                                 "stanford" : "ok", 
                                 "tokenizer" : "CoreNLP",
                                 "pennstring" : nlp_sentence_node.find('parse').text,
                                 }
            
            for dependencies in nlp_sentence_node.iter('dependencies'):
                # Pick the most processed variant of the dependencies
                if not dependencies.attrib['type'] == 'collapsed-ccprocessed-dependencies':
                    continue
                for idn, dep in enumerate(dependencies.iter('dep')):
                    dependency_type = dep.attrib['type']
                    if dependency_type == 'root': continue
                    try:
                        governor = oid_nid_idx[dep.find('governor').attrib['idx']]
                        dependnt = oid_nid_idx[dep.find('dependent').attrib['idx']]
                        
                        dependency_unique_id = "d" + str(idn)

                        dependency_node = ET.SubElement(parse_node, 'dependency')
                        dependency_node.attrib = {'id' : dependency_unique_id,
                                                  't1' : governor,
                                                  't2' : dependnt,
                                                  'type' : dependency_type}
                    except KeyError:
                        # Happens if a dependency exists between a headline that was chopped
                        # away for Brat, and other words in the sentence. The dependency is
                        # therefore spurious, and should therefore be skipped.
                        pass
                    

            # NOTE: This script ignores phrasalization, because that cannot be read 
            # directly from the CoreNLP output XML. If we need this, it needs to be
            # extracted from the pennstring.
            
            # Create nodes for entities and interactions
            entities = sentence_nbr_to_entities[i]
            relations = sentence_nbr_to_relations[i]

            # Index original_ID -> new_ID for entities and relations
            oeid_neid_idx = dict()
        
            for ii, entity in enumerate(entities):
                entity_node = ET.SubElement(sentence_node, 'entity')
                sstart, _ = offsets[i]
                eid = paper+"."+str(i)+"."+str(ii)
                oeid_neid_idx[entity[0]] = eid
                entity_node.attrib = {'text' : ' '.join(entity[4:]).strip(),
                                      'type' : entity[1],
                                      'id' :  eid,
                                      'charOffset' : entity[2]+"-"+entity[3],
                                      'headOffset' : entity[2]+"-"+entity[3],
                                      'origOffset' : str(int(sstart)+int(entity[2]))+"-"+str(int(sstart)+int(entity[3])),
                                      }
                if entity[1] in ["Variable", "Thing"]:
                    entity_node.attrib['given'] = "True"
                else:
                    entity_node.attrib['event'] = "True"
            
            # A for-loop is impossible, because the events need to be added in a specific order, no neccessarily the order produced by the iterator
            ii = 0
            relations = list(relations)
            while relations:
                relation = relations.pop(0)
                event_id = relation[0]
                _, source_id = relation[1].split(':')
                
                all_arguments_exist = (source_id in oeid_neid_idx)
                for argument in relation[2:]:
                    _, argument_id = argument.split(':')
                    all_arguments_exist = all_arguments_exist and (argument_id in oeid_neid_idx)
                    
                if not all_arguments_exist:
                    # Not all the required events have been processed yet, so we postpone processing this event.
                    relations.append(relation)
                else:
                    # Every relation should be split into a node for each of the arguments
                    for iii, argument in enumerate(relation[2:]):
                        # NOTE: There is a problem where the argument of an event is another event that has more than one argument. In this problem, it is hard to know where to attach the event.
                        argumnet_type, argument_id = argument.split(':')
                        
                        microevent_id = paper+"."+str(i)+"."+str(ii)+"."+str(iii)
                        oeid_neid_idx[event_id] = microevent_id
                        
                        relation_node = ET.SubElement(sentence_node, 'interaction')
                        relation_node.attrib = {'directed' : 'True',
                                                'event' : 'True',
                                                'id' : microevent_id,
                                                'e1' : oeid_neid_idx[source_id],
                                                'e2' : oeid_neid_idx[argument_id],
                                                'type' : argumnet_type,
                                                }
                    ii += 1
                    
    xml_tree.write("IXML/n.xml")
    
if __name__ == "__main__":
    optparser = OptionParser("Script for converting to Interaction XML format.")
    optparser.add_option("-a", "--ann", default=None, dest="annotation_directory", help="Directory where the annotation files are stored.")
    optparser.add_option("-p", "--prep", default=None, dest="analyses_directory", help="Directory where the linguistic preprocessing files are stored.")
    (options, args) = optparser.parse_args()
    
    assert options.annotation_directory, "You must specify a directory from which to gather the annotation files."
    assert options.analyses_directory, "You must specify a directory from which to gather the files with the linguistic preprocessings."    
    
    convert_to_ixml(options.annotation_directory, options.analyses_directory)
   