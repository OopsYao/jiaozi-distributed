from . import node
from tool import caller
from conn import channel
from conn import const
import random
from route import dispatcher


class SendHandler:
    """ 处理prepare -> send消息链，或者单独的send消息 """

    # 为有pepare的send消息规划的节点 默认为None
    node_intend = None
    channel_id = 0

    def _rand_channel(self):
        """ 按策略随机选择通道类型 """
        p = node.M_H / (node.M_H + node.M_N)
        if random.random() < p:
            return const.CHANNEL_TYPE_FAST
        else:
            return const.CHANNEL_TYPE_NORMAL

    def on_prepare(self, target_node, delay, prepare_message):
        def _on_build_success(target_node, channel_id, channel_type):
            # 设置好预设节点(如果send message晚于通道建成)
            self.node_intend = target_node
            # 发送那个消息(如果send message早于通道建成)
            if hasattr(self, "send_message"):
                caller.send_message(self.send_message, target_node, channel_id)
            # 修改邻接表
            node.adjacent_nodes.append(
                {
                    "target": target_node,
                    "channelType": channel_type,
                    "channelId": channel_id,
                }
            )
            # 修改路由表
            node.route_table.append(
                {"next_node": target_node, "m_h": 0, "m_l": 0, "end": target_node}
            )
            # 向周围节点发送通知（除了建立通道的那个节点）
            for adj_node in node.adjacent_nodes:
                if adj_node["target"] != target_node:
                    ano_channel_type, ano_channel_id = (
                        adj_node["channelType"],
                        adj_node["channelId"],
                    )
                    # 接受通知的那个节点到自己再到建立通道的那个节点之间高速通道数目(0, 1, 2)
                    m_h = (1 if channel_type == const.CHANNEL_TYPE_FAST else 0) + (
                        1 if ano_channel_type == const.CHANNEL_TYPE_FAST else 0
                    )
                    caller.send_sys_message(
                        {
                            "route_msg": {
                                "next_node": node.NODE_ID,
                                "m_h": m_h,
                                "m_l": 2 - m_h,
                                # 跟自己建立通道的那个节点
                                "end": target_node,
                            }
                        },
                        adj_node["target"],
                        adj_node["channelId"],
                    )

        def _on_build_failure(error_code=None):
            pre_msg = prepare_message
            # 从邻接节点里随机选一个转发prepare消息（高速通道优先）
            candidates = [
                adj
                for adj in node.adjacent_nodes
                if adj["channelType"] == const.CHANNEL_TYPE_FAST
            ]
            if len(candidates) == 0:
                # 全是普通通道
                bingo = random.choice(node.adjacent_nodes)
            else:
                bingo = random.choice(candidates)

            # 存储该节点，下次直接将相应的send转发给他
            self.node_intend = bingo["target"]
            caller.send_message(pre_msg, bingo["target"], bingo["channelId"])

        for record in node.route_table:
            if record["end"] == target_node:
                self.node_intend = target_node
                break
        else:
            # 没有找到
            # 满足C限制，未达节点最大连接数上限
            print("当前邻接节点数", len(node.adjacent_nodes))
            print("最大持有通道数", node.C)
            if len(node.adjacent_nodes) < node.C:
                # 尝试建立通道
                print("尝试建立通道...")
                print("准备发出建立通道请求前检查队列", node.requiring_channels)
                # 如果前面已有一个在申请
                if (
                    (target_node, const.CHANNEL_TYPE_FAST) in node.requiring_channels
                    or (target_node, const.CHANNEL_TYPE_NORMAL)
                    in node.requiring_channels
                ):
                    # 注册自己
                    dispatcher.await_build_result(
                        target_node, None, _on_build_success, _on_build_failure
                    )
                    return

                caller.build_channel(
                    target_node,
                    self._rand_channel(),
                    _on_build_success,
                    _on_build_failure,
                )
            else:
                _on_build_failure()

    def on_send(self, target_node, send_message):
        if node.NODE_ID == target_node:
            print("Success recved")
            return

        if self.node_intend != None:
            _, channel_id = node.get_channel(self.node_intend)
            caller.send_message(send_message, self.node_intend, channel_id)
        else:
            for record in node.route_table:
                if record["end"] == target_node:
                    # 说明是没有prepare的send
                    next_node = record["next_node"]
                    _, channel_id = node.get_channel(next_node)
                    caller.send_message(send_message, next_node, channel_id)
                    break
            else:
                # 此时申请的通道尚未建立好
                # 将消息缓存起来
                self.send_message = send_message


