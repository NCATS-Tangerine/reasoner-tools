# usage: $uvicorn uberonto_OAS3:uberonto_oas3 --reload
import json
import uvicorn
from fastapi import FastAPI
from SPARQLWrapper import SPARQLWrapper, JSON

uberonto_oas3 = FastAPI(
    title="UberOnto API, an Uberongraph Interface",
    description="UberOnto API is a simple interface to the SPARQL-queried Uberongraph available at https://stars-app.renci.org/uberongraph/#query",
    version="1.0",
    contact="colinkcurtis@gmail.com",
    openapi_url="/uberonto_oas3/openapi.json",
    docs_url="/uberonto_oas3/docs",
    redoc_url="/uberonto_oas3/redocs"
    )

@uberonto_oas3.get("/id_list/{ontology_name}")
def id_list(ontology_name: str):
    formatted_input = ontology_name
    uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
    sparql = SPARQLWrapper(uberongraph_request_url)
    query_text = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?subject
        FROM     <http://reasoner.renci.org/ontology>
        WHERE {    
        ?subject rdfs:isDefinedBy <http://purl.obolibrary.org/obo/PLACEHOLDER.owl>
        }
        """
    formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input.lower())
    sparql.setQuery(formatted_query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    #print(json.dumps(results['results'], sort_keys=True, indent = 4))
    output = []
    for item in results['results']['bindings']:
        an_id = item['subject']['value'].replace('http://purl.obolibrary.org/obo/','')
        reformatted_id = an_id.replace('_',':')
        output.append(reformatted_id)
    return output

@uberonto_oas3.get('/descendants/{curie}')
def descendants(curie: str):
    formatted_input = curie.replace(':','_')
    uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
    sparql = SPARQLWrapper(uberongraph_request_url)
    query_text = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?term
        FROM     <http://reasoner.renci.org/ontology/closure>
        WHERE {    
            ?term rdfs:subClassOf <http://purl.obolibrary.org/obo/PLACEHOLDER>
        }
        """
    formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input)
    sparql.setQuery(formatted_query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    output = []
    for term in results['results']['bindings']:
        sub_term = term['term']['value']
        output.append(sub_term)
    formatted_output = []
    for term in output:
        formatted_output.append(term.replace('http://purl.obolibrary.org/obo/','') \
        .replace('_',':').replace('http://linkedlifedata.com/resource/umls/id/','') \
        .replace('http://www.ebi.ac.uk/efo/',''))
    return formatted_output

@uberonto_oas3.get('/children/{curie}')
def children(curie: str):
    formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input)
    sparql.setQuery(formatted_query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    output = []
    for term in results['results']['bindings']:
        sub_term = term['term']['value']
        output.append(sub_term)
    formatted_output = []
    for term in output:
        formatted_output.append(term.replace('http://purl.obolibrary.org/obo/','') \
        .replace('_',':').replace('http://linkedlifedata.com/resource/umls/id/','') \
        .replace('http://www.ebi.ac.uk/efo/',''))
    return formatted_output

@uberonto_oas3.get('/label/{curie}')
def label(curie: str):
    formatted_input = curie.replace(':','_')
    uberongraph_request_url = 'https://stars-app.renci.org/uberongraph/sparql'
    sparql = SPARQLWrapper(uberongraph_request_url)
    query_text = """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT *
        FROM     <http://reasoner.renci.org/ontology>
        WHERE {    
            <http://purl.obolibrary.org/obo/PLACEHOLDER> rdfs:label ?label
        }
        """
    formatted_query_text = query_text.replace('PLACEHOLDER', formatted_input)
    sparql.setQuery(formatted_query_text)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    output = {}
    if results['results']['bindings']:
        label = results['results']['bindings'][0]['label']['value']
        output['id'] = curie
        output['label'] = label
    return output

if __name__ == "__main__":
    uvicorn.run(uberonto_oas3, host="0.0.0.0", port=8000)


### below are templates for each of the many RESTful interactive types

# @roivant_API.get("/get_test/{id}")
# def get_item(id: int, q: str = None):
#     return {"id": id, "q": q}

# @roivant_API.put("/put_test/{id}")
# def put_item(id: int, item: Item):
#     return {"name": item.name, "id": id}

# @roivant_API.post("/post_test/{id}")
# def post_item(id: int, item: Item):
#     return {'hey fren'}

# @roivant_API.delete("/delete_test/{id}")
# def delete_item(id: int, item: Item):
#     return {'hey fren'}

# @roivant_API.options("/options_test/{id}")
# def options_item(id: int, item: Item):
#     return {'hey fren'}

# @roivant_API.head("/head_test/{id}")
# def head_item(id: int, item: Item):
#     return {'hey fren'}

# @roivant_API.patch("/patch_test/{id}")
# def patch_item(id: int, item: Item):
#     return {'hey fren'}

# @roivant_API.trace("/trace_test/{id}")
# def trace_item(id: int, item: Item):
#     return {'hey fren'}