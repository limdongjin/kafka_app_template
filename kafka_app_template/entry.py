#!/usr/bin/env python3
import hydra
import os
import logging
import sys
from typing import Optional, Tuple, Any, Dict, List
from confluent_kafka import Message, Consumer as KafkaConsumer, Producer as KafkaProducer, KafkaException, KafkaError 
import threading
from omegaconf import OmegaConf, DictConfig

from kafka_app_template.kafka_util import init_kafka_loader, print_assignment, on_acked_print, on_commit_completed_print
from kafka_app_template.protobuf.my_message_pb2 import MyMessage
from kafka_app_template.core import on_next

"""CONSUME AND HANDLING LOOP"""

def _process(msg: bytes):
    logging.info(
        '#%sT%s - Received message: %s',
        os.getpid(), threading.get_ident(), msg.value()
    )

    my_message = MyMessage.FromString(msg.value())

    serialized_result, is_success = on_next(
        my_message=my_message
    )

    return serialized_result
    
def consume_loop(kafka_loader):
    consumer: KafkaConsumer = kafka_loader('consumer')
    producer: KafkaProducer = kafka_loader('producer')
    
    CONSUMER_GROUP_ID = kafka_loader('consumer_group_id')
    CONSUMER_TOPIC_NAME = kafka_loader('consumer_topic_name')
    PRODUCER_TOPIC_NAME = kafka_loader('producer_topic_name')

    logging.info('#%s - Starting consumer group=%s, topic=%s', os.getpid(), CONSUMER_GROUP_ID, CONSUMER_TOPIC_NAME)
    consumer.subscribe([CONSUMER_TOPIC_NAME], on_assign=print_assignment)
    while True:
        logging.info('#%s - Waiting for message...', os.getpid())
        try:
            msg: Optional[Message] = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logging.error('#%s - Consumer error: %s', os.getpid(), msg.error())
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    sys.stderr.write("%s %s [%d] reached end at of offset %d\n" %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    logging.error("Kafka Exception")
                    logging.error(msg.error())
                    raise KafkaException(msg.error())
            else:
                serialized_result = _process(msg=msg)
                producer.produce(
                    topic=PRODUCER_TOPIC_NAME,
                    value=serialized_result,
                    callback=on_acked_print
                )
                producer.poll(3)
                consumer.commit(msg)
        except Exception as e:
            logging.exception('#%s - Worker terminated.', os.getpid())
            logging.error(e)
            consumer.close()
            producer.flush()
            break

"""MAIN"""

@hydra.main(version_base=None, config_path='../conf', config_name="config")
def main(cfg: DictConfig):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )

    kafka_cfg = cfg.kafka 
    kafka_cfg = OmegaConf.to_container(kafka_cfg, resolve=True)
    kafka_cfg['consumer']['on_commit'] = on_commit_completed_print
    kafka_loader = init_kafka_loader(kafka_cfg_dict = kafka_cfg)

    consume_loop(kafka_loader=kafka_loader)

if __name__ == "__main__":
    main()
