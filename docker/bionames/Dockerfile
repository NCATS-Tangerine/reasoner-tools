FROM renciorg/green-base:latest

ADD ./bionames_smartapi.sh .
ADD ./synonym.py /usr/local/lib/python3.6/site-packages/pronto/synonym.py

RUN chmod +x bionames_smartapi.sh

ENV APP_PORT 5001
ENV NUM_WORKERS 2
ENV DATA_DIR /data
ENV GIT_PULL false

CMD ["./bionames_smartapi.sh"]
