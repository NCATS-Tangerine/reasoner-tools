import logging
import requests
from flask import jsonify
#from greent import node_types

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


#Just going to use MONDO.
def lookup_disease_by_name( disease_name, greent ):
    """We can have different parameterizations if necessary.
    Here, we first get a mondo ID.  Then we try to turn that into
    (in order), a DOID, a UMLS, and an EFO.
    Return type is a list of identifiers."""
    logger=logging.getLogger('application')
    #This performs a case-insensitive exact match, and also inverts comma-ed names
    mondo_ids =  greent.mondo.search( disease_name )
    #Take out phenotypes...
    mondo_ids = list( filter( lambda x: not x.startswith('HP'), mondo_ids))
    if len(mondo_ids) == 0:
        logger.error('Could not convert disease name: {}.'.format(disease_name))
    else:
        logging.getLogger('application').debug('Found mondo identifiers for {}'.format(disease_name))
    return mondo_ids

#    for mid in mondo_ids:
#        logger.debug('  {}  {}'.format(mid, greent.mondo.get_label(mid)))
#    doids = sum([ greent.mondo.mondo_get_doid( r ) for r in mondo_ids], [] )
#    if len(doids) > 0:
#        logger.debug('Returning: {}'.format(' '.join(doids)))
#        return doids
#    umls = sum([ greent.mondo.mondo_get_umls( r ) for r in mondo_ids], [] )
#    if len(umls) > 0:
#        logger.debug('Returning: {}'.format(' '.join(umls)))
#        return umls
#    efos = sum([ greent.mondo.mondo_get_efo( r ) for r in mondo_ids], [] )
#    if len(efos) > 0:
#        logger.debug('Returning: {}'.format(' '.join(efos)))
#        return efos
#    logger.error('For disease name: "{}" found mondo ID(s): {}, but could not transform to another identifier system.'.format(disease_name, ';'.join(mondo_ids)))
#    return []


#below is taken from greent/services/CTD.py line 91
def ctd_drug_name_string_to_chemical_identifier(drug_name_as_string):  
    
    CTD_query = requests.get(f"http://ctdapi.renci.org/CTD_chemicals_ChemicalName/{drug_name_as_string}/").json()
    matches_from_CTD_query = [ x['ChemicalID'] for x in CTD_query if x['ChemicalName'].upper() == drug_name_as_string.upper()]
    if not matches_from_CTD_query:
        CTD_synonym_query = requests.get (f"http://ctdapi.renci.org/CTD_chemicals_Synonyms/{drug_name_as_string}/").json()
        print(CTD_synonym_query)
        synonym_matches_from_CTD_query = [x['ChemicalID'] for x in CTD_synonym_query]
        print(synonym_matches_from_CTD_query)
        matches_from_CTD_query = matches_from_CTD_query + synonym_matches_from_CTD_query
    return matches_from_CTD_query

def pharos_drug_name_to_chemical_identifier(drug_name_as_string):

    pharos_query = requests.get(f"https://pharos.nih.gov/idg/api/v1/ligands/search?q={drug_name_as_string}").json()
    facets = pharos_query['facets']
    values = [x['values'] for x in facets]
    values = [val for sublist in values for val in sublist] #stripping off a superfluous outer list
    labels = [x['label'] for x in values]
    useful_labels = [x for x in labels if x.startswith('CHEMBL') and len(x) > len('CHEMBL')]
    useful_labels_no_duplicates = []
    for x in useful_labels:
        if x not in useful_labels_no_duplicates:
            useful_labels_no_duplicates.append(x)
    added_string = ':CHEMBL'
    added_string_location = len('CHEMBL')
    useful_labels_modified = [x[:added_string_location]+added_string+x[added_string_location:] for x in useful_labels_no_duplicates]
    return useful_labels_modified

def pubchem_drug_name_to_chemical_identifier(drug_name_as_string):

    pubchem_query = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name_as_string}/property/MolecularFormula/JSON").json()
    pubchem_IDs = [x['CID'] for x in pubchem_query['PropertyTable']['Properties']]
    pubchem_IDs_annotated = ["PUBCHEM:" + str(x) for x in pubchem_IDs]
    return pubchem_IDs_annotated






def chemical_ids_from_drug_names( drug_name_as_string ):
    """Look up drugs by name.  We will pull results from multiple sources in this case,
    and return them all."""
    
    logger=logging.getLogger('application')
    logger.debug('Looking up drug name: {}'.format(drug_name_as_string) )
    
    #CTD_ids
    ctd_ids = ctd_drug_name_string_to_chemical_identifier( drug_name_as_string )
    logger.debug(' CTD says: {}'.format(ctd_ids) )

    # pharos_ids = 
    pharos_ids = pharos_drug_name_to_chemical_identifier (drug_name_as_string)
    logger.debug(' pharos says: {}'.format(pharos_ids) )

    # pubchem_ids = 
    pubchem_ids = pubchem_drug_name_to_chemical_identifier (drug_name_as_string)
    logger.debug(' pubchem says: {}'.format(pubchem_ids))

    # #TOTAL:
    chemical_ids_from_drug_names = ctd_ids + pharos_ids + pubchem_ids
    logger.debug( chemical_ids_from_drug_names )

    return [ { "id" : i, "label" : drug_name_as_string } for i in chemical_ids_from_drug_names ] if chemical_ids_from_drug_names else []
   


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