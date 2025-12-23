#!/usr/bin/python
# -*- coding:utf-8 -*-
# @File    : roh_controller.py
# @version : V1
import time
# from pymodbus import FramerType   # pymodbus version >=3.7.2
from frametype import FramerType
from pymodbus.client import ModbusSerialClient
from roh_registers_v1 import *

NUM_FINGERS = 5


class ROHandController:
    def __init__(self, port="COM7", node_id=2):
        """
        初始化手部控制器
        """
        self.port = port
        self.node_id = node_id
        self.client = None

        self.connect()

    def connect(self):
        """
        连接设备
        """
        self.client = ModbusSerialClient(self.port, FramerType.RTU, 115200)
        if not self.client.connect():
            raise ConnectionError(f"无法连接到设备 {self.port}")

        # Set current limit during connection
        self.set_current_limit([200] * NUM_FINGERS)

        # 大拇指旋转到初始位置
        # self._write_registers(ROH_FINGER_POS_TARGET5, [65535])

    def disconnect(self):
        """
        断开设备连接
        """
        if self.client:
            self.client.close()

    def _write_registers(self, address, values):
        """
        内部方法：写入寄存器
        """
        if self.client:
            resp = self.client.write_registers(address, values, self.node_id)
            print('resp:', resp)
            if resp.isError():
                raise RuntimeError(f"写入寄存器失败: {resp}")

    def open_hand(self):
        """
        打开手部
        """
        print("打开手...")
        self._write_registers(ROH_FINGER_POS_TARGET1, [0, 0, 0, 0, 0])  # 打开所有手指
        time.sleep(1.5)

    def close_hand(self):
        """
        关闭手部
        """
        print("关闭手...")
        self._write_registers(ROH_FINGER_POS_TARGET1, [65535, 65535, 65535, 65535])  # 关闭其他手指
        time.sleep(1.5)

    def open_finger_thumb0(self):
        """大拇指"""
        self._write_registers(ROH_FINGER_POS_TARGET2, [0])
        time.sleep(1.5)

    def set_current_limit(self, limits):
        """Set the current limit for the fingers."""
        if len(limits) != NUM_FINGERS:
            raise ValueError(f"Expected {NUM_FINGERS} current limits, got {len(limits)}")
        resp = self.client.write_registers(ROH_FINGER_CURRENT_LIMIT0, limits, self.node_id)
        if resp.isError():
            print("Failed to set current limit:", resp)
        else:
            print("Current limit set successfully")


if __name__ == '__main__':
    roh = ROHandController()
    roh.close_hand()
    time.sleep(3)
    roh.open_hand()
    # roh.open_finger_thumb0()
