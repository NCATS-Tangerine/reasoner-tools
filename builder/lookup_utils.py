import logging
import requests
from flask import jsonify

#jenkins tester 1 - july 27 11:06AM

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

def ctd_drug_name_string_to_chemical_identifier(drug_name_as_string):  
    CTD_query = requests.get(f"http://ctdapi.renci.org/CTD_chemicals_ChemicalName/{drug_name_as_string}/").json()
    matches_from_CTD_query = [ x['ChemicalID'] for x in CTD_query if x['ChemicalName'].upper() == drug_name_as_string.upper()]
    if not matches_from_CTD_query:
        CTD_synonym_query = requests.get (f"http://ctdapi.renci.org/CTD_chemicals_Synonyms/{drug_name_as_string}/").json()
        synonym_matches_from_CTD_query = [x['ChemicalID'] for x in CTD_synonym_query]
        matches_from_CTD_query = matches_from_CTD_query + synonym_matches_from_CTD_query
    #print('CTD:', matches_from_CTD_query)
    return matches_from_CTD_query

def pharos_drug_name_to_chemical_identifier(drug_name_as_string):
    # pharos_results = []
    # pharos_query = requests.get(f"https://pharos.nih.gov/idg/api/v1/ligands/search?q={drug_name_as_string}").json()
    # if pharos_query['content']:
        
    #     if drug_name_as_string in pharos_query['content'] or drug_name_as_string in pharos_query['facets']:
    #         drug_specific_url = pharos_query['content'][0]["self"]
    #         drug_specific_query = requests.get(drug_specific_url).json()
    #         print(drug_specific_query["name"])
    #         print(drug_specific_query["description"])
    #         print(drug_specific_query["synonyms"])

    #         if drug_name_as_string in drug_specific_query["name"] or drug_specific_query["description"] or drug_specific_query["synonyms"]:
    #             if drug_specific_query["name"]:
    #                 print(drug_specific_query["name"])
    #             try:
    #                 #drug_specific_query["synonyms"][1]["term"]:
    #                 print(drug_specific_query["synonyms"][1]["term"])
    #             except:
    #                 print("no chembl ID")
    #     else:
    #         pass
    
    
    # current method live on stars-c0, below:
    # drug_name_as_string = drug_name_as_string.replace(' ','' '')
    # pharos_query = requests.get(f"https://pharos.nih.gov/idg/api/v1/ligands/search?q={drug_name_as_string}").json()
    # facets = pharos_query['facets']
    # print(facets)
    # values = [x['values'] for x in facets]
    
    # values = [val for sublist in values for val in sublist] #stripping off a superfluous outer list
    # labels = [x['label'] for x in values]
    # useful_labels = [x for x in labels if x.startswith('CHEMBL') and len(x) > len('CHEMBL')]
    # useful_labels_no_duplicates = []
    # for x in useful_labels:
    #     if x not in useful_labels_no_duplicates:
    #         useful_labels_no_duplicates.append(x)
    # added_string = ':CHEMBL'
    # added_string_location = len('CHEMBL')
    # useful_labels_modified = [x[:added_string_location]+added_string+x[added_string_location:] for x in useful_labels_no_duplicates]
    # print('pharos:', useful_labels_modified)
    
    return #pharos_results

def pubchem_drug_name_to_chemical_identifier(drug_name_as_string):
    pubchem_query = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name_as_string}/property/MolecularFormula/JSON").json()
    if 'Fault' in pubchem_query:
        empty_pubchem_query = []
        return empty_pubchem_query
    else:
        pubchem_IDs = [x['CID'] for x in pubchem_query['PropertyTable']['Properties']]
        pubchem_IDs_annotated = ["PUBCHEM:" + str(x) for x in pubchem_IDs]
        return pubchem_IDs_annotated

def onto_drug_name_to_chemical_identifier(drug_name_as_string):
    query_text = f"https://onto.renci.org/search/{drug_name_as_string}/?regex=false"
    onto_response = requests.get(query_text).json()
    onto_IDs_annotated = []
    new_dict = {}
    for substance in onto_response['values']:
        del substance['type']
        onto_IDs_annotated.append(substance)
    print(onto_IDs_annotated)
    print()


    return onto_IDs_annotated

def chemical_ids_from_drug_names( drug_name_as_string ):
    """Look up drugs by name.  We will pull results from multiple sources in this case,
    and return them all."""
    logger=logging.getLogger('application')
    ctd_ids = ctd_drug_name_string_to_chemical_identifier(drug_name_as_string)
    pubchem_ids = pubchem_drug_name_to_chemical_identifier (drug_name_as_string)
    onto_ids = onto_drug_name_to_chemical_identifier(drug_name_as_string)
    chemical_ids_from_drug_names = ctd_ids + pubchem_ids + onto_ids
    
    return
    #return onto_ids
    #return [ { "id" : i, "label" : drug_name_as_string } for i in chemical_ids_from_drug_names ] if chemical_ids_from_drug_names else []

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