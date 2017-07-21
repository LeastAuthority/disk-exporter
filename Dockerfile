FROM leastauthority/base

COPY requirements.txt /disk-exporter/requirements.txt

RUN /app/env/bin/pip install --requirement /disk-exporter/requirements.txt

COPY . /disk-exporter

RUN /app/env/bin/pip install --no-index /disk-exporter
