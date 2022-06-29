FROM python:3.10

RUN pip install dumb-init

# For the simulators, which need to come up in a certain order
RUN apt-get update && apt-get install -y netcat
RUN wget https://raw.githubusercontent.com/eficode/wait-for/master/wait-for
RUN chmod +x ./wait-for

WORKDIR /app/soaculib/

# Take advantage of build cache when working on simulator/
COPY versioneer.py /app/soaculib/
COPY setup.cfg /app/soaculib/
COPY python/ /app/soaculib/python/
COPY scripts/ /app/soaculib/scripts/
COPY setup.py /app/soaculib/

RUN pip install .['simulator']

COPY simulator/ /app/soaculib/simulator/
