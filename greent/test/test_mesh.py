import pytest
import requests
import os
from greent.services.mesh import MeshKS
from greent.servicecontext import ServiceContext

@pytest.fixture(scope='module')

def mesh():
    url = "http://id.nlm.nih.gov/mesh/sparql"
    return MeshKS(ServiceContext.create_context(), url)

def test_label(mesh):
    assert mesh.get_label_by_id('mesh:D001241') == [{ "label" : "Aspirin" }]

