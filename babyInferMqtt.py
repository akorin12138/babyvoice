import requests
import time
import pyaudio
import wave
import flask
import os

from tqdm import tqdm
from macls.predict import MAClsPredictor
from paho.mqtt import client as mqttClient
from paho.mqtt import __version__

broker = '192.168.76.179'
port = 31002

class babyInferMqtt:
    def __init__(self, port, broker, url=None):
        self.topic = 'baby/'
        self.clientID = f'python-mqtt-orangepi'
        self.broker = broker
        self.port = port
        self.url = url
        
        self.chunk = 512
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recordSecond = 5
        self.deviceIndex = 3
        self.savaAudioName = "./temp/temp.wav"
        self.localAudioPath = './temp/temp.wav'
        
        self.predictor = MAClsPredictor(configs='./cam++.yml',
                            model_path='./model',
                            use_gpu=False)
 
    def printBase(self):
        print(f'topic:{self.topic}')
        print(f'mqtt server: {self.broker}:{self.port}')
        print(f'deviceIndex: {self.deviceIndex}')
 
    def babyConnectMqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
                return
        # Set Connecting Client ID
        client = mqttClient.Client(mqttClient.CallbackAPIVersion.VERSION1,self.clientID)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client
    
    def babyMqttPublish(self,client,branch,msg):
        result = client.publish(self.topic + branch, msg)
        status = result[0]
        if status == 0:
            print(f'send {msg} to {self.topic + branch}')
            return 0
        else :
            print(f'send {msg} error')
            return -1

    def babyInfer(self):
        if self.url !=  None:
            try:
                r = requests.get(self.url,verify=False)
            except:
                print('url close')
                return
            label, score = self.predictor.predict(audio_data=r.content)
        elif os.path.exists(self.localAudioPath):
            label, score = self.predictor.predict(audio_data=self.localAudioPath)
        else:
            raise ValueError("don't get sound")
        print(f'音频的预测结果标签为：{label}，得分：{score}')
        return label,score
    
    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        input_device_index=self.deviceIndex, #一定要指定好输入设备,
                        frames_per_buffer=self.chunk)
        print("recording...")
        frames = []
        for i in range(0, int(self.rate / self.chunk * self.recordSecond)):
            data = stream.read(self.chunk)
            frames.append(data)
        print("done")
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        wf = wave.open(self.savaAudioName, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()


#测试
def main():
    # 获取识别器
    print('------>获取识别器')
    predictor = MAClsPredictor(configs='./cam++.yml',
                            model_path='./model',
                            use_gpu=False)
    
    url = 'https://61.139.65.143:53294/music/temp.wav'
    print('------>正在获取音频')
    try:
        r = requests.get(url,verify=False)
    except:
        print('url close')
        return
    
    print('------>成功获取音频')
    while r.ok:
        label, score = predictor.predict(audio_data=r.content)
        print(f'音频：test_0.wav 的预测结果标签为：{label}，得分：{score}')
        for _ in tqdm(range(5)):
            time.sleep(1)
        try:
            r = requests.get(url,verify=False)
        except:
            print('url close')
            return
    print('end')


if __name__ == "__main__":
    main()
