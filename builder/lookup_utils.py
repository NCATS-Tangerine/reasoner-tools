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
    
    CTD_query_url = 'http://ctdbase.org/tools/batchQuery.go?'
    CTD_query_details = {'inputType':'chem', 'inputTerms': drug_name_as_string, 'report':'genes_curated','format':'json'}
    
    CTD_query_results = requests.get(CTD_query_url, params = CTD_query_details).json()
    
    exact_matches_from_CTD_query_results = [ x for x in CTD_query_results if x['ChemicalName'].upper() == drug_name_as_string.upper()]
    related_matches_from_CTD_query_results = [x for x in CTD_query_results if x['ChemicalName'].upper() != drug_name_as_string.upper()]
    
    exact_match_IDs_from_CTD_query =['CTD exact match IDs:']+[q['ChemicalId'] for q in exact_matches_from_CTD_query_results]
    
    related_match_IDs_from_CTD_query = ['CTD related match IDs:']+[p['ChemicalId'] for p in related_matches_from_CTD_query_results]
    
    all_ctd_results = exact_match_IDs_from_CTD_query + related_match_IDs_from_CTD_query
    return all_ctd_results

# pharos query a string drug_name to return chemical IDs ... same model as fcn above, CTD_drug_name_string_to_drug_identifier

def pharos_drug_name_to_chemical_identifier(drug_name_as_string):

    pharos_query_url = 'https://pharos.nih.gov/idg/api/v1/ligands/search?'
    pharos_query_details = {'q': 'aspirin'}

    pharos_query_results = requests.get(pharos_query_url, params = pharos_query_details).json()
    
    #this way, below, reduces the number of list comprehensions by half from the above method 'ctd_drug_name_to_chemical_identifier'... i think
    exact_matches_from_pharos_search_results = [x['id'] for x in pharos_query_results['content'] if x['name'].upper() == drug_name_as_string.upper()]
   
    related_matches_from_pharos_search_results = [x['id'] for x in pharos_query_results['content'] if x['name'].upper() != drug_name_as_string.upper()]
    all_pharos_results = ['pharos exact match IDs:']+ exact_matches_from_pharos_search_results + ['pharos related match IDs:'] +related_matches_from_pharos_search_results
    return all_pharos_results


def pubchem_drug_name_to_chemical_identifier(drug_name_as_string):

    pubchem_query_url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name_as_string}/property/MolecularFormula/JSON'
    
    pubchem_query_results = requests.get(pubchem_query_url).json()
    test = pubchem_query_results['PropertyTable']['Properties']
   
    matches_from_pubchem_search_results = [x['CID'] for x in pubchem_query_results['PropertyTable']['Properties']]
    all_pubchem_results = ['pubchem IDs:'] + matches_from_pubchem_search_results
    return all_pubchem_results




def chemical_ids_from_drug_names( drug_name ):
    """Look up drugs by name.  We will pull results from multiple sources in this case,
    and return them all."""
    
    logger=logging.getLogger('application')
    logger.debug('Looking up drug name: {}'.format(drug_name) )
    
    #CTD_ids
    ctd_ids = ctd_drug_name_string_to_chemical_identifier( drug_name )
    logger.debug(' CTD says: {}'.format(ctd_ids) )

    #pharos_ids = 
    pharos_ids = pharos_drug_name_to_chemical_identifier (drug_name)
    logger.debug(' pharos says: {}'.format(pharos_ids) )

    #pubchem_ids = 
    pubchem_ids = pubchem_drug_name_to_chemical_identifier (drug_name)
    logger.debug(' pubchem says: {}'.format(pubchem_ids))

    # #PHAROS
    # pids_and_labels = greent.pharos.drugname_string_to_pharos_info( drug_name )
    # pharos_ids = [x[0] for x in pids_and_labels]
    # logger.debug(' Pharos says: {}'.format(pharos_ids) )

    # #PUBCHEM
    # pubchem_info = greent.chembio.drugname_to_pubchem( drug_name )
    # pubchem_ids = [ 'PUBCHEM:{}'.format(r['drugID'].split('/')[-1]) for r in pubchem_info ]
    # logger.debug(' pubchem says: {}'.format(pubchem_ids))
    # #TOTAL:
    chemical_ids_from_drug_names =  jsonify(ctd_ids + pharos_ids + pubchem_ids)
    logger.debug( chemical_ids_from_drug_names )
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
