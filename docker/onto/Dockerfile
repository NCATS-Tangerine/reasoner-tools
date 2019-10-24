FROM renciorg/green-base:latest

ADD ./onto_gunicorn_smartapi.sh .
ADD ./synonym.py /usr/local/lib/python3.6/site-packages/pronto/synonym.py

RUN chmod +x onto_gunicorn_smartapi.sh

ENV APP_PORT 5359
ENV DATA_DIR /data
ENV GIT_PULL true
ENV NUM_WORKERS 3

CMD ["./onto_gunicorn_smartapi.sh"]
