import pytest
import requests
import os
from greent.services.chembl import CHEMBL
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

def chembl():
    return CHEMBL("chembl", ServiceContext.create_context())

def test_label(chembl):
    assert chembl.get_label ("898") == { "label" : "Azapeptide" } 

