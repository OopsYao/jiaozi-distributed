# 架构
### Dispatcher
`Dispatcher`以session为组分发本节点消息栈中的每一封消息给相应的`MessageDealer`。即认为消息是有状态的，且可以分为如下的几种session，而每一个session都有一个`MessageDealer`来进行处理：

- prepare - send

    系统发送的prepare message和随后的send message
- channel build request - build result

    收到的其他节点发来的channel build request以及其后的channel建立成功与否的结果
- channel destroy message

    收到的关于其他邻接节点发起的channel destroy的通知
- general send message

    从邻接节点收到的需要转发的消息



### MessageDealer
因此相应地，类`MessageDealer`应至少具有如下API（或者考虑分为不同的Dealer，如`PrepareDealer`等等）：

- prepare -> send 
    - `on_prepare(target_node, delay)`
    - `on_send(message)`

- channel build request -> build result
    - `on_channel_build_request(request_node, channel_type)`
        需要返回同意与否
    - `on_channel_build_success(channel_id)`
    - `on_channel_build_failure(error_code)`

- channel destroy
    - `on_channel_destroy(channel_id)`

- general message
    - `on_message(message)`


### Caller
可以调用`Caller`进行主动的通信操作：

- `build_channel(target_node, callback)`

    建立channel，并传入callback以处理后续结果

- `destroy_channel(channel_id, callback)`

    销毁通道并传入callback以处理后续结果

- `send()`

    general send