from conn.channel import GeneralChannel
from conn import const
from tool import message


def build_channel(target_node, channel_type, success_callback, failure_callback):
    """建立与target_node之间的通道"""
    pass


def destroy_channel(channel_id, callback):
    """摧毁通道"""
    pass


def send_message(message, channel_id):
    """通过某一条channel传输信息"""
    pass
