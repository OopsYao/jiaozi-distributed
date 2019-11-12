class SendHandler:
    """处理prepare -> send消息链，或者单独的send消息"""

    def on_prepare(self, target_node, delay):
        pass

    def on_send(self, target_node, message):
        pass

    pass


class BuildRequestHandler:
    """处理其他节点请求建立通道的请求，以及后续建立结果的处理"""

    def on_channel_build_request(self, request_node, channel_type):
        pass

    def on_channel_build_success(self, channel_id):
        pass

    def on_channel_build_failure(self, error_code):
        pass

    pass


class DestroyHandler:
    """处理其他节点发起的通道销毁成功后的通知"""

    def on_channel_destroy(self, channel_id):
        pass

    pass


class SysHandler:
    """处理节点之间自定义消息的传播"""

    def on_sys(self, come_from, message):
        pass

    pass
