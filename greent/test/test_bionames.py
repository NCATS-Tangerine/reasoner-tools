import pytest
import requests
import os
from greent.services.ontology import GenericOntology
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

# the below requires a local version of the API to be active
def local_test_object():
  pass

#this test
def remote_test_object():
  pass

# test 1: 
def test_ID_to_label_local(THING)