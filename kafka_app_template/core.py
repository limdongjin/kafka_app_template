import logging
from typing import Tuple 
from google.protobuf.timestamp_pb2 import Timestamp

from .protobuf.my_message_pb2 import MyMessage
from .protobuf.my_result_message_pb2 import MyResultMessage

def on_next(
    my_message: MyMessage,
) -> Tuple[bytes, bool]:
    """MyMessage -> (<Serialized Value>, <Boolean>)
    """
    logging.debug("on_next(...)")
    
    req_id: str = my_message.reqId
    user_id: str = my_message.userId
    request_message: str = my_message.requestMessage
    
    logging.info(f"process req_id = {req_id}, user_id = {user_id}, request_message = {request_message}")

    timestamp = Timestamp()
    timestamp.GetCurrentTime()
    my_result_message = MyResultMessage(
        reqId = req_id,
        userId = user_id,
        resultMessage = "process ok",
        createdAt = timestamp.ToMicroseconds()
    )
    logging.debug(my_result_message)

    serialized_value = my_result_message.SerializeToString()
    logging.debug(serialized_value)

    return serialized_value, True

