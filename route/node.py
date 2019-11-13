from conn import const
import json

"""node内部的所有信息"""

N = 10  # 总节点数目
C = 0  # 最大持有通道数量
NODE_ID = 0  # 本节点的node id
TIME_OUT = 3.1  # 允许延时
TIME_BUILD_H = 1.1  # 高速通道的建立时间
TIME_BUILD_N = 1.1  # 普通通道建立时间
LAG_H = 0.1  # 高速通道时延
LAG_N = 0.5  # 普通通道时延
M_H = 100  # 高速通道限制数目
M_N = 100  # 低速通道限制数目

CHANNEL_TYPE_NORMAL = 0  # 低速通道标识
CHANNEL_TYPE_FAST = 1  # 高速通道标识
K = 2  # K( m_h' * delay_h + m_l' * delay_l ) < timeout


def init(channel):
    """ 初始化参数 """
    N = channel.get_config(const.main_config, const.node_count)
    NODE_ID = channel.get_config(const.index)

    # 云端测试环境
    C = channel.get_config(const.main_config, const.max_channel_conn)
    # 本地测试环境
    with open("server/cmake-build-debug/server.json") as f:
        config = json.load(f)
        C = config["mainConfig"]["maxChannelCount"][NODE_ID - 1]

    TIME_OUT = channel.get_config(const.main_config, const.timeout)
    TIME_BUILD_H = channel.get_config(
        const.channel_config, const.high_speed, "buildTime"
    )
    TIME_BUILD_H = channel.get_config(
        const.channel_config, const.normal_speed, "buildTime"
    )
    LAG_H = channel.get_config(const.channel_config, const.high_speed, const.lag)
    LAG_N = channel.get_config(const.channel_config, const.normal_speed, const.lag)
    M_H = channel.get_config(const.channel_config, const.high_speed, "maxCount")
    M_N = channel.get_config(const.channel_config, const.normal_speed, "maxCount")


"""
route_table: 存储当前节点的路由表

[{'next_node': ,
  'm_h': ,
  'm_l': ,
  'end': ,
 }]

"""
route_table = []

"""
存放当前节点的邻接节点

[{'target':  ,     #相邻节点ID
 'channelType': ,   # 连接通道类型
 'channelId':       # 通道ID
 }]

"""
adjacent_nodes = []


def get_channel(adj_node):
    for n in adjacent_nodes:
        if n["target"] == adj_node:
            return (n["channelType"], n["channelId"])

