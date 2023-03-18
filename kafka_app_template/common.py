import logging
from collections.abc import MutableMapping

def get_stream_logger(logger_name: str, logging_level: int = logging.DEBUG):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    return logger

# https://stackoverflow.com/a/6027615
def flatten_dict(d: MutableMapping, parent_key: str = '', sep: str ='.') -> MutableMapping:
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)    
