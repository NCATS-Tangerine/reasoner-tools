from __future__ import absolute_import, unicode_literals
from __future__ import absolute_import
from celery import Celery
import greent.flow.dag.conf as Conf

'''
app = Celery('greent.flow.dag',
             broker='amqp://guest:guest@localhost/rosetta',
             backend='rpc://',
             include=[ 'greent.flow.dag.tasks' ])
'''
app = Celery(Conf.celery_app_package,
             broker=Conf.celery_broker_url,
             backend=Conf.celery_result_backend,
             include=[ f'{Conf.celery_app_package}.tasks' ])

