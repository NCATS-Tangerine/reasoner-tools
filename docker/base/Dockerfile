FROM python:3.6.5
ADD . /code
WORKDIR /code

RUN git clone https://github.com/NCATS-Tangerine/reasoner-tools.git

RUN pip install -r reasoner-tools/greent/requirements.txt

RUN apt-get update
RUN apt-get install telnet
RUN apt-get install -y emacs24

CMD ["PYTHONPATH=reasoner-tools", "python", "reasoner-tools/greent/rosetta.py", "--debug", "--test"]
