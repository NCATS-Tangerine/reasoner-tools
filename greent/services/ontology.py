import json

import pronto
import networkx
import obonet

import re
import logging
from greent.util import LoggingUtil
from greent.service import Service
from pronto.relationship import Relationship
from greent.servicecontext import ServiceContext
from flask import jsonify
logger = LoggingUtil.init_logging(__name__, level=logging.DEBUG)

#import sys

class GenericOntology(Service):
    """ Sure, don't just dig around in obo files they say. But when the SPARQL is dry, we will drink straight from the obo if need be. """
    
    def __init__(self, context, obo):
        """ Load an obo file. """
        super(GenericOntology, self).__init__("go", context)
        self.ont = pronto.Ontology (obo)
        #self.pronto_ont = pronto.Ontology (obo)
        self.obo_ont = obonet.read_obo(obo)
        
    
    def label(self,identifier):
        """Return the exitlabel for an identifier"""
        return self.ont[identifier].name if identifier in self.ont else None
 
    def is_a(self,identifier, term):
        """Determine whether a term has a particular ancestor"""
        print (f"is {identifier} a {term}?")
        is_a = False
        is_a_rel = Relationship('is_a')
        if identifier in self.ont:
            #parents = self.ont[identifier].parents
            the_term = self.ont[identifier]
            parents = the_term.relations[is_a_rel] if is_a_rel in the_term.relations else []
            print (f"{identifier} parents {parents}")
            for ancestor in parents:
                ancestor_id = ancestor.id
                if ' ' in ancestor.id:
                    ancestor_id = ancestor.id.split(' ')[0]
                print (f"   ancestor: {ancestor_id}")
                is_a = ancestor_id == term
                if is_a:
                    break
                if 'xref' in ancestor.other:
                    for xancestor in ancestor.other['xref']:
                        print (f"      ancestor-xref: {xancestor} ?=~ {term}")
                        is_a = xancestor.startswith (term)
                        if is_a:
                            break
                if not is_a:
                    is_a = self.is_a (ancestor_id, term)
                if is_a:
                    break
        print (f"{identifier} is_a {term} => {is_a}")
        return is_a
    
    def xrefs(self, identifier):
        """ Get external references. """
        result = []
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other['xref']  if 'xref' in term.other else []
        result = [ x.split(' ') if ' ' in x else [x, ''] for x in result ]
        result = [ { 'id' : x[0], 'desc' : ' '.join(x[1:]) } for x in result if len(x) > 1 and ':' in x[0] ]
        return result
    
    def synonyms(self, identifier, curie_pattern=None):
        """ Get synonyms. """
        return \
            [ x for x in self.ont[identifier].synonyms if curie_pattern and x.startswith(curie_pattern) ] + \
            [ syn for syn in self.ont[identifier].synonyms ] \
            if identifier in self.ont else []
    
    def search (self, text, is_regex=False, ignore_case=True):
        """ Search for the text, treating it as a regular expression if indicated. """
        print (f"text: {text} is_regex: {is_regex}, ignore_case: {ignore_case}")
        pat = None
        if is_regex:
            pat = re.compile(text, re.IGNORECASE) if ignore_case else re.compile(text)
        result = {}
        for term in self.ont:
            if is_regex:
                if pat.match (term.name):
                    logger.debug (f"  matched {text} pattern in term name: {term.name}")
                    result[term.id] = term
                else:
                    for syn in term.synonyms:
                        if pat.match (syn.desc):
                            logger.debug (f"  matched {text} pattern in synonym: {syn.desc}")
                            result[term.id] = term
            else:
                if text.lower() == term.name.lower():
                    logger.debug (f"  text {text} == term name {term.name}")
                    result[term.id] = term
                else:
                    for syn in term.synonyms:
                        if text.lower() == syn.desc.lower():
                            logger.debug (f"  text {text.lower()} == synonym: {syn.desc.lower()}")
                            result[term.id] = term
        result = [  { "id" : term.id, "label" : term.name } for key, term in result.items () ]
        return result
    
    def lookup(self, identifier):
        """ Given an identifier, find ids in the ontology for which it is an xref. """
        assert identifier and ':' in identifier, "Must provide a valid identifier."
        result = []
        for term in self.ont:
            xrefs = []
            if 'xref' in term.other:
                for xref in term.other['xref']:
                    if xref.startswith (identifier):
                        if ' ' in xref:
                            xref_pair = xref.split(' ')
                            xref_pair = [ xref_pair[0], ' '.join (xref_pair[1:]) ]
                        else:
                            xref_pair = [xref, '']
                            print (f"xref_pair: {xref_pair}")
                        xrefs.append ({
                            'id'   : xref_pair[0],
                            'desc' : xref_pair[1]
                        })
            if len(xrefs) > 0:
                result.append ({
                    "id"    : term.id,
                    "xrefs" : xrefs
                })                
        return result

    def id_list(self, identifier):
        id_list = []
        id_list = [term.id for term in self.ont if term.id.startswith(identifier)]
        if not id_list:
            id_list = None
        return id_list

    def exactMatch(self, identifier):
        
        result = []
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other['property_value']  if 'property_value' in term.other else []
        
        raw_exactMatches = [x.replace('exactMatch ', '') for x in result if 'exactMatch' in x]
        url_stripped_exactMatches = [re.sub(r"(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)", "", str(x)) for x in raw_exactMatches]
        formatted_exactMatches = [re.sub(r"(\/)",":", str(x)) for x in url_stripped_exactMatches]     
        # the umls URIs have a peculiar format, we handle that as follows:
        umls_exactMatches = [re.sub(r"(?:(resource:)|(id:))","", str(x)) for x in formatted_exactMatches if "resource" in x]
        normal_exactMatches = [x for x in formatted_exactMatches if "resource" not in x]
        all_exactMatches = normal_exactMatches + umls_exactMatches
        return all_exactMatches

    def closeMatch(self, identifier):
        
        result = []
        if identifier in self.ont:
            term = self.ont[identifier]
            result = term.other['property_value']  if 'property_value' in term.other else []

        raw_closeMatches = [x.replace('closeMatch ', '') for x in result if 'closeMatch' in x]
        url_stripped_closeMatches = [re.sub(r"(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)", "", str(x)) for x in raw_closeMatches]
        formatted_closeMatches = [re.sub(r"(\/)",":", str(x)) for x in url_stripped_closeMatches]     
        # the umls URIs have a peculiar format, we handle that as follows:
        umls_closeMatches = [re.sub(r"(?:(resource:)|(id:))","", str(x)) for x in formatted_closeMatches if "resource" in x]
        normal_closeMatches = [x for x in formatted_closeMatches if "resource" not in x]
        all_closeMatches = normal_closeMatches + umls_closeMatches
        return all_closeMatches

    def descendants(self, identifier):
        # networkx.ancestors returns SUBTERMS (DESCENDANTS)
        # networkx.ancestors(<file>.obo, CURIE) ---> this says
        # that CURIE is the ancestor and DESCENDANTS will be returned...
        obo_ont_netx_descendants = networkx.ancestors(self.obo_ont, identifier)
        
        return list(obo_ont_netx_descendants)

    def ancestors(self, identifier):
        # networkx.descendants returns SUPERTERMS (ANCESTORS)
        # networkx.descendants(<file>.obo, CURIE) --> this says
        # that CURIE is the descendant and ANCESTORS will be returned
        obo_ont_netx_ancestors = networkx.descendants(self.obo_ont, identifier)
        return list(obo_ont_netx_ancestors)

    def parents(self,identifier):
        predecessor_lineage = networkx.predecessor(self.obo_ont, identifier)
        parents = [key for key, value in predecessor_lineage.items() if identifier in value]
        return parents

    def children(self, identifier):

        return

    def siblings(self, identifiers):

        pronto_ont_parents = self.ont.rparents()

        return 