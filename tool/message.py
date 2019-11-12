from conn import const
import copy

_extMessage = "extMessage"


def _get_prototype():
    """消息原型"""
    return {
        const.call_type: "",
        const.channel_id: 0,
        const.sys_message: {const.target: 0, const.data: "", const.delay: 0},
        _extMessage: {},
        const.state: const.STATE_REQUEST,
        const.err_code: const.ERR_CODE_NONE,
    }


def get_channel_build_msg(target_node, channel_type):
    """生成通道建立请求消息"""
    msg = _get_prototype()
    msg[const.call_type] = const.CALL_TYPE_CHANNEL_BUILD
    msg[const.sys_message][const.target] = target_node
    msg[const.channel_type] = channel_type
    return msg


def get_build_reply_msg(request_msg, agreed):
    """根据请求建立通道消息产生回复消息"""
    msg = copy.deepcopy(request_msg)
    msg[const.state] = const.STATE_ACCEPT if agreed else const.STATE_REFUSE
    return msg


def get_sys_msg(ext_msg, target_node, channel_id):
    """生成sys message"""
    msg = _get_prototype()
    msg[const.call_type] = const.CALL_TYPE_SYS
    msg[const.sys_message][const.target] = target_node
    msg[const.channel_id] = channel_id
    return msg


def get_destroy_msg(channel_id):
    """生成destroy message"""
    msg = _get_prototype()
    msg[const.channel_type] = const.CALL_TYPE_CHANNEL_DESTROY
    msg[const.channel_id] = channel_id
    return msg


def put_ext_to(origin_msg, ext_msg):
    """为origin_msg附加信息"""
    origin_msg[_extMessage] = ext_msg
