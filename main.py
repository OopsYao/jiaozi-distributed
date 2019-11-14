from conn.channel import GeneralChannel
import json
import time
from route import node
from route import dispatcher
from tool import caller

def main():
    channel = GeneralChannel()
    with open("client.json") as f:
        config = json.load(f)
        channel.init_config(config)
        node.init(channel)
        caller.init(channel)
        main_loop(channel)


def main_loop(channel):
    while True:
        message_list = channel.recv()
        for m in message_list:
            dispatcher.on_recv(m)
        time.sleep(0.1)


if __name__ == "__main__":
    main()

