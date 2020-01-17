FROM renciorg/green-base:latest

ADD ./onto_gunicorn_smartapi.sh .
ADD ./synonym.py /usr/local/lib/python3.6/site-packages/pronto/synonym.py

RUN chmod +x onto_gunicorn_smartapi.sh

ENV APP_PORT 6001
ENV NUM_WORKERS 2
ENV DATA_DIR /data
#ENV GIT_PULL false

CMD ["./onto_gunicorn_smartapi.sh"]
