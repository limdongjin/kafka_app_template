FROM python:3.9.16-slim-buster as builder

WORKDIR /app

RUN apt update -y && apt-get update -y
RUN pip install --upgrade pip && pip install poetry 
COPY pyproject.toml poetry.toml README.md ./
RUN python -m venv .venv
RUN /app/.venv/bin/python3.9 -m pip install --upgrade pip
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt
RUN apt install -y git gcc g++

RUN .venv/bin/python3.9 -m pip install -r requirements.txt --use-pep517

##############################
FROM python:3.9.16-slim-buster as production

WORKDIR /app

###
RUN apt update && apt-get install -y dumb-init
COPY --from=builder /app/.venv ./.venv

### 
WORKDIR /app
COPY conf ./conf
COPY kafka_app_template ./kafka_app_template

### for debug
# COPY samples ./samples
# ENTRYPOINT ["sleep", "1000000"]

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/app/.venv/bin/python3.9", "-m", "kafka_app_template.entry"]
