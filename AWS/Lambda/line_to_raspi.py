import os
import json

#トークン取得
import requests

#Lineからの要求かを判定するため
import base64
import hashlib
import hmac

#raspiへの要求処理用
import boto3


CHANNEL_ID = os.environ["CHANNELID"]
CHANNEL_SECRET = os.environ["CHANNELSECRET"]


def line_request_check(event):
  _ret = 0
  checkHeader = event["headers"]["X-Line-Signature"].encode("utf-8")
  hash = hmac.new(CHANNEL_SECRET.encode("utf-8"), event["body"].encode("utf-8"), hashlib.sha256).digest()
  signature = base64.b64encode(hash)

  if signature != checkHeader:
    print("署名認証エラー")
    _ret = -1
  return _ret


_conver_dic = {
  "text":{
    "ON":     "0101", # エアコンON
    "OFF":    "0102", # エアコンOFF
    "UP":     "0103", # 温度アップ
    "DOWN":   "0104", # 温度Down
    "STATUS": "0104", # エアコンの状態を取得
  }
}
def line_request_convert(event):
  body = json.loads(event["body"])

  #テキストが送られてきた場合
  text = body["events"][0]["message"]["text"]

  #text = text.uppper()
  '''
  ↑処理は以下のエラーが出たのでコメントアウト
  ----
  [ERROR] AttributeError: 'str' object has no attribute 'uppper'
  Traceback (most recent call last):
    File "/var/task/lambda_function.py", line 74, in lambda_handler
      raspi_request = line_request_convert(event)
    File "/var/task/lambda_function.py", line 47, in line_request_convert
      text = text.uppper()
  ----

  試したこと
    print(text)
    print(type(text))
  実行結果
    ON
    <class 'str'>
  '''

  _conver_dic["text"][text]
  return _conver_dic["text"].get(text, None)


def send_raspi_request(raspi_request):
  _ret = 0

  topic = "raspi/main/order"
  payload = raspi_request
  try:
    iot = boto3.client("iot-data")
    iot.publish(
      topic = topic,
      qos = 0,
      payload = payload
    )
  except Exception as e:
    print(e)
    _ret = -1
  return _ret


def lambda_handler(event, context):
  print(event)

  if line_request_check(event) < 0:
    return
  
  raspi_request = line_request_convert(event)
  if raspi_request is None:
    return

  ret = send_raspi_request(raspi_request)
  if ret < 0:
    return

  return {
    "statusCode": 200,
    "headers": { "X-Line-Status" : "OK"},
    "body": "{'result':'completed'}"
  }
