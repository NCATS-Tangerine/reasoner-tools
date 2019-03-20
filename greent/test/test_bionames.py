import pytest
import requests
import os
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

def THING():
  pass

# test 1: 
def test_ID_to_label(THING)