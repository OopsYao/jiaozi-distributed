# Construction
## Session-oriented
### Dispatcher
`MessageDealer` get registered here. A dispatcher dispatches
every message the node received to the corrrespond `MessageDealer`
instance. i.e., dispatching them by event flow or session.

There are types of sessions:
- prepare - send

    The event flow of a prepare message and its corresponding send message
- channel build request - build result

    The request of building a channel and the final result
- channel destroy message

    Message of channel destroy which is not initiated by this node
- general send message

    Message received from connected nodes

### Caller
The api to make initiative actions.

Types of actions:
- `build_channel(..., callback)`

- `destroy_channel(..., callback)`

- `send()`

    general send