import pytest
import requests
import os
from greent.services.hgnc import HGNC
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

def hgnc():
    return HGNC("hgnc", ServiceContext.create_context())

def test_label(hgnc):
    assert hgnc.get_label ("HGNC:1097") == { "label" : "BRAF" } 

