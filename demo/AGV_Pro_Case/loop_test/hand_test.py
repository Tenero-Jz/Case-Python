#!/usr/bin/python
# -*- coding:utf-8 -*-
# @File    : hand_test.py
# @Author  : Wang Weijian
# @Time    :  2024/12/26 16:29:40
# @function: the script is used to do something
# @version : V1
import time
from roh_controller import ROHandController

hand_controller = ROHandController('COM7')

# hand_controller.close_hand()
hand_controller.open_hand()