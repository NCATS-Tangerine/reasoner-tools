import pytest
import requests
import os
import sys
import traceback
import logging
from greent.service import Service
from greent.servicecontext import ServiceContext
from greent.services.bionames import BioNames
from builder.lookup_utils import chemical_ids_from_drug_names

@pytest.fixture(scope='module')
def bionames():
    """
    Create a bionames instance for passing in to the test functions.
    """
    return BioNames(ServiceContext.create_context())


# test 1
def test_lookup_router(bionames):
    """
    Validates the pass case for the lookup_router method for both the
    include similar and don't include similar boolean cases.
    """
    query_key = 'asthma'
    concept_key = 'disease'

    lookup_no_sims_result = [
      {
        "id": "MONDO:0004979",
        "label": "asthma",
        "type": "disease"
      }
    ]
    lookup_w_sims_result = [
      {
        "id": "MONDO:0004979",
        "label": "asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0022742",
        "label": "occupational asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0004765",
        "label": "intrinsic asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0004784",
        "label": "allergic asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0004766",
        "label": "status asthmaticus",
        "type": "disease"
      },
      {
        "id": "MONDO:0012607",
        "label": "asthma-related traits, susceptibility to, 5",
        "type": "disease"
      },
      {
        "id": "MONDO:0010940",
        "label": "inherited susceptibility to asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0025556",
        "label": "isocyanate induced asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0011805",
        "label": "asthma-related traits, susceptibility to, 1",
        "type": "disease"
      },
      {
        "id": "MONDO:0012067",
        "label": "asthma-related traits, susceptibility to, 2",
        "type": "disease"
      },
      {
        "id": "MONDO:0012771",
        "label": "asthma-related traits, susceptibility to, 7",
        "type": "disease"
      },
      {
        "id": "MONDO:0001491",
        "label": "cough variant asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0005405",
        "label": "childhood onset asthma",
        "type": "disease"
      },
      {
        "id": "MONDO:0008835",
        "label": "asthma, short stature, and elevated IgA",
        "type": "disease"
      },
      {
        "id": "MONDO:0008834",
        "label": "asthma, nasal polyps, and aspirin intolerance",
        "type": "disease"
      }
    ]

    result = bionames.lookup_router(query_key, concept_key)

    print(f"query_key={query_key}")
    print(f"concept_key={concept_key}")
    print(f"result={result}")

    unique_result = [x for x in result if x['label'] == query_key]
    print(f"unique_result={unique_result}")
    assert unique_result == lookup_no_sims_result

    full_result = zip(result, lookup_w_sims_result)
    assert any(x == y for x, y in full_result)


# test 2
def test__find_chemical_substance(bionames):
    """
    Validates pass case for the find_chemical_substance method.
    """
    query_key = 'nicotine'
    concept_key = 'chemical_substance'

    cs_result = [
      {
        'defined_by': 'http://purl.obolibrary.org/obo/chebi.owl',
        'definition': 'A racemate composed of equimolar amounts of (R)- and (S)-nicotine.',
        'id': 'CHEBI:18723',
        'label': 'nicotine'
      },
      {
        'id': 'PUBCHEM:89594',
        'label': 'nicotine'
      },
      {
        'id': 'MESH:D009538',
        'label': 'nicotine'
       }
    ]

    result = bionames._find_chemical_substance(query_key, concept_key)
    print(f"query_key={query_key}")
    print(f"concept_key={concept_key}")
    print(f"result={result}")

    paired_results = zip(result, cs_result)
    assert any(x == y for x, y in paired_results)


# TODO
# test 3
def test__find(bionames):
    """
    Validate the pass case for the _find method.
    """
    assert True


# test 4
def test__search_monarch(bionames):
    """
    Validates the pass case for the _search_monarch method.
    """
    query_key = 'ebola'
    concept_key = 'disease'
    mon_result = [
      {

        'id': 'MONDO:0005737',
        'label': 'Ebola hemorrhagic fever',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0018087',
        'label': 'viral hemorrhagic fever',
        'type': 'disease'
      }
    ]

    result = bionames._search_monarch(query_key, concept_key)
    print(f"query_key={query_key}")
    print(f"concept_key={concept_key}")
    print(f"result={result}")

    paired_results = zip(result, mon_result)
    assert any(x == y for x, y in paired_results)


# TODO
# test 5
def test__search_onto(bionames):
    """
    Validates the pass case for _search_onto.
    """
    query_key = 'digestion'
    concept_key = 'biological_process_or_activity'
    result = bionames._search_onto(query_key)
    print(f"query_key={query_key}")
    print(f"concept_key={concept_key}")
    print(f"result={result}")
    assert True


# test 6
def test_ID_to_label_lookup(bionames):
    """
    Validates pass case of ID_to_label_lookup method for onto, mesh, and hgnc
    cases, which exercises all branches of the method (MONDO exercises onto).
    """
    onto_expected_result = [
      {
        "id": "MONDO:0004634",
        "label": "vein disease"
      }
    ]
    hgnc_expected_result = [
      {
         "id": "HGNC:3449",
         "label": "ERN1"
      }
    ]
    mesh_expected_result = [
      {
        "id": "MESH:D001241",
        "label": "Aspirin"
      }
    ]

    onto_id = 'MONDO:0004634'
    onto_result = bionames.ID_to_label_lookup(onto_id)
    paired_results1 = zip(onto_result, onto_expected_result)
    assert any(x == y for x, y in paired_results1)

    mesh_id = 'MESH:D001241'
    mesh_result = bionames.ID_to_label_lookup(mesh_id)
    paired_results2 = zip(mesh_result, mesh_expected_result)
    assert any(x == y for x, y in paired_results2)

    hgnc_id = 'HGNC:3449'
    hgnc_result = bionames.ID_to_label_lookup(hgnc_id)
    paired_results3 = zip(hgnc_result, hgnc_expected_result)
    assert any(x == y for x, y in paired_results3)
