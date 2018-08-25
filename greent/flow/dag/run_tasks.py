#from greent.flow.dag.tasks import longtime_add
import os
import json
import requests
import time
import yaml

if __name__ == '__main__':

    with open("mq2.yaml", "r") as stream:
        workflow_spec = yaml.load (stream.read ())

        host = "localhost"
        port = os.environ["ROSETTA_WF_PORT"]

        workflow_spec['args'] = {
            "drug_name" : "imatinib",
            "disease_name" : "asthma"
        }
        response = requests.post (
            f"http://localhost:{port}/api/executeWorkflow",
            json=workflow_spec)

        print (f"{json.dumps (response.json (), indent=2)}")

        
    '''
    result = longtime_add.delay(1,2)
    # at this time, our task is not finished, so it will return False
    print ('Task finished? ', result.ready())
    print ('Task result: ', result.result)
    # sleep 10 seconds to ensure the task has been finished
    time.sleep(10)
    # now the task should be finished and ready method will return True
    print ('Task finished? ', result.ready())
    print ('Task result: ', result.result)
    '''
