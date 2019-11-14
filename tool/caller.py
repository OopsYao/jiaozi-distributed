from conn.channel import GeneralChannel
from conn import const
from tool import message as msger
from route import dispatcher
import sys
from route import node


current_module = sys.modules[__name__]
_channel_api = None


def init(channel):
    current_module._channel_api = channel


def build_channel(target_node, channel_type, success_callback, failure_callback):
    """建立与target_node之间的通道"""
    _channel_api.send(msger.get_channel_build_msg(target_node, channel_type), 0)
    # 向dispatcher注册监听器，监听通道建立结果
    dispatcher.await_build_result(
        target_node, channel_type, success_callback, failure_callback
    )
    node.requiring_channels.append((target_node, channel_type))


def reply(request_msg, agreed):
    """回复是否建立通道（需要传入当时请求的消息）"""
    _channel_api.send(msger.get_build_reply_msg(request_msg, agreed), 0)


def destroy_channel(channel_id, callback):
    """摧毁通道"""
    _channel_api.send(msger.get_destroy_msg(channel_id), 0)
    # 向dispatcher注册监听器，监听通道destroy完毕的消息
    dispatcher.await_destroy(callback)


def send_message(message, next_node, channel_id, ext_message=None):
    """通过某一条channel传输（转发）信息，并附加ext_msg"""
    if ext_message != None:
        msger.put_ext_to(message, ext_message)
    message[const.channel_id] = channel_id

    _channel_api.send(message, next_node)


def send_sys_message(extMsg, next_node, channel_id):
    """通过某一条channel传输自定义信息"""
    _channel_api.send(msger.get_sys_msg(extMsg, next_node, channel_id), next_node)

