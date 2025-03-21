FROM python:3.10

WORKDIR /app/soaculib/

RUN pip install pip --upgrade

# Take advantage of build cache when working on simulator/
COPY python/ ./python
COPY setup.py .
COPY pyproject.toml .

RUN pip install .['simulator']

COPY simulator/ ./simulator
