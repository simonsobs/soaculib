FROM python:3.10

RUN pip install dumb-init

WORKDIR /app/soaculib/

COPY . /app/soaculib/
RUN pip install .['simulator']

# For the simulators, which need to come up in a certain order
RUN apt-get update && apt-get install -y netcat
RUN wget https://raw.githubusercontent.com/eficode/wait-for/master/wait-for
RUN chmod +x ./wait-for
