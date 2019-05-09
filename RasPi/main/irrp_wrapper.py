#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess


devise_requests = [
  {
    #devise_id:1
    ##エアコン制御用のリクエスト
    "ON": "python ./../lib/irrp.py -p -g4 -f ./../lib/signal ON",
    "OFF": "python ./../lib/irrp.py -p -g4 -f ./../lib/signal OFF",
    "UP": "sl",
    "DOWN": "sl",
    "STATUS": "sl",
  }
]

def request(devise_id, request_code):
  global request_list
  ret = 1

  _id = devise_id - 1
  if _id <0 or _id >= len(devise_requests):
    print("devise_id判別エラー")
    return 1

  cmd = devise_requests[_id].get(request_code)
  if cmd is None:
    print("サポートされていないリクエスト")
    return 1

  print(cmd)
  subprocess.Popen(cmd.split())
  return 0


if __name__ == "__main__":
  request(int(sys.argv[1]))
