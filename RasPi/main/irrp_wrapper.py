#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

#エアコン制御用のリクエスト
request_list = [
  "dumy",
  "python ./../lib/irrp.py -p -g4 -f ./../lib/signal ON",
  "python ./../lib/irrp.py -p -g4 -f ./../lib/signal OFF",
  "UP",
  "DOWN",
]

def request(id):
  global request_list
  cmd = request_list[id]
  print(cmd)
  subprocess.Popen(cmd.split())

if __name__ == "__main__":
  request(int(sys.argv[1]))
