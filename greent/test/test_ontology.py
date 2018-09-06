import pytest
import requests
import os
#import json
#from greent.graph_components import KNode
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

# setup fcn, not a test ... 
# oh ok... the fcn below creates an object called 'ontology' of
# type "GenericOntology" with all its various associated properties

def ontology():
    url = "http://purl.obolibrary.org/obo/mondo.obo"
    ontology_file = "mondo.obo"
    if not os.path.exists (ontology_file):
        
        r = requests.get(url, stream=True)
        with open(ontology_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    
        
    return GenericOntology(ServiceContext.create_context(),
                           ontology_file)

# test 1: 
# checks that some identifier (alpha-numerical) for the ontology object
# is associated with an english-word name as expected
def test_label(ontology):
    assert ontology.label('MONDO:0005737') == "Ebola hemorrhagic fever"

# test 2
# 
def test_is_a(ontology):
    assert ontology.is_a('MONDO:0005737', 'MONDO:0005762')

# test 3

def test_xrefs(ontology):
    xrefs = ontology.xrefs('MONDO:0005737')
    xref_ids = [ x['id'] for x in xrefs ]
    print (xref_ids)
    for i in [ "DOID:4325", "EFO:0007243", "ICD10:A98.4", "MedDRA:10014071", "MESH:D019142", "NCIT:C36171", "Orphanet:319218", "SCTID:37109004", "UMLS:C0282687" ]:
        assert i in xref_ids

# test 4

def test_synonyms(ontology):
    syns = ontology.synonyms ('MONDO:0005737')
    received = []
    for s in syns:
        received = received + s.xref
    for expected in [ "DOID:4325",
                      "Orphanet:319218",
                      "SCTID:186746000",
                      "NCIT:C36171" ]:
        assert expected in received

# test 5

def test_search(ontology):
    result = ontology.search ('ebola', ignore_case=True)
    assert result[0]['id'] == 'MONDO:0005737'

# test 6

def test_lookup(ontology):
    result = ontology.lookup ('UMLS:C0282687')
    assert result[0]['id'] == 'MONDO:0005737'

# test 7

def test_id_list(ontology):
    result = ontology.id_list('MONDO')
    assert result is not None

    result2 = ontology.id_list('A BAD ONTOLOGY')
    assert result2 is None

# test 8 

def test_exactMatch(ontology):
    result = ontology.exactMatch('MONDO:0004634')
    assert result[-1] == "umls:C0235522"

# test 9

def test_closeMatch(ontology):
    result = ontology.closeMatch('MONDO:0004634')
    assert result[-1] == "umls:C0155774"

# test 10

# def test_ancestors(ontology):
#     result = ontology.ancestors('MONDO:0005586')
#     assert 'MONDO:0000500' in result

# test 11

# def test_descendants(ontology):
#     result = ontology.descendants('MONDO:0000500')
#     assert 'MONDO:0005586' in result
    
# test 12

def test_parents(ontology):
    result = ontology.parents('MONDO:0004634')
    assert 'MONDO:0005385' in result