class BuildRequestHandler:
    """ 处理其他节点请求建立通道的请求，以及后续建立结果的处理 """

    def on_channel_build_request(self, request_node, channel_type):
        # 直接同意
        self.channel_type = channel_type
        self.request_node = request_node
        # 存储已有通道正在建立的信息
        node.requiring_channels.append((request_node, channel_type))
        return True

    def on_channel_build_success(self, target_node, channel_id, channel_type):
        # 修改邻接表
        node.adjacent_nodes.append(
            {
                "target": self.request_node,
                "channelType": self.channel_type,
                "channelId": channel_id,
            }
        )
        # 修改路由表，插入记录
        m_h = 1 if self.channel_type == const.CHANNEL_TYPE_FAST else 0
        node.route_table.append(
            {
                "next_node": self.request_node,
                "m_h": m_h,
                "m_l": 1 - m_h,
                "end": self.request_node,
            }
        )

        # 向周围节点广播（除了建立通道的那个节点 ）
        for adj in node.adjacent_nodes:
            if adj["target"] == self.request_node:
                continue
            adj_channel_type, adj_channel_id = adj["channelType"], adj["channelId"]
            caller.send_sys_message(
                {
                    "route_msg": {
                        "next_node": node.NODE_ID,
                        "m_h": m_h
                        + (1 if adj_channel_type == const.CHANNEL_TYPE_FAST else 0),
                        "m_l": 1
                        - m_h
                        + (1 if adj_channel_type == const.CHANNEL_TYPE_NORMAL else 0),
                        "end": self.request_node,
                    }
                },
                adj["target"],
                adj["channelId"],
            )

    def on_channel_build_failure(self, error_code):
        return


class DestroyHandler:
    """ 处理其他节点发起的通道销毁成功后的通知 """

    def on_channel_destroy(self, channel_id):
        pass

    pass


class SysHandler:
    """处理节点之间自定义消息的传播"""

    """
    come_from : 发来msg的节点的target_id
    msg = {
        'callType': 'sys',
           ...,
           'extMessage': {
                'route_msg':{
                    next_node: (与come_from相同) ,
                    m_h:  ,
                    m_l:  ,
                    end:  
                }
           }
    }

    msg' = {
        'callType': 'sys',
           ...,
           'extMessage': {
                'route_msg':{
                    next_node: (当前节点的id) ,
                    m_h: m_h  ,
                    m_l: m_l  ,
                    end:  不修改
                }
           }
    }
        
    """

    """
    1. 修改 msg 为 msg'
    2. 查询路由表，判定是否插入或替换
        1. 判断 msg' 是否是可以不超时传递数据的一条路径 -> K( m_h' * delay_h + m_l' * delay_l ) < timeout
        2. no -> return ???
        3. yes -> 检索路由表中是否有 end==msg[end]
               -> no -> return ???
               -> yes -> 判别msg'与该条记录哪个更优
                      -> msg'更优 -> 替换该条记录 -> 广播msg' -> return 
                      -> msg'较差 -> 扔掉msg' -> return

    """

    def on_sys(self, message):
        # 取出extMessage
        print(message)
        route = message["extMessage"]["route_msg"]

        # 新时延
        delay = self.calculate_delay(route)

        # 判断msg是否是一条有效的路径
        if delay > node.TIME_OUT:
            return
        else:
            # 扫描路由表中无有可到达route['end']的记录
            scan_result = self.scan_route_table(route["end"])

        # 没有，向路由表中插入一条记录
        if scan_result == -1:
            node.route_table.append(route)
        else:
            old_delay = self.calculate_delay(node.route_table[scan_result])

            # 如果该记录对当前节点来说更优，则替代路由表中那条记录
            if delay < old_delay:
                self.modify_route_table(scan_result, route)

        # 修改该条记录中的next_node = 当前节点ID
        route["next_node"] = node.NODE_ID

        # 广播该条消息
        adjacent_nodes = node.adjacent_nodes
        for adjacent in adjacent_nodes:
            if adjacent["channelType"] == 0:
                route["m_l"] += 1
                # 向该邻接节点发送msg'
                caller.send_sys_message(
                    {"route_msg": route}, adjacent["target"], adjacent["channelId"]
                )

                # 修改回msg
                route["m_l"] -= 1
            else:
                route["m_h"] += 1
                # 向邻接节点发送msg'
                caller.send_sys_message(
                    {"route_msg": route}, adjacent["target"], adjacent["channelId"]
                )

                # 修改回msg
                route["m_h"] -= 1

    # 修改node.route_table
    #
    def modify_route_table(self, index, route):
        node.route_table[index] = route

    # 传入一条路由记录，返回计算时延
    def calculate_delay(self, route):
        return node.K * (route["m_h"] * node.LAG_H + route["m_l"] * node.LAG_N)

    # 检索路由表中有无end==msg[end]
    # 有则返回对应路由表中对应记录计算所得的delay返回
    # 无则返-1
    def scan_route_table(self, end):
        table = node.route_table
        row = 0
        # 标识是否找到一条route['end']==end 路由记录
        flag = 0
        for route in table:
            if route["end"] != end:
                flag = 1
                break
            else:
                row += 1
        if flag == 0:
            return -1
        else:
            return row

