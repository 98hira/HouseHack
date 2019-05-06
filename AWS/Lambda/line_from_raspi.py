import os
import json

#トークン取得
import requests

#Lineへメッセージを送信するため
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

CHANNEL_ID     = os.environ["CHANNELID"]
CHANNEL_SECRET = os.environ["CHANNELSECRET"]
USER_ID        = os.environ["USERID"]
def get_token():
  #POSTパラメータは二つ目の引数に辞書で指定する
  response = requests.post(
      "https://api.line.me/v2/oauth/accessToken",
      {"grant_type":"client_credentials",
       "client_id": CHANNEL_ID,
       "client_secret": CHANNEL_SECRET
      }).json()
  _token = response.get("access_token", None)
  if _token is None:
      print("トークン取得エラー")
      print(response["error"])
      print(response["error_description"])
  return _token


_message_list = [
    "成功",
    "msg_id判別エラー",
    "ソフトウェアエラー",
]

def respons_message_conver(event):
  _msg = _message_list[event["status"]]
  _value = ""
  if event["value"] != 0:
    _value = ":" + (event["value"])

  return "%s%s" % (_msg, _value)

def lambda_handler(event, context):
  # トークン取得
  _token = get_token()
  if _token is not None:
    line_bot_api = LineBotApi(_token)    
    _text = respons_message_conver(event)
    try:
      # Lineへ送信する
      line_bot_api.push_message(USER_ID, TextSendMessage(text=_text))
      return {
        "statusCode": 200,
        "headers": { "X-Line-Status" : "OK"},
        "body": "{'result':'completed'}"
      }
    except LineBotApiError as e:
      print(f"送信エラー {e}")
