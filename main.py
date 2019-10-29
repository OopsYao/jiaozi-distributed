from conn.channel import GeneralChannel
import json
import time


def main():
    channel = GeneralChannel()
    with open("client.json") as f:
        config = json.load(f)
        channel.init_config(config)
        main_loop(channel)


def main_loop(channel):
    while True:
        msg = channel.recv()
        for m in msg:
            print(msg)
            print("ID of this node",channel.get_id())
        time.sleep(0.1)


if __name__ == "__main__":
    main()

