# kafka-app-template

Confluent Kafka Python app template with hydra, protobuf

## How to start?

```bash
git clone https://github.com/limdongjin/kafka_app_template
cd kafka_app_template

poetry install 

# and
# setup your environment variables for kafka authentication.
# ref to /conf/kafka/kafka.conf

.venv/bin/python3.9 kafka_app_template/entry.py
```

## Dockerizing

```bash
docker build -t tempapp .
```
