import pytest
import requests
import os
from greent.services.pubchem import PubChem
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

def pubchem():
    return PubChem("pubchem", ServiceContext.create_context())

def test_label(pubchem):
    assert pubchem.get_label ("2244") == { "label" : "cytidylate" } 

