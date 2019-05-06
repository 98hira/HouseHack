#!/usr/bin/env python
# -*- coding: utf-8 -*-

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json

import queue # キュー操作用
from threading import Thread #スレッド処理用

import irrp_wrapper


# Ctl + C で強制終了させる。
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


# グローバル変数
ENV_HOST        = "秘密だよ"
ENV_ROOTCA      = "秘密だよ"
ENV_CERT        = "秘密だよ"
ENV_PRIVATE_KEY = "秘密だよ"
host            = ENV_HOST
rootCAPath      = ENV_ROOTCA
certificatePath = ENV_CERT
privateKeyPath  = ENV_PRIVATE_KEY
port            = 8883


message_q = queue.Queue()
topic = {
    "aws_to_raspi":   "raspi/main/order",
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
        _request_msg = message_q.get()
        print("_request_msg:%s" % (_request_msg))

        #メッセージ解析
        # ToDo:ValueErrorの対策必要
        _msg_id = int(_request_msg)
        
        _devise_id  = int(_msg_id / 100)
        _request_id = int(_msg_id % 100)
        print("_devise_id:%d _request_id:%d" % (_devise_id, _request_id))

        #実行結果の初期値代入
        _response_mesg = {
            "status": 1, #msg_id判別エラー
            "value": 0,
        }

        if _devise_id == 1: #エアコン制御
            if (_request_id >= 1) and (_request_id <= 5):
                irrp_wrapper.request(_request_id)
                _response_mesg["status"] = 0

        #処理結果の送信
        _main_client.publish(topic["aws_from_raspi"], json.dumps(_response_mesg), 1)
        print("Published topic %s: %s\n" % (topic["aws_from_raspi"], _response_mesg))


if __name__ == "__main__":
	#AWSからのメッセージ受信スレッド開始

	t1 = Thread(target=order_thread)
	t1.start()

	main_thread()
