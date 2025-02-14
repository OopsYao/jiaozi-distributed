from conn import const
from route.handler import SendHandler
from route.handler import BuildRequestHandler
from route.handler import SysHandler
from tool import caller
import time
from route import node


# 三种监听器等候区
waiting_for_send = {}
waiting_for_build = {}
waiting_for_destroy = {}


def on_recv(message):
    call_type = message[const.call_type]
    # 消息初步分类
    if call_type == const.CALL_TYPE_PREPARE:
        _on_prepare(message)
    elif call_type == const.CALL_TYPE_SEND:
        _on_send(message)
    elif call_type == const.CALL_TYPE_CHANNEL_BUILD:
        _on_build(message)
    elif call_type == const.CALL_TYPE_CHANNEL_DESTROY:
        _on_destroy(message)
    elif call_type == const.CALL_TYPE_SYS:
        _on_sys(message)


def _on_prepare(message):
    sys_message = message[const.sys_message]
    target_node = sys_message[const.target]
    delay = sys_message[const.delay]

    handler = SendHandler()
    handler.on_prepare(target_node, delay, message)
    await_send_message(target_node, time.time() + delay, handler)


def _on_send(message):
    EPS = 0.3  # 误差范围(s)
    target_node = message[const.sys_message][const.target]
    for (target, eta), handler_list in waiting_for_send.items():
        # 若该send消息的到达时间与预计到达时间在误差范围内
        if target == target_node and abs(time.time() - eta) < EPS:
            for handler in handler_list:
                handler.on_send(target_node, message)
            del waiting_for_send[(target, eta)]
            break
    else:
        # 没有找到匹配的prepare session
        SendHandler().on_send(message[const.sys_message][const.target], message)


def _on_build(message):
    state = message[const.state]
    channel_id = message[const.channel_id]
    target_node = message[const.sys_message][const.target]
    channel_type = message[const.channel_type]

    if channel_id == 0 and state == const.STATE_NOTICE:
        # 收到的是来自别的节点创建通道的请求
        handler = BuildRequestHandler()
        agreed = handler.on_channel_build_request(
            target_node, message[const.channel_type]
        )
        caller.reply(message, agreed)
        if agreed:
            await_build_result(
                target_node,
                channel_type,
                handler.on_channel_build_success,
                handler.on_channel_build_failure,
            )
        else:
            pass
    else:
        # 收到的是通道结果
        key = (target_node, channel_type)
        if key in waiting_for_build.keys():
            for succ_call, fail_call in waiting_for_build[key]:
                if channel_id != 0:
                    succ_call(target_node, channel_id, channel_type)
                    try:
                        node.requiring_channels.remove(key)
                    except ValueError:
                        print("ALREADY REMOVED")
                else:
                    fail_call(message[const.err_code])
            del waiting_for_build[key]

        # 针对模糊通道要求等待者
        key_vague = (target_node, None)
        if key_vague in waiting_for_build.keys():
            if channel_id != 0:
                for s, _ in waiting_for_build[key_vague]:
                    s(target_node, channel_id, channel_type)
                del waiting_for_build[key_vague]
            elif (
                target_node,
                const.CHANNEL_TYPE_FAST
                if channel_type == const.CHANNEL_TYPE_NORMAL
                else const.CHANNEL_TYPE_NORMAL,
            ) not in node.requiring_channels:
                # 该类型通道建立不成功
                # 而正在建立的通道中又没有另一类型的
                # 即该等待者没有等待意义
                for _, f in waiting_for_build[key_vague]:
                    f(message[const.err_code])
                del waiting_for_build[key_vague]
            # 否则继续等待另一类型通道建立结果消息


def _on_destroy(message):
    """收到（其他节点发起的）通道销毁的消息"""
    pass


def _on_sys(message):
    """收到自定义消息"""
    SysHandler().on_sys(message)


def await_send_message(target_node, eta, handler):
    """向waiting_for_sent中加入等待者handler
    其等待的send message由target_node, eta(预计到达时间)所判定"""
    _add_to(waiting_for_send, (target_node, eta), handler)
    pass


def await_build_result(target_node, channel_type, on_success, on_failure):
    """向waiting_for_build中加入等待者(on_success, on_failure)
    其等待的build result由target_node与channel_type决定"""
    _add_to(waiting_for_build, (target_node, channel_type), (on_success, on_failure))


def await_destroy(channel_id, callback):
    """向waiting_for_build中加入等待者callback
    其等待的destroy完毕消息由channel_id决定"""
    _add_to(waiting_for_destroy, channel_id, callback)


def _add_to(dict, key, value):
    """给定一个字典，其value部分为list类型，通过键向对应的list添加元素（不存在则创建）"""
    ls = dict.get(key, [])
    if len(ls) == 0:
        dict[key] = ls
    ls.append(value)
