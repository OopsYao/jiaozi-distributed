from conn import const
import copy


def _get_prototype():
    return {
        const.call_type: "",
        const.channel_id: 0,
        const.sys_message: {const.target: 0, const.data: "", const.delay: 0},
        "extMessage": {},
        const.state: const.STATE_REQUEST,
        const.err_code: const.ERR_CODE_NONE,
    }


def get_channel_build_msg(target_node, channel_type):
    msg = _get_prototype()
    msg[const.call_type] = const.CALL_TYPE_CHANNEL_BUILD
