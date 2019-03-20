import pytest
import requests
import os
#import json
#from greent.graph_components import KNode
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

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

def test_subterms(ontology):
    result = ontology.subterms('MONDO:0004634')
    for x in [
    "MONDO:0004872",
    "MONDO:0021642",
    "MONDO:0006291",
    "MONDO:0021643",
    "MONDO:0003032",
    "MONDO:0005928",
    "MONDO:0001221",
    "MONDO:0000492",
    "MONDO:0001481",
    "MONDO:0004873",
    "MONDO:0004871",
    "MONDO:0000945",
    "MONDO:0001498",
    "MONDO:0021644",
    "MONDO:0004869",
    "MONDO:0021257",
    "MONDO:0002996",
    "MONDO:0021064",
    "MONDO:0041093",
    "MONDO:0001339",
    "MONDO:0002800",
    "MONDO:0001954",
    "MONDO:0004625",
    "MONDO:0002303",
    "MONDO:0015196",
    "MONDO:0004206",
    "MONDO:0004208",
    "MONDO:0001148",
    "MONDO:0008638",
    "MONDO:0021645"
      ]:
      assert x in result

# test 10
# def test_ancestors(ontology):
#     result = ontology.ancestors('MONDO:0005586')
#     assert 'MONDO:0000500' in result

# test 11
# def test_descendants(ontology):
#     result = ontology.descendants('MONDO:0000500')
#     assert 'MONDO:0005586' in result
    
# test 12
# def test_parents(ontology):
#     result = ontology.parents('MONDO:0004634')
#     assert 'MONDO:0005385' in result

# def test_single_level_is_a(ontology):
#     mondo_result = ontology.single_level_is_a('MONDO:0004979')
#     assert ["MONDO:0001491", "MONDO:0004765", "MONDO:0004766", "MONDO:0004784", "MONDO:0005405", "MONDO:0010940" ] in mondo_result

#     go_result = ontology.single_level_is_a('GO:0005575')
#     assert [ "GO:0044422","GO:0016020","GO:0044215","GO:0043226","GO:0044464","GO:0005576","GO:0032991","GO:0019012",
#     "GO:0044423",
#     "GO:0031974",
#     "GO:0044217",
#     "GO:0044425",
#     "GO:0044456",
#     "GO:0005623",
#     "GO:0055044",
#     "GO:0045202",
#     "GO:0009295",
#     "GO:0099080",
#     "GO:0097423",
#     "GO:0044421",
#     "GO:0030054"
#   ] in go_result

#     chebi_result = ontology.single_level_is_a('CHEBI:48565')
#     assert  [
#     "CHEBI:48562",
#     "CHEBI:10093",
#     "CHEBI:48567"
#   ] in chebi_result

# def test_descendants(ontology):
    
#     mondo_result = ontology.descendants('MONDO:0004979')
#     assert [
#     "MONDO:0001491",
#     "MONDO:0004765",
#     "MONDO:0004766",
#     "MONDO:0004784",
#     "MONDO:0005405",
#     "MONDO:0010940",
#     "MONDO:0025556",
#     "MONDO:0011805",
#     "MONDO:0012067",
#     "MONDO:0012379",
#     "MONDO:0012577",
#     "MONDO:0012607",
#     "MONDO:0012666",
#     "MONDO:0012771",
#     "MONDO:0013180"
#   ] in mondo_result

#     chebi_result = ontology.descendants('CHEBI:48565')
#     assert [
#     "CHEBI:48562",
#     "CHEBI:10093",
#     "CHEBI:48567"
#   ] in chebi_result
