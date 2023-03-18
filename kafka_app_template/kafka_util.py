import uuid
from confluent_kafka import Consumer as KafkaConsumer, Producer as KafkaProducer
from .common import get_stream_logger, flatten_dict

def on_acked_print(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


def on_commit_completed_print(err, partitions):
    if err:
        print(str(err))
    else:
        print("Committed partition offsets: " + str(partitions))


def print_assignment(topic_consumer, partitions):
    print('Assignment:', partitions)

def init_kafka_loader(kafka_cfg_dict):
    assert type(kafka_cfg_dict) is dict 
    consumer_cfg = flatten_dict(kafka_cfg_dict['consumer']) if 'consumer' in kafka_cfg_dict else None
    producer_cfg = flatten_dict(kafka_cfg_dict['producer']) if 'producer' in kafka_cfg_dict else None

    def loader(target):
        if target == 'consumer':
            assert consumer_cfg is not None
            return KafkaConsumer(consumer_cfg, logger=get_stream_logger(f'kafka-consumer-{str(uuid.uuid4())}'))
        elif target == 'producer':
            assert producer_cfg is not None
            return KafkaProducer(producer_cfg, logger=get_stream_logger(f'kafka-producer-{str(uuid.uuid4())}'))
        else:
            return kafka_cfg_dict[target]
    return loader


