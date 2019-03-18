# usage: $uvicorn uberonto_OAS3:uberonto_oas3 --reload
import json
from fastapi import FastAPI
from SPARQLWrapper import SPARQLWrapper, JSON

uberonto_oas3 = FastAPI(
    title="UberOnto API, OpenAPI 3.0",
    description="A RESTful interface for UberonGraph",
    version="0.1",
    openapi_url="/uberonto_oas3/v1/openapi.json",
    docs_url="/uberonto_oas3/v1/docs",
    redoc_url="/uberonto_oas3/v1/redocs"
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

#@uberonto_oas3.get('/descendants/{curie}')





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