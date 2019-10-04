import logging
import requests
from flask import jsonify

def lookup_phenotype_by_name( name, greent ):
    """Return type is a list of HPO identifiers."""
    logger=logging.getLogger('application')
    #This performs a case-insensitive exact match, and also inverts comma-ed names
    hpo_ids =  greent.hpo.search( name )
    if len(hpo_ids) == 0:
        logger.error('Could not convert phenotype name: {}.'.format(name))
    else:
        logger.debug('Found ids for phenotype name: {} {}.'.format(name,' '.join(hpo_ids)))
    return hpo_ids

def pubchem_drug_name_to_chemical_identifier(drug_name_as_string):
    pubchem_query = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name_as_string}/property/MolecularFormula/JSON").json()
    if 'Fault' in pubchem_query:
        empty_pubchem_query = []
        return empty_pubchem_query
    else:
        pubchem_IDs = [x['CID'] for x in pubchem_query['PropertyTable']['Properties']]
        pubchem_IDs_annotated = ["PUBCHEM:" + str(x) for x in pubchem_IDs]
        pubchem_IDs_formatted = [ { "id" : i, "label" : drug_name_as_string } for i in pubchem_IDs_annotated ] if pubchem_IDs_annotated else []
        return pubchem_IDs_formatted

def onto_drug_name_to_chemical_identifier(drug_name_as_string):
    query_text = f"https://onto.renci.org/search/{drug_name_as_string}?regex=false"
    onto_response = requests.get(query_text).json()
    onto_IDs_annotated = []
    new_dict = {}
    for substance in onto_response['values']:
        #del substance['type']
        onto_IDs_annotated.append(substance)
    return onto_IDs_annotated

def ctd_drug_name_string_to_chemical_identifier(drug_name_as_string):  
    CTD_query = requests.get(f"http://ctdapi.renci.org/CTD_chemicals_ChemicalName/{drug_name_as_string}/").json()
    matches_from_CTD_query = [ { "id" : x['ChemicalID'], "label" : x['ChemicalName'].lower() } for x in CTD_query if x['ChemicalName'].upper() == drug_name_as_string.upper()]
    if not matches_from_CTD_query:
        CTD_synonym_query = requests.get (f"http://ctdapi.renci.org/CTD_chemicals_Synonyms/{drug_name_as_string}/").json()
        synonym_matches_from_CTD_query = [x['ChemicalID'] for x in CTD_synonym_query]
        matches_from_CTD_query = matches_from_CTD_query + synonym_matches_from_CTD_query
    return matches_from_CTD_query

def chemical_ids_from_drug_names( drug_name_as_string ):
    """Look up drugs by name.  We will pull results from multiple sources in this case,
    and return them all."""
    logger=logging.getLogger('application')
    ctd_ids = ctd_drug_name_string_to_chemical_identifier(drug_name_as_string)
    pubchem_ids = pubchem_drug_name_to_chemical_identifier (drug_name_as_string)
    onto_ids = onto_drug_name_to_chemical_identifier(drug_name_as_string)
    chemical_ids_from_drug_names =  onto_ids + pubchem_ids + ctd_ids
    return chemical_ids_from_drug_names

def lookup_identifier( name, name_type, greent ):
    if name_type == node_types.DRUG:
        return lookup_drug_by_name( name, greent )
    elif name_type == node_types.DISEASE:
        return lookup_disease_by_name( name, greent )
    elif name_type == node_types.PHENOTYPE:
        return lookup_phenotype_by_name( name, greent )
    else:
        raise ValueError('Only Drugs, Diseases, and Phenotypes may be used as named nodes')

def test():
    from greent.rosetta import Rosetta
    r = Rosetta()
    names = ['BUTYLSCOPOLAMINE','ADAPALENE','NADIFLOXACIN','TAZAROTENE']
    for name in names:
        print ( name, lookup_drug_by_name( name , r.core) )

if __name__ == '__main__':
    test()
