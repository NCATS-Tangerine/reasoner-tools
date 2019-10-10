import json
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
        'id': 'MONDO:0004979',
        'label': 'asthma',
        'type': 'disease'
      }
    ]
    lookup_w_sims_result = [
      {
        'id': 'MONDO:0004979',
        'label': 'asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0022742',
        'label': 'occupational asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0004765',
        'label': 'intrinsic asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0004784',
        'label': 'allergic asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0004766',
        'label': 'status asthmaticus',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0012607',
        'label': 'asthma-related traits, susceptibility to, 5',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0010940',
        'label': 'inherited susceptibility to asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0025556',
        'label': 'isocyanate induced asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0011805',
        'label': 'asthma-related traits, susceptibility to, 1',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0012067',
        'label': 'asthma-related traits, susceptibility to, 2',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0012771',
        'label': 'asthma-related traits, susceptibility to, 7',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0001491',
        'label': 'cough variant asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0005405',
        'label': 'childhood onset asthma',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0008835',
        'label': 'asthma, short stature, and elevated IgA',
        'type': 'disease'
      },
      {
        'id': 'MONDO:0008834',
        'label': 'asthma, nasal polyps, and aspirin intolerance',
        'type': 'disease'
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


# test 3
def test__find(bionames):
    """
    Validate the pass case for the _find method.
    """
    expected = [
      {
        'id': 'MONDO:0005737',
        'label': 'Ebola hemorrhagic fever',
        'type': 'disease'
      }
    ]
    query_key = 'ebola'
    concept_key = 'disease'
    result = bionames._find(query_key, concept_key)
    print(f"query_key={query_key}")
    print(f"concept_key={concept_key}")
    print(f"result={result}")
    paired_results = zip(result, expected)
    assert any(x == y for x, y in paired_results)


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
    print(f"result={json.dumps(result,indent=2)}")

    paired_results = zip(result, mon_result)
    assert any(x == y for x, y in paired_results)


# test 5
def test__search_onto(bionames):
    """
    Validates the pass case for _search_onto.
    """
    expected = [
      {
        "defined_by": "http://purl.obolibrary.org/obo/mondo.owl",
        "definition": "Townes-Brocks syndrome (TBS) is a rare genetic disorder characterized by the triad of imperforate anus, dysplastic ears often associated with sensorineural and/or conductive hearing impairment, and thumb malformations. These features are often associated with other signs mainly affecting the kidneys and heart.",
        "id": "MONDO:0007142",
        "label": "Townes-Brocks syndrome"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/chebi.owl",
        "definition": "A hydroxycalciol that is calcidiol in which the pro-S hydrogen of calcidiol is replaced by a hydroxy group. It is the active form of vitamin D3, produced fom calciol via hydoxylation in the liver to form calcidiol, which is subsequently oxidised in the kidney to give calcitriol.",
        "id": "CHEBI:17823",
        "label": "calcitriol"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/chebi.owl",
        "definition": "A nitrosamine that is dipropylamine in which the hydrogen attached to the nitrogen has been replaced by a nitroso group. It is a genotoxic carcinogen, targeting the lung, liver, thyroid, and kidney.",
        "id": "CHEBI:131518",
        "label": "N,N-bis(2-hydroxypropyl)nitrosamine"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/chebi.owl",
        "definition": "A hydroxy seco-steroid that is (5Z,7E)-9,10-secocholesta-5,7,10(19)-triene in which the pro-S hydrogen at position 3 has been replaced by a hydroxy group. It is the inactive form of vitamin D3, being hydroxylated in the liver to calcidiol (25-hydroxyvitamin D3), which is then further hydroxylated in the kidney to give calcitriol (1,25-dihydroxyvitamin D3), the active hormone.",
        "id": "CHEBI:28940",
        "label": "calciol"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/chebi.owl",
        "definition": "A hydroxycalciol that is calciol in which the hydrogen at position 25 has been replaced by a hydroxy group. A prehormone resulting from the oxidation of calciol in the liver, it is further hydroxylated in the kidney to give calcitriol, the active form of vitamin D3.",
        "id": "CHEBI:17933",
        "label": "calcidiol"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/chebi.owl",
        "definition": "A pregnane-based steroidal hormone produced by the outer-section (zona glomerulosa) of the adrenal cortex in the adrenal gland, and acts on the distal tubules and collecting ducts of the kidney to cause the conservation of sodium, secretion of potassium, increased water retention, and increased blood pressure. The overall effect of aldosterone is to increase reabsorption of ions and water in the kidney.",
        "id": "CHEBI:27584",
        "label": "aldosterone"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/go.owl",
        "definition": "Any process that activates or increases the frequency, rate or extent of cell proliferation involved in kidney development.",
        "id": "GO:1901724",
        "label": "positive regulation of cell proliferation involved in kidney development"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/go.owl",
        "definition": "The series of molecular signals initiated by binding of Wnt protein to a receptor on the surface of the target cell, resulting a change in cell state that contributes to the progression of the kidney over time.",
        "id": "GO:0061289",
        "label": "Wnt signaling pathway involved in kidney development"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/hp.owl",
        "definition": "A developmental defect in which a kidney is located in an abnormal anatomic position.",
        "id": "HP:0000086",
        "label": "Ectopic kidney"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/hp.owl",
        "definition": "Any structural anomaly of the kidney.",
        "id": "HP:0012210",
        "label": "Abnormal renal morphology"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/hp.owl",
        "definition": "An abnormal functionality of the kidney.",
        "id": "HP:0012211",
        "label": "Abnormal renal physiology"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/mondo.owl",
        "definition": "Any congenital anomaly of kidney and urinary tract in which the cause of the disease is a mutation in the TBX18 gene.",
        "id": "MONDO:0027676",
        "label": "congenital anomalies of kidney and urinary tract type 2"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/mondo.owl",
        "definition": "a medical condition characterized by major shock and renal failure after a crushing injury to skeletal muscle.",
        "id": "MONDO:0043549",
        "label": "crush syndrome"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/mondo.owl",
        "definition": "Emanuel syndrome is a constitutional genomic disorder due to the presence of a supernumerary derivative 22 chromosome and characterized by severe intellectual disability, characteristic facial dysmorphism (micrognathia, hooded eyelids, upslanting downslanting parebral fissures, deep set eyes, low hanging columnella and long philtrum), congenital heart defects and kidney abnormalities.",
        "id": "MONDO:0012176",
        "label": "Emanuel syndrome"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/mondo.owl",
        "id": "MONDO:0014629",
        "label": "autoimmune interstitial lung disease-arthritis syndrome"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/mondo.owl",
        "definition": "Cystinosis is a metabolic disease characterized by an accumulation of cystine inside the lysosomes, causing damage in different organs and tissues, particularly in the kidneys and eyes. Three clinical forms have been described: nephropathic infantile, nephropathic juvenile and ocular (see these terms).",
        "id": "MONDO:0016239",
        "label": "cystinosis"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/uberon.owl",
        "definition": "An organ that is located within the body cavity (or in its extension, in the scrotum); it consists of organ parts that are embryologically derived from endoderm, splanchnic mesoderm or intermediate mesoderm; together with other organs, the viscus constitutes the respiratory, gastrointestinal, urinary, reproductive and immune systems, or is the central organ of the cardiovascular system. Examples: heart, lung, esophagus, kidney, ovary, spleen.",
        "id": "UBERON:0002075",
        "label": "viscus"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/uberon.owl",
        "definition": "Paired organ that connects the primitive kidney Wolffian body (or mesonephros) to the cloaca and serves as the anlage for certain male reproductive organs. the Wolffian duct is what remains of the pronephric duct after the atrophy of the pronephros[WP]. In Zebrafish: Duct of the adult kidney (mesonephros), present bilaterally ventral to the somites and leading to the cloacal chamber[ZFA].",
        "id": "UBERON:0003074",
        "label": "mesonephric duct"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/uberon.owl",
        "definition": "The site of bicarbonate resorption in the adult kidney. It is equivalent to the convoluted distal segment of metanephric nephrons. [Xenbase]",
        "id": "UBERON:3010393",
        "label": "mesonephric late distal segment"
      },
      {
        "defined_by": "http://purl.obolibrary.org/obo/uberon.owl",
        "definition": "The valve-like structure found at the site of entry of the ureter into the urinary bladder, normally displays an oblique angulation through the detrusor to avoid reflux of urine up the ureters and the kidney",
        "id": "UBERON:0009973",
        "label": "ureterovesical junction"
      }
    ]

    query_key = 'kidney'
    result = bionames._search_onto(query_key)
    print(f"result={json.dumps(result,indent=2)}")
    assert all(item in result for item in expected)


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
