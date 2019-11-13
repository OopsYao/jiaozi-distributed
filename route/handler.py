from . import node
from tool import caller
from conn import channel

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
    '''
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
        
    '''

    '''
    1. 修改 msg 为 msg'
    2. 查询路由表，判定是否插入或替换
        1. 判断 msg' 是否是可以不超时传递数据的一条路径 -> K( m_h' * delay_h + m_l' * delay_l ) < timeout
        2. no -> return ???
        3. yes -> 检索路由表中是否有 end==msg[end]
               -> no -> return ???
               -> yes -> 判别msg'与该条记录哪个更优
                      -> msg'更优 -> 替换该条记录 -> 广播msg' -> return 
                      -> msg'较差 -> 扔掉msg' -> return

    '''



    def on_sys(self, message):
        # 取出extMessage
        route = message['extMessage']['route_msg']
        
        # 新时延
        delay = self.calculate_delay(route)
        
        # 判断msg是否是一条有效的路径
        if delay>node.TIME_OUT:
            return
        else:
            # 扫描路由表中无有可到达route['end']的记录
            scan_result = self.scan_route_table(route['end'])
        
        # 没有，向路由表中插入一条记录
        if scan_result==-1:
            node.route_table.append(route)
        else:
            old_delay = self.calculate_delay(node.route_table[scan_result])

            # 如果该记录对当前节点来说更优，则替代路由表中那条记录
            if delay<old_delay:
                self.modify_route_table(scan_result,route)

        # 修改该条记录中的next_node = 当前节点ID

        # 广播该条消息
        adjacent_nodes = node.adjacent_nodes
        for adjacent in adjacent_nodes:
            if adjacent['channelType']==0 :
                route['m_l'] += 1
                # 向该邻接节点发送msg'

                # 修改回msg
                route['m_l'] -= 1
            else:
                route['m_h'] += 1
                # 向邻接节点发送msg'

                # 修改回msg
                route['m_h'] -= 1




                
            

    
    # 修改node.route_table
    # 
    def modify_route_table(self, index, route):
        node.route_table[index] = route
        

    # 传入一条路由记录，返回计算时延
    def calculate_delay(self,route):
        return node.K*( route['m_h']*node.LAG_H + route['m_l']*node.LAG_N)


    # 检索路由表中有无end==msg[end]
    # 有则返回对应路由表中对应记录计算所得的delay返回
    # 无则返-1    
    def scan_route_table(self,end):
        table = node.route_table
        row = 0
        # 标识是否找到一条route['end']==end 路由记录
        flag = 0
        for route in table:
            if route['end']!=end:
                flag = 1
                break
            else:
                row += 1
        if flag==0:
            return -1
        else:
            return row



 
            
        


    

   
