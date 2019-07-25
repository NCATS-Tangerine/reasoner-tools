FROM greentranslator/green-base:latest

WORKDIR /code/reasoner-tools

# scaffold: until we sort out connection to base container.
RUN git pull
RUN git checkout Phil_onto_update
RUN pip install -r greent/requirements.txt

RUN useradd -m -s /bin/bash rosetta

ADD ./setenv.sh setenv.sh
ADD ./task_queue.sh task_queue.sh
ADD ./task_queue_wrapper.sh task_queue_wrapper.sh
RUN chmod +x task_queue.sh
RUN chmod +x task_queue_wrapper.sh

CMD ["./task_queue_wrapper.sh"]