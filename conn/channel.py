import json
import time
from conn import channel
from conn import client
from conn import const


class GeneralChannel:
    def __init__(self):
        self.client = None
        self.config = None

    def _init_main_config(self):
        print(self.config)
        print(
            self.config[const.main_config][const.master_ip],
            self.config[const.main_config][const.master_port],
        )
        self.client = client.SocketClient(
            self.config[const.main_config][const.master_ip],
            self.config[const.main_config][const.master_port],
        )
        while True:
            line = self.client.read_line()
            if len(line):
                print("id recved : %s" % line)
                ex_config = json.loads(line)
                self.config[const.index] = ex_config[const.index]
                self.config[const.max_channel_conn] = ex_config[const.max_channel_conn]
                break
            else:
                time.sleep(0.05)

    def init_config(self, config):
        """初始化通道"""
        self.config = config
        print("conn.channel:L37", config)
        print("conn.channel:L38", self.config)
        self._init_main_config()

    def send(self, message, target_id):
        """将消息发送给指定目标"""
        message[const.target_id] = target_id
        print("msg send : %s" % message)
        self.client.println(json.dumps(message))

    def recv(self):
        """获取缓存中的所有信息"""
        result = []
        while True:
            line = self.client.read_line()
            if len(line):
                print("msg recv: %s" % line)
                message = json.loads(line)
                message[const.recv_time] = time.time()
                result.append(message)
            else:
                break
        return result

    def get_id(self):
        """获取当前节点编号"""
        return self.config[const.index]

    def get_config(self, args):
        obj = self.config
        for arg in args:
            obj = obj[arg]
        return obj
