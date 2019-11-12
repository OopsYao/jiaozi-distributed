# 架构
### Dispatcher
`Dispatcher`以session为组分发本节点消息栈中的每一封消息给相应的`MessageDealer`。即认为消息是有状态的，且可以分为如下的几种session，而每一个session都有一个`MessageDealer`来进行处理：

- prepare - send
    处理消息栈中的prepare message和send message
    prepare 对应创建md
    send需要先匹配之间的md ，没有匹配成功则创建
    系统发送的prepare message和随后的send message
    note! 能够将不同send消息映射到对应的messageDealer
    
- channel build request - build result

    收到的其他节点发来的channel build request以及其后的channel建立成功与否的结果
- channel destroy message

    收到的关于其他邻接节点发起的channel destroy的通知
    
    
- sys message
    路由表信息交换
    
    
    



### MessageDealer
因此相应地，类`MessageDealer`应至少具有如下API（或者考虑分为不同的Dealer，如`PrepareDealer`等等）：

- prepare -> send  
    [] : 保存路线
    - `on_prepare(target_node, delay)`
        查看路由表是否可达
        y: 保存对应send消息路线
        n: 创建 -> 调用Caller
                -> build_channel(（print 10，print 9）)
                （-------）
    - `on_send(message)`

// callType =  channel_build 
// state = -1 (NOTICE)
- channel build request -> build result  
    - `on_channel_build_request(request_node, channel_type)`
        需要返回同意与否
    - `on_channel_build_success(channel_id)`
    - `on_channel_build_failure(error_code)`
    

- channel destroy
    - `on_channel_destroy(channel_id)`

- sys message
    - `on_message(message)`


### Caller
可以调用`Caller`进行主动的通信操作：

- `build_channel(target_node, callback)`

    建立channel，并传入callback以处理后续结果

- `destroy_channel(channel_id, callback)`

    销毁通道并传入callback以处理后续结果

- `send()`

    general send
