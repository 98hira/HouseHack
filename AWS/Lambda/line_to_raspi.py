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

#MQTT通信時のフォーマット関連の変数群
REQUEST_TOPIC = "raspi/main/request"
DEVISE_REQUEST_CODES = {
  1:["ON","OFF","UP","DOWN","STATUS"],
}
request_form = {
  "devise_id": None,
  "request_code": None,
}


def line_request_check(event):
  _ret = 0
  checkHeader = event["headers"]["X-Line-Signature"].encode("utf-8")
  hash = hmac.new(CHANNEL_SECRET.encode("utf-8"), event["body"].encode("utf-8"), hashlib.sha256).digest()
  signature = base64.b64encode(hash)

  if signature != checkHeader:
    print("署名認証エラー")
    _ret = -1
  return _ret



def line_request_convert(event):
  _ret = None
  body = json.loads(event["body"])

  #テキストが送られてきた場合
  _code = body["events"][0]["message"].get("text")
  _id = 1 #現状は１つしかないので固定値を代入
  if _code is not None:
    #text = text.uppper()
    #上記処理はエラーが出たのでコメントアウト
    if _code in DEVISE_REQUEST_CODES[_id]:
      request_form["devise_id"] = _id
      request_form["request_code"] = _code
      _ret = request_form
    else:
      #メッセージ判別エラー
      pass
  else:
    #メッセージ判別エラー
    pass
  return _ret


def send_raspi_request(raspi_request):
  _ret = 0

  try:
    iot = boto3.client("iot-data")
    iot.publish(
      topic = REQUEST_TOPIC,
      qos = 0,
      payload = json.dumps(raspi_request, ensure_ascii=False)
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
