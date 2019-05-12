#!/usr/bin/env python
# -*- coding: utf-8 -*-

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import os
import queue # キュー操作用
from threading import Thread #スレッド処理用

import irrp_wrapper

# Ctl + C で強制終了させる。
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

#ローカル環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# グローバル変数
host            = os.environ["ENV_HOST"]
rootCAPath      = os.environ["ENV_ROOTCA"]
certificatePath = os.environ["ENV_CERT"]
privateKeyPath  = os.environ["ENV_PRIVATE_KEY"]
port            = 8883

message_q = queue.Queue()
topic = {
    "aws_to_raspi":   "raspi/main/request",
    "aws_from_raspi": "raspi/main/result",
}

def new_AwsIotClient(clientId):
    _client = None
    # Init AWSIoTMQTTClient
    _client = AWSIoTMQTTClient(clientId)
    _client.configureEndpoint(host, port)
    _client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    _client.configureAutoReconnectBackoffTime(1, 32, 20)
    _client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    _client.configureDrainingFrequency(2)  # Draining: 2 Hz
    _client.configureConnectDisconnectTimeout(10)  # 10 sec
    _client.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    _client.connect()
    return _client


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

    message_q.put((message.payload))


def order_thread():
    _client = new_AwsIotClient("aa")
    _client.subscribe(topic["aws_to_raspi"], 1, customCallback)


def main_thread():
    _main_client = new_AwsIotClient("bb")

    while True:
        #メッセージ受信待ち
        _request_msg = json.loads(message_q.get().decode())
        print(_request_msg)

        #メッセージに応じた処理
        _response_msg = {
            "status": 1, #request_msg判別エラー
            "value": 0,
        }
        _id   = _request_msg["devise_id"]
        _code = _request_msg["request_code"]
        _response_msg["status"] = irrp_wrapper.request(_id, _code)

        #処理結果の送信
        _main_client.publish(topic["aws_from_raspi"], json.dumps(_response_msg), 1)
        print("Published topic %s: %s\n" % (topic["aws_from_raspi"], _response_msg))


if __name__ == "__main__":
    #AWSからのメッセージ受信スレッド開始

    t1 = Thread(target=order_thread)
    t1.start()

    main_thread()
