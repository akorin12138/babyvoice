# TODO:
# [x]1.隔一段时间自动录音5s，推到http上(x)，将录音放在本地
# [x]2.获取录音并推理（直接使用main.py），并将结果推送到mqtt上
# [x]3.打包成docker上传到火山引擎，使用应用负载功能
# 4.实现类似于小度机器人的可问答，调用大模型网关的api
import time
import argparse
from babyInferMqtt import babyInferMqtt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker",help="broker server ip",default='192.168.35.179',type=str,required=False)
    args = parser.parse_args()
    print(f'broker ip:{args.broker}')
    
    baby = babyInferMqtt(port=31002,broker=args.broker)
    # baby = babyInferMqtt(port=31002,broker='192.168.76.179',
    #                      url='https://61.139.65.143:53294/music/temp.wav')
    while True:
        baby.record()
        client = baby.babyConnectMqtt()
        # 循环下面的函数即可
        label,score = baby.babyInfer()
        baby.babyMqttPublish(client=client,branch='status',msg=label)
        baby.babyMqttPublish(client=client,branch='score',msg=score)
        # 打印转圈
        for i in range(0, int(10/0.25)):
            list = ["\\", "|", "/", "—"]
            index = i % 4
            print("\r waiting... {}".format(list[index]), end="")
            time.sleep(0.25)