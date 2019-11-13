"""node内部的所有信息"""

N = 10  # 总节点数目
C = 0  # 最大持有通道数量
NODE_ID = 0  # 本节点的node id
TIME_OUT = 3.1  # 允许延时
TIME_BUILD_H = 1.1  # 高速通道的建立时间
TIME_BUILD_N = 1.1  # 普通通道建立时间
LAG_H = 0.1  # 高速通道时延
LAG_N = 0.5  # 普通通道时延

CHANNEL_TYPE_NORMAL = 0  # 低速通道标识
CHANNEL_TYPE_FAST = 1    # 高速通道标识
K = 2 # K( m_h' * delay_h + m_l' * delay_l ) < timeout

'''
route_table: 存储当前节点的路由表

[{'next_node': ,
  'm_h': ,
  'm_l': ,
  'end': ,
 }]

'''
route_table = []

'''
存放当前节点的邻接节点

[{'target':  ,     #相邻节点ID
 'channelType': ,   # 连接通道类型
 'channelId':       # 通道ID
 }]

'''
adjacent_nodes = []