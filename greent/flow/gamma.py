class Gamma:
    def __init__(self):
        pass
    
    def quick(self, question):
        url=f'http://robokop.renci.org:80/api/simple/quick/'
        response = requests.post(url,json=question)
        print( f"Return Status: {response.status_code}" )
        if response.status_code == 200:
            return response.json()
        return response

    def make_N_step_question(self, types,curies):
        question = {
            'machine_question': {
                'nodes': [],
                'edges': []
            }
        }
        for i,t in enumerate(types):
            newnode = {'id': i, 'type': t}
            if curies[i] is not None:
                newnode['curie'] = curies[i]
            question['machine_question']['nodes'].append(newnode)
            if i > 0:
                question['machine_question']['edges'].append( {'source_id': i-1, 'target_id': i})
        return question

    def extract_final_nodes(self, returnanswer):
        nodes = [{'node_name': answer['nodes'][2]['name'], 'node_id': answer['nodes'][2]['id']} for answer in returnanswer['answers']]
        return pd.DataFrame(nodes)

    '''
diabetes = 'MONDO:0005148' #type 2 diabetes
asthma = 'MONDO:0004979' #asthma

diabetes_question = make_N_step_question(['disease','phenotypic_feature','genetic_condition'],[diabetes,None,None])
diabetes_answer = quick(diabetes_question)
Return Status: 200

diabetes_frame = extract_final_nodes(diabetes_answer)
diabetes_frame
    '''
