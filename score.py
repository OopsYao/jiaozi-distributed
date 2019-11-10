import json

"""计算单组测试得分（总分为各组测试得分和）"""


server_home = "./server/"
cmake_build_debug_dir = server_home + "cmake-build-debug/"


def get_sigma():
    """从测试服务器配置server.json中读取允许最大延时sigma"""
    server = json.load(open(cmake_build_debug_dir + "server.json"))
    return server["mainConfig"]["timeOut"]


def get_test_msg_num():
    """获取要求传达的msg的数量"""
    test = json.load(open(server_home + "test.json"))
    # 除去一半的prepare消息
    return len(test) / 2


def get_delay_list():
    """实际到达的msg的延迟（包含了可能超时到达的）"""
    arrived_set = set()
    delay_list = []
    with open(cmake_build_debug_dir + "attach.log") as log:
        for line in log.readlines():
            # hash(or data), 收到时间, 延时
            h, _, d = line.split(",")
            # 去重添加，仅算第一个到达的
            if h not in arrived_set:
                delay_list.append(float(d))
            arrived_set.add(h)
    return delay_list


def main():
    test_msg_num = get_test_msg_num()
    sigma = get_sigma()
    delay_list = get_delay_list()

    tao = [delay for delay in delay_list if delay <= sigma]
    tao_avg = sum(tao) / len(tao) if len(tao) != 0 else 0
    D_tao = sum([(i - tao_avg) ** 2 for i in tao]) / len(tao) if len(tao) != 0 else 0

    eta = len(tao) / test_msg_num

    print(f"With sigma = {sigma}")
    print({"eta": f"{eta:.001%}", "Mean of tao": tao_avg, "Variance of tao": D_tao})

    G = ((sigma * 2 - tao_avg) / sigma * 3.5 + 0.5 / (D_tao + 1)) * eta ** 2.5 * 10
    print("Final score: G =", G)


if __name__ == "__main__":
    main()
