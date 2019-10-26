from conn import GeneralChannel
import json
import time


def main():
    channel = GeneralChannel.GeneralChannel()
    with open("clie.json") as f:
        config = json.load(f)
        channel.init_config(f)
        main_loop(channel)


def main_loop(channel):
    while True:
        msg = channel.recv()
        for m in msg:
            pass
        time.sleep(0.1)


if __name__ == "__name__":
    main()
