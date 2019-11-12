from conn.channel import GeneralChannel
import json
import time
from route import dispatcher


def main():
    channel = GeneralChannel()
    with open("client.json") as f:
        config = json.load(f)
        channel.init_config(config)
        main_loop(channel)


def main_loop(channel):
    while True:
        message_list = channel.recv()
        for m in message_list:
            dispatcher.on_recv(m)


if __name__ == "__main__":
    main()

