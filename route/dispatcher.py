from conn import const
from route.handler import SendHandler
from queue import SimpleQueue
import time

prepare_hangout_queue = {"target"}

EPS = 0.3


def on_recv(message):
    call_type = message[const.channel_type]
    # 消息初步分类
    if call_type == const.CALL_TYPE_PREPARE:
        _on_prepare(message)
    elif call_type == const.CALL_TYPE_SEND:
        _on_send(message)
    elif call_type == const.CALL_TYPE_CHANNEL_BUILD:
        pass
    elif call_type == const.CALL_TYPE_CHANNEL_DESTROY:
        pass
    elif call_type == const.CALL_TYPE_SYS:
        pass

    pass


def _on_prepare(message):
    handler = SendHandler()
    sys_message = message[const.sys_message]
    handler.on_prepare(sys_message[const.target], sys_message[const.delay])
    prepare_hangout_queue.put(handler)


def _on_send(message):
    for target, eta, handler in prepare_hangout_queue:
        if (
            target == message[const.sys_message][const.target]
            and abs(time.time() - eta) < EPS
        ):
            handler.on_send(message)
            prepare_hangout_queue.remove((target, eta, handler))
            break
    else:
        # 没有找到匹配的prepare session
        SendHandler().on_send(message)
