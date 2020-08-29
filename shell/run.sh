#!/bin/bash

# 请在项目根目录下执行此命令
screen -S community -X quit

sleep 1s

screen -Sdm community
screen -x -S community -p 0 -X stuff "python3 run.py\n"

