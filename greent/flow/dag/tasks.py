from __future__ import absolute_import
import time
import greent.flow.dag.conf as Conf
from greent.flow.dag.celery import app

@app.task(bind=True, queue="rosetta")
def longtime_add(self, x, y):
    print ('long time task begins')
    # sleep 5 seconds
    time.sleep(5)
    print ('long time task finished')
    return x + y



