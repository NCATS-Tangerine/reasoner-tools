FROM greentranslator/green-base:latest

WORKDIR /code/reasoner-tools

# scaffold: until we sort out connection to base container.
RUN git pull
RUN git checkout Phil_onto_update
RUN pip install -r greent/requirements.txt

RUN useradd -m -s /bin/bash rosetta

ADD ./setenv.sh setenv.sh
ADD ./conf.sh conf.sh
ADD ./start_api_wrapper.sh start_api_wrapper.sh

CMD ["./start_api_wrapper.sh"]