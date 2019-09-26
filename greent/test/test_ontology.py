import pytest
import requests
import os
import sys
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext


@pytest.fixture(scope='module')
def ontology():
    """
    Creates and returns a GenericOntology instance.
    For cases relying on .obo files, this ontology
    relies on the mondo.obo file.
    """
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


@pytest.fixture(scope='module')
def go_ontology():
    """
    Creates and returns a GenericOntology instance.
    For cases relying on .obo files, this ontology
    relies on the go.obo file.
    """
    url = "http://purl.obolibrary.org/obo/go.obo"
    ontology_file = "go.obo"
    if not os.path.exists (ontology_file):
        r = requests.get(url, stream=True)
        with open(ontology_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    return GenericOntology(ServiceContext.create_context(),
                           ontology_file)


@pytest.fixture(scope='module')
def hp_ontology():
    """
    Creates and returns an HP2 GenericOntology instance.
    For cases relying on .obo files, this ontology
    relies on the hp .obo file.
    """
    url = "http://purl.obolibrary.org/obo/hp.obo"
    ontology_file = "hp.obo"
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
    """Validate pass case of label function."""
    assert ontology.label('MONDO:0005737') == "Ebola hemorrhagic fever"

# test 2:
def test_go_label(go_ontology):
    """Validate pass case of label function."""
    assert go_ontology.label('GO:0005576') == "extracellular region"

# test 3
def test_hp_label(hp_ontology):
    """Validate pass case of label function."""
    assert hp_ontology.label('HP:0000175') == "Cleft palate"

# test 4
def test_is_a(ontology):
    """Validate pass case of is_a function."""
    assert ontology.is_a('MONDO:0005737', 'MONDO:0005762')


# test 5
def test_go_is_a(go_ontology):
    """Validate pass case of is_a function."""
    assert go_ontology.is_a('GO:0001025', 'GO:0140296')


# test 6
def test_hp_is_a(hp_ontology):
    """Validate pass case of is_a function."""
    assert hp_ontology.is_a('HP:0000552', 'HP:0011519')


# test 7
def test_xrefs(ontology):
    """Validate pass case of xrefs function."""
    xrefs = ontology.xrefs('MONDO:0005737')
    xref_ids = [ x['id'] for x in xrefs ]
    print (xref_ids)
    for i in [ "DOID:4325", "EFO:0007243", "ICD10:A98.4", "MedDRA:10014071", "MESH:D019142",
               "NCIT:C36171", "Orphanet:319218", "SCTID:37109004", "UMLS:C0282687" ]:
        assert i in xref_ids


# test 8
def test_go_xrefs(go_ontology):
    """Validate pass case of xrefs function."""
    xrefs = go_ontology.xrefs('GO:0005576')
    xref_ids = [ x['id'] for x in xrefs ]
    print (f"xref_ids={xref_ids}")
    for x in [ "MIPS_funcat:70.27","Wikipedia:Extracellular" ]:
        assert x in xref_ids


# test 9
def test_hp_xrefs(hp_ontology):
    """Validate pass case of xrefs function."""
    xrefs = hp_ontology.xrefs('HP:0000175')
    xref_ids = [ x['id'] for x in xrefs ]
    print (f"xref_ids={xref_ids}")
    for x in [ "Fyler:4876", "MSH:D002972", "SNOMEDCT_US:63567004",
               "SNOMEDCT_US:87979003", "UMLS:C0008925", "UMLS:C2981150" ]:
        assert x in xref_ids


# test 10
def test_synonyms(ontology):
    """Validate pass case of synonyms function."""
    syns = ontology.synonyms ('MONDO:0005737')
    received = []
    for s in syns:
        received = received + s.xref
    for expected in [ "DOID:4325",
                      "Orphanet:319218",
                      "NCIT:C36171",
                      "MONDO:patterns/specific_infectious_disease_by_agent" ]:
        assert expected in received


# test 11
def test_synonyms(go_ontology):
    """Validate pass case of synonyms function."""
    syns = go_ontology.synonyms ('GO:0005575')
    received = []
    for s in syns:
        received = received + s.xref
    assert "NIF_Subcellular:nlx_subcell_100315" in received


# test 12
def test_synonyms(hp_ontology):
    """Validate pass case of synonyms function."""
    syns = hp_ontology.synonyms ('HP:0000175')
    received = []
    for s in syns:
        received = received + s.xref
    for expected in [ "Facebase",
                      "ORCID:0000-0001-5208-3432",
                      "ORCID:0000-0001-5889-4463" ]:
        assert expected in received


# test 13
def test_search(ontology):
    """Validate pass case of search function."""
    result = ontology.search ('ebola', ignore_case=True)
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    # Need to check all id's returned for this one.
    assert result[0]['id'] == 'MONDO:0005737'


# test 14
def test_go_search(go_ontology):
    """Validate pass case of search function."""
    result = go_ontology.search ('subcellular entity', ignore_case=True)
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    # Need to check all id's returned for this one.
    assert result[0]['id'] == 'GO:0005575'


# test 15
def test_hp_search(hp_ontology):
    """Validate pass case of search function."""
    result = hp_ontology.search ('cleft palate', ignore_case=True)
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    received = list()
    # Need to check all id's returned for this one.
    assert result[0]['id'] == 'HP:0000175'


# test 16
def test_lookup(ontology):
    """Validate pass case of lookup function."""
    result = ontology.lookup ('UMLS:C0282687')
    assert result[0]['id'] == 'MONDO:0005737'


# test 17
def test_go_lookup(go_ontology):
    """Validate FAIL case of lookup function.
       Couldn't find any pass cases for GO.
    """
    result = go_ontology.lookup ('GO:0001102')
    assert not len(result)


# test 18
def test_hp_lookup(hp_ontology):
    """Validate pass case of lookup function."""
    result = hp_ontology.lookup ('UMLS:C0152427')
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    assert result[0]['id'] == 'HP:0010442'


# test 19
def test_id_list(ontology):
    """Validate pass and fail cases of id_list function."""
    result = ontology.id_list('MONDO')
    assert result is not None

    result2 = ontology.id_list('A BAD ONTOLOGY')
    assert result2 is None


# test 20
def test_go_id_list(go_ontology):
    """Validate pass case of GO id_list function."""
    result = go_ontology.id_list('GO')
    assert result is not None


# test 21
def test_hp_id_list(hp_ontology):
    """Validate pass case of HP id_list function."""
    result = hp_ontology.id_list('HP')
    assert result is not None


# test 22
def test_exactMatch(ontology):
    """Validate pass case of exactMatch function."""
    result = ontology.exactMatch('MONDO:0004634')
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    matches = [
        "DOID:866",
        "snomedct:90507008",
        "umls:C0235522"
    ]
    for m in matches:
        assert m in result


# test 23
def test_go_exactMatch(go_ontology):
    """Validate FAIL case of exactMatch function.
    Couldn't find any pass cases for GO.
    """
    result = go_ontology.exactMatch('GO:0032411')
    assert not len(result)


# test 24
def test_hp_exactMatch(hp_ontology):
    """Validate FAIL case of exactMatch function.
    Couldn't find any pass cases for HP.
    """
    result = hp_ontology.exactMatch('HP:0000113')
    assert not len(result)


# test 25
def test_closeMatch(ontology):
    """Validate pass case of closeMatch function."""
    result = ontology.closeMatch('MONDO:0004634')
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    matches = [
        "snomedct:195435006",
        "umls:C0155774"
    ]
    for m in matches:
        assert m in result


# test 26
def test_go_closeMatch(go_ontology):
    """Validate FAIL case of exactMatch function.
    Couldn't find any pass cases for GO.
    """
    result = go_ontology.closeMatch('GO:0000405')
    assert not len(result)


# test 27
def test_hp_closeMatch(hp_ontology):
    """Validate FAIL case of exactMatch function.
    Couldn't find any pass cases for HP.
    """
    result = hp_ontology.closeMatch('HP:0000113')
    assert not len(result)


# test 28
def test_subterms(ontology):
    """Validate pass case of subterm function."""
    result = ontology.subterms('MONDO:0004634')
    for r in [ "MONDO:0004871","MONDO:0000492","MONDO:0001221","MONDO:0001148","MONDO:0001954",
               "MONDO:0001498","MONDO:0004206","MONDO:0004872","MONDO:0005928","MONDO:0004208",
               "MONDO:0002996","MONDO:0004625","MONDO:0021643","MONDO:0021644","MONDO:0021642",
               "MONDO:0001339","MONDO:0041093","MONDO:0001733","MONDO:0021645","MONDO:0004869",
               "MONDO:0002303","MONDO:0021064","MONDO:0015196","MONDO:0021257","MONDO:0006291",
               "MONDO:0003032","MONDO:0004873","MONDO:0002800","MONDO:0008638","MONDO:0001481",
               "MONDO:0000945"]:
        assert r in result


# test 29
def test_go_subterms(go_ontology):
    """Validate pass case of subterm function."""
    result = go_ontology.subterms('GO:0099116')
    for x in [ "GO:0097745", "GO:0008193", "GO:0001682" ]:
      assert x in result


# test 30
def test_hp_subterms(hp_ontology):
    """Validate pass case of subterm function."""
    result = hp_ontology.subterms('HP:0011186')
    assert "HP:0010853" in result


# test 31
def test_superterms(ontology):
    """Validates pass case of superterms search for a curie"""
    result = ontology.superterms('MONDO:0004634')
    print(f"result={result}")
    superterms = [
        "MONDO:0021199",
        "MONDO:0004995",
        "MONDO:0005385",
        "MONDO:0000001"
    ]
    for s in superterms:
        assert s in result


# test 32
def test_go_superterms(go_ontology):
    """Validates pass case of superterms search for a curie"""
    result = go_ontology.superterms('GO:0005576')
    print(f"result={result}")
    assert result[0] == "GO:0005575"


# test 33
def test_hp_superterms(hp_ontology):
    """Validates pass case of superterms search for a curie"""
    result = hp_ontology.superterms('HP:0000175')
    print(f"result={result}")
    superterms = [
        "HP:0031816",
        "HP:0000163",
        "HP:0100737",
        "HP:0000271",
        "HP:0000174",
        "HP:0000234",
        "HP:0000152",
        "HP:0000153",
        "HP:0000202",
        "HP:0000118",
        "HP:0000001"
    ]
    for s in superterms:
        assert s in result


# test 34
def test_mondo_single_level_is_a(ontology):
    """Validates pass case of single_level_is_a for MONDO"""
    mondo_result = ontology.single_level_is_a('MONDO:0004979')
    for m in ["MONDO:0001491", "MONDO:0004765", "MONDO:0004766",
              "MONDO:0004784", "MONDO:0005405", "MONDO:0022742"]:
        assert m in mondo_result


# test 35
def test_go_single_level_is_a(go_ontology):
    go_result = go_ontology.single_level_is_a('GO:0005575')
    print(f"{go_result}")
    for g in ["GO:0044422","GO:0016020","GO:0043226","GO:0044464","GO:0005576","GO:0032991","GO:0019012",
              "GO:0044423","GO:0031974","GO:0044217","GO:0044425","GO:0044456","GO:0005623","GO:0055044",
              "GO:0045202","GO:0009295","GO:0099080","GO:0097423","GO:0044421","GO:0030054"]:
        assert g in go_result


# test 36
def test_hp_single_level_is_a(hp_ontology):
    result = hp_ontology.single_level_is_a('HP:0000175')
    print(f"result={result}")
    for h in ["HP:0000185","HP:0009099","HP:0100338","HP:0410005","HP:0410031"]:
        assert h in result


# test 37
def test_parents(ontology):
    """Validates pass case of retrieving parents for a curie"""
    result = ontology.parents('MONDO:0004634')
    assert 'MONDO:0005385' in result


# test 38
def test_go_parents(go_ontology):
    """Validates pass case of retrieving parents for a curie"""
    result = go_ontology.parents('GO:0005576')
    assert 'GO:0005575' in result


# test 39
def test_hp_parents(hp_ontology):
    """Validates pass case of retrieving parents for a curie"""
    result = hp_ontology.parents('HP:0000175')
    parents = [
        "HP:0000202",
        "HP:0100737"
    ]
    for p in parents:
        assert p in result


# test 40
def test_descendants(ontology):
    """Validates pass case of retrieving descendants for a curie
       Only check for mondo curies due to limitation of unit test
    """
    result = ontology.descendants('MONDO:0004979')
    print(f"result= {result}")

    descendants = [
        "MONDO:0001491",
        "MONDO:0004765",
        "MONDO:0004766",
        "MONDO:0004784",
        "MONDO:0005405",
        "MONDO:0022742",
        "MONDO:0025556"#,
        #"MONDO:0004979",
        #"C0038218",
        #"C0155877",
        #"C0155880",
        #"C0264408",
        #"C0264423",
        #"C0694548",
        #"C1321273",
        #"DOID:9415",
        #"SCTID:389145006",
        #"COHD:313236",
        #"COHD:4145497",
        #"COHD:45769438",
        #"DOID:0040041",
        #"DOID:12323",
        #"DOID:9360",
        #"DOID:9362",
        #"ICD10:J45.991",
        #"ICD10:J46",
        #"ICD9:493.82",
        #"ICD9:493.91",
        #"MESH:D013224",
        #"MESH:D059366",
        #"SCTID:409663006",
        #"NCIT:C122577",
        #"SCTID:233678006",
        #"SCTID:266361008",
        #"SCTID:708090002",
        #"EFO:0004591",
        #"EFO:0008590",
        #"SCTID:404808000",
        #"SCTID:57607007"
    ]
    for d in descendants:
        assert d in result


# test 41
def test_go_descendants(go_ontology):
    """Validates pass case of retrieving descendants for a curie"""
    result = go_ontology.descendants('GO:0005576')
    print(f"result= {result}")

    descendants = [
        "GO:0043083",
        "GO:0048046",
        "GO:0098595",
        "GO:0099544"
    ]
    for d in descendants:
        assert d in result


# test 42
def test_hp_descendants(hp_ontology):
    """Validates pass case of retrieving descendants for a curie"""
    result = hp_ontology.descendants('HP:0000175')
    print(f"result= {result}")

    descendants = [
        "HP:0000176",
        "HP:0000185",
        "HP:0002744",
        "HP:0008501",
        "HP:0009094",
        "HP:0009099",
        "HP:0010289",
        "HP:0011819",
        "HP:0100334",
        "HP:0100337",
        "HP:0100338",
        "HP:0410005",
        "HP:0410031",
        "HP:0410032",
        "HP:0410033",
        "HP:0410034"
    ]
    for d in descendants:
        assert d in result


# test 43
def test_children(ontology):
    """Validates pass case of retrieving children for a curie
       Only check for mondo curies due to limitation of unit test
    """
    result = ontology.children('MONDO:0000544')
    print(f"result={result}")

    children = [
        "MONDO:0002988",
        "MONDO:0006489"#,
        #"C0877611",
        #"C2004576",
        #"DOID:4413",
        #"GARD:0009664",
        #"NCIT:C27394",
        #"NCIT:C40239",
        #"ONCOTREE:VMM",
        #"EFO:1000619"
    ]
    for c in children:
        assert c in result


# test 44
def test_go_children(go_ontology):
    """Validates pass case of retrieving children for a curie"""
    result = go_ontology.children('GO:0005576')
    print(f"result={result}")
    children = [
        "GO:0043083",
        "GO:0048046",
        "GO:0098595",
        "GO:0099544"
    ]
    for c in children:
        assert c in result


# test 45
def test_hp_children(hp_ontology):
    """Validates pass case of retrieving children for a curie"""
    result = hp_ontology.children('HP:0000175')
    print(f"result={result}")
    children = [
        "HP:0000185",
        "HP:0009099",
        "HP:0100338",
        "HP:0410005",
        "HP:0410031"
    ]
    for c in children:
        assert c in result


# test 46
def test_siblings(ontology):
    """Validates pass case of retrieving siblings for a curie"""
    result = ontology.siblings('MONDO:0004634')
    print(f"result={result}")
    siblings = [
        "MONDO:0000473",
        "MONDO:0000701",
        "MONDO:0000831",
        "MONDO:0001065",
        "MONDO:0001574",
        "MONDO:0002322",
        "MONDO:0002405",
        "MONDO:0003159",
        "MONDO:0004634",
        "MONDO:0005053",
        "MONDO:0005294",
        "MONDO:0005399",
        "MONDO:0005568",
        "MONDO:0005979",
        "MONDO:0008895",
        "MONDO:0016469",
        "MONDO:0017215",
        "MONDO:0017311",
        "MONDO:0017818",
        "MONDO:0018870",
        "MONDO:0018882",
        "MONDO:0019063",
        "MONDO:0019293",
        "MONDO:0019748",
        "MONDO:0020672",
        "MONDO:0020674",
        "MONDO:0020676",
        "MONDO:0021080",
        "MONDO:0021658",
        "MONDO:0022293",
        "MONDO:0023152",
        "MONDO:0024471",
        "MONDO:0036870",
        "MONDO:0043218",
        "MONDO:0043287"
    ]
    for s in siblings:
        assert s in result


# test 47
def test_go_siblings(go_ontology):
    """Validates pass case of retrieving siblings for a curie"""
    result = go_ontology.siblings('GO:0099017')
    print(f"result={result}")

    siblings =  [
        "GO:0007016",
        "GO:0032065",
        "GO:0042989",
        "GO:0045053",
        "GO:0072595",
        "GO:0072658",
        "GO:0090286",
        "GO:0099017",
        "GO:1990153",
        "GO:0001411",
        "GO:0031520",
        "GO:0035838",
        "GO:0035839",
        "GO:0043332",
        "GO:0051285",
        "GO:0099017"
    ]

    for s in siblings:
        assert s in result



# test 48
def test_hp_siblings(hp_ontology):
    """Validates pass case of retrieving siblings for a curie"""
    result = hp_ontology.siblings('HP:0000407')
    print(f"result={result}")

    siblings =  [
        "HP:0000405",
        "HP:0000407",
        "HP:0001730",
        "HP:0005101",
        "HP:0008542",
        "HP:0009900",
        "HP:0011975",
        "HP:0012712",
        "HP:0012713",
        "HP:0012714",
        "HP:0012715",
        "HP:0012779",
        "HP:0012781",
        "HP:0000407",
        "HP:0001751"
    ]

    for s in siblings:
        assert s in result



# Property_value has defect: In some cases, will cut off first and last chars of returned property value.
# test 49
def test_property_value(ontology):
    """Validates pass case of retrieving properties for a given curie and key"""
    result = ontology.property_value("MONDO:0000212","exactMatch")
    print(f"result={result}")
    assert result  == "ttp://identifiers.org/mesh/C56299"


# Property_value has defect: In some cases, will cut off first and last chars of returned property value.
# test 50
def test_go_property_value(go_ontology):
    """Validates pass case of retrieving properties for a given curie and key"""
    result = go_ontology.property_value("GO:0099017", "http://purl.org/dc/elements/1.1/creator")
    print(f"result={result}")
    assert result  == "dos"


# Property_value has defect: In some cases, will cut off first and last chars of returned property value.
# test 51
def test_hp_property_value(hp_ontology):
    """Validates pass case of retrieving properties for a given curie and key"""
    result = hp_ontology.property_value("HP:0025078", "http://purl.org/dc/elements/1.1/date")
    print(f"result={result}")
    assert result  == "016-09-26T10:52:41"


# test 52
def test_all_properties(ontology):
    """Validates pass case of retrieving all_properties for a curie"""
    result = ontology.all_properties('MONDO:0004979')
    assert result['id'][0] == "MONDO:0004979"
    assert result['is_a'][0] == 'MONDO:0001358 {source="DOID:2841", source="EFO:0000270", source="MESH:D001249"}'

    xref_str_list = [
        'COHD:317009 {source="MONDO:equivalentTo"}',
        'DOID:2841 {source="MONDO:equivalentTo", source="EFO:0000270"}',
        'EFO:0000270 {source="MONDO:equivalentTo", source="DOID:2841"}',
        'GARD:0010246 {source="MONDO:equivalentTo"}',
        'HP:0002099 {source="MONDO:otherHierarchy"}',
        'ICD10:J45 {source="MONDO:equivalentTo", source="DOID:2841"}',
        'ICD10:J45.90 {source="DOID:2841"}',
        'ICD10:J45.909 {source="DOID:2841"}',
        'ICD9:493 {source="DOID:2841", source="EFO:0000270"}',
        'ICD9:493.81 {source="MONDO:equivalentTo", source="i2s"}',
        'ICD9:493.9 {source="DOID:2841"}',
        'KEGG:05310 {source="MONDO:equivalentTo", source="DOID:2841"}',
        'MESH:D001249 {source="MONDO:equivalentTo", source="DOID:2841", source="EFO:0000270"}',
        'NCIT:C28397 {source="MONDO:equivalentTo", source="DOID:2841", source="EFO:0000270"}',
        'SCTID:31387002 {source="MONDO:kboom-pr-0.90/0.77/0.32", source="MONDO:equivalentTo"}',
        'UMLS:C0004096 {source="NCIT:C28397", source="MONDO:equivalentTo", source="DOID:2841"}'
    ]

    xref_result_list = result['xref']
    for s in xref_str_list:
        print(s)
        assert s in xref_result_list

    pv_str_list = [
        'closeMatch http://identifiers.org/snomedct/155574008',
        'closeMatch http://identifiers.org/snomedct/155579003',
        'closeMatch http://identifiers.org/snomedct/187687003',
        'closeMatch http://identifiers.org/snomedct/195967001',
        'closeMatch http://identifiers.org/snomedct/195979001',
        'closeMatch http://identifiers.org/snomedct/195983001',
        'closeMatch http://identifiers.org/snomedct/21341004',
        'closeMatch http://identifiers.org/snomedct/266365004',
        'closeMatch http://identifiers.org/snomedct/266398009',
        'closeMatch http://identifiers.org/snomedct/278517007',
        'exactMatch DOID:2841',
        'exactMatch http://identifiers.org/mesh/D001249',
        'exactMatch http://identifiers.org/snomedct/31387002',
        'exactMatch http://linkedlifedata.com/resource/umls/id/C0004096',
        'exactMatch NCIT:C28397'
    ]

    pv_result_list = result['property_value']
    for s in pv_str_list:
        print(s)
        assert s in pv_result_list


# test 53
def test_go_all_properties(go_ontology):
    """Validates pass case of retrieving all_properties for a curie"""
    result = go_ontology.all_properties('GO:0001682')
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    assert result['id'][0] == "GO:0001682"
    assert result['is_a'][0] == "GO:0099116"
    assert result['namespace'][0] == "biological_process"


# test 54
def test_hp_all_properties(hp_ontology):
    """Validates pass case of retrieving all_properties for a curie"""
    result = hp_ontology.all_properties('HP:0000607')
    print(f"result={result}")
    sys.stdout.flush()
    sys.stderr.flush()
    assert result['id'][0] == "HP:0000607"
    for x in [ "HP:0000606", "HP:0100678" ]:
        assert x in result['is_a']
    assert result['xref'][0] == "UMLS:C1844605"
    